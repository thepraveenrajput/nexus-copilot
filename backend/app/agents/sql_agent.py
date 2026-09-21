from app.core.config import DATABASE_URL
from typing import TypedDict
import re

from sqlalchemy import create_engine, text
from langgraph.graph import StateGraph, END
from ollama import chat


# DATABASE

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# STATE

class SQLState(TypedDict):
    question: str
    sql: str
    answer: str


# DATABASE SCHEMA

SCHEMA = """
users(
    id INTEGER,
    email VARCHAR,
    full_name VARCHAR,
    role VARCHAR,
    is_active BOOLEAN,
    created_at TIMESTAMP
)

documents(
    id INTEGER,
    filename VARCHAR,
    file_type VARCHAR,
    uploaded_by INTEGER,
    status VARCHAR,
    qdrant_collection VARCHAR,
    created_at TIMESTAMP
)

conversations(
    id INTEGER,
    user_id INTEGER,
    title VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

messages(
    id INTEGER,
    conversation_id INTEGER,
    role VARCHAR,
    content TEXT,
    created_at TIMESTAMP
)
"""


# DETERMINISTIC SQL

def deterministic_sql(question: str):

    q = question.lower().strip()

    # ACTIVE USERS

    if (
        "how many active users" in q
        or "number of active users" in q
        or "count of active users" in q
        or q in {
            "active users",
            "active users?",
        }
    ):
        return (
            "SELECT COUNT(*) "
            "FROM users "
            "WHERE is_active = TRUE"
        )

    # INACTIVE USERS

    if (
        "how many inactive users" in q
        or "number of inactive users" in q
        or "count of inactive users" in q
        or q in {
            "inactive users",
            "inactive users?",
        }
    ):
        return (
            "SELECT COUNT(*) "
            "FROM users "
            "WHERE is_active = FALSE"
        )

    # TOTAL USERS

    if (
        "how many users" in q
        or "number of users" in q
        or "count of users" in q
        or "how many registered users" in q
        or "number of registered users" in q
        or "count of registered users" in q
        or q in {
            "users",
            "users?",
            "registered users",
            "registered users?",
        }
    ):
        return (
            "SELECT COUNT(*) "
            "FROM users"
        )

    # DOCUMENTS

    if (
        "how many documents" in q
        or "number of documents" in q
        or "count of documents" in q
        or q in {
            "documents",
            "documents?",
        }
    ):
        return (
            "SELECT COUNT(*) "
            "FROM documents"
        )

    # CONVERSATIONS

    if (
        "how many conversations" in q
        or "number of conversations" in q
        or "count of conversations" in q
        or q in {
            "conversations",
            "conversations?",
        }
    ):
        return (
            "SELECT COUNT(*) "
            "FROM conversations"
        )

    return None


# LLM SQL GENERATION

def generate_sql(state: SQLState):

    question = state["question"]

    # FIRST: DETERMINISTIC RULES

    deterministic = deterministic_sql(question)

    if deterministic:
        return {
            "sql": deterministic
        }

    # LLM FALLBACK

    prompt = f"""
You are a PostgreSQL SQL generator for an enterprise AI assistant.

Database schema:

{SCHEMA}

Convert the user's question into ONE read-only SQL query.

Rules:

1. ONLY SELECT queries are allowed.

2. Never generate:
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
GRANT
REVOKE
MERGE
CALL

3. Use only the tables and columns in the schema.

4. Generate exactly ONE SQL statement.

5. Do not use SQL comments.

6. Do not use markdown.

7. Return ONLY the SQL query.

User question:
{question}
"""

    response = chat(
        model="qwen2.5:1.5b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    sql = response["message"]["content"].strip()

    # REMOVE MARKDOWN

    sql = re.sub(
        r"```(?:sql|postgresql)?",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = sql.replace("```", "").strip()

    return {
        "sql": sql
    }


# SQL VALIDATION

def validate_sql(sql: str) -> bool:

    if not sql:
        return False

    sql = sql.strip()

    # REMOVE ONE TRAILING SEMICOLON

    if sql.endswith(";"):
        sql = sql[:-1].strip()

    if not sql:
        return False

    # ONLY SELECT

    if not re.match(
        r"^select\b",
        sql,
        flags=re.IGNORECASE,
    ):
        return False

    # NO MULTIPLE STATEMENTS

    if ";" in sql:
        return False

    # NO COMMENTS

    if "--" in sql:
        return False

    if "/*" in sql:
        return False

    if "*/" in sql:
        return False

    # BLOCK DANGEROUS SQL KEYWORDS

    forbidden_pattern = re.compile(
        r"\b("
        r"insert|"
        r"update|"
        r"delete|"
        r"drop|"
        r"alter|"
        r"create|"
        r"truncate|"
        r"grant|"
        r"revoke|"
        r"merge|"
        r"call"
        r")\b",
        re.IGNORECASE,
    )

    if forbidden_pattern.search(sql):
        return False

    # ONLY ALLOW KNOWN TABLES

    allowed_tables = {
        "users",
        "documents",
        "conversations",
        "messages",
    }

    table_pattern = re.compile(
        r"\b(?:from|join)\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*)",
        re.IGNORECASE,
    )

    tables = table_pattern.findall(sql)

    for table in tables:

        if table.lower() not in allowed_tables:
            return False

    return True


# SQL EXECUTION

def execute_sql(state: SQLState):

    sql = state["sql"]

    print(f"[SQL Agent] Generated SQL: {sql}")

    if not validate_sql(sql):

        print("[SQL Agent] SQL validation FAILED")

        return {
            "answer": "Unsafe SQL query rejected."
        }

    print("[SQL Agent] SQL validation PASSED")

    # Remove optional trailing semicolon.
    sql = sql.rstrip(";").strip()

    try:

        with engine.connect() as connection:

            # Make this transaction read-only.
            connection.execute(
                text(
                    "SET TRANSACTION READ ONLY"
                )
            )

            result = connection.execute(
                text(sql)
            )

            rows = result.fetchall()

        # NO RESULTS

        if not rows:

            return {
                "answer": "No results found."
            }

        # SINGLE VALUE

        if (
            len(rows) == 1
            and len(rows[0]) == 1
        ):

            value = rows[0][0]

            return {
                "answer": f"The result is {value}."
            }

        # MULTIPLE RESULTS

        formatted_rows = [
            tuple(row)
            for row in rows
        ]

        return {
            "answer": str(formatted_rows)
        }

    except Exception as e:

        print(
            f"[SQL Agent] Database execution error: {e}"
        )

        return {
            "answer": (
                "I couldn't execute the database query."
            )
        }


# LANGGRAPH

graph = StateGraph(SQLState)


graph.add_node(
    "generate_sql",
    generate_sql,
)

graph.add_node(
    "execute_sql",
    execute_sql,
)


graph.set_entry_point(
    "generate_sql"
)


graph.add_edge(
    "generate_sql",
    "execute_sql",
)


graph.add_edge(
    "execute_sql",
    END,
)


sql_agent = graph.compile()