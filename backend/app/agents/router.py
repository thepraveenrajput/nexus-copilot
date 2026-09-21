from typing import TypedDict

from langgraph.graph import StateGraph, END
from ollama import chat

from app.agents.rag_agent import rag_agent
from app.agents.sql_agent import sql_agent


print("NEXUS ROUTER LOADED - HYBRID VERSION")


# Router state

class RouterState(TypedDict):
    question: str
    history: str
    user_id: int

    route: str
    agent: str
    answer: str
    sources: list

    sql_answer: str
    rag_answer: str

    sql_question: str
    rag_question: str


# Question resolver

def resolve_question(state: RouterState):

    question = state["question"].strip()
    history = state["history"].strip()

    question_lower = question.lower()

    if not history:
        return {
            "question": question
        }

    if (
        "where do i submit" in question_lower
        or "where should i submit" in question_lower
        or "where can i submit" in question_lower
    ):

        history_lower = history.lower()

        if (
            "leave" in history_lower
            and (
                "annual leave" in history_lower
                or "leave request" in history_lower
                or "leave requests" in history_lower
            )
        ):
            return {
                "question": (
                    "Where do employees submit leave requests?"
                )
            }

    if (
        "what about active users" in question_lower
        or "what about active user" in question_lower
        or question_lower == "active users?"
        or question_lower == "active users"
    ):
        return {
            "question": "How many active users are there?"
        }

    if (
        "what about inactive users" in question_lower
        or "what about inactive user" in question_lower
        or question_lower == "inactive users?"
        or question_lower == "inactive users"
    ):
        return {
            "question": "How many inactive users are there?"
        }

    if (
        "how many days is it" in question_lower
        or "how many days is that" in question_lower
    ):

        history_lower = history.lower()

        if "annual leave" in history_lower:
            return {
                "question": (
                    "How many days of annual leave "
                    "are employees entitled to?"
                )
            }

    return {
        "question": question
    }


# Question classifier

def classify_question(state: RouterState):

    question = state["question"].strip()
    question_lower = question.lower()

    print(f"CLASSIFY QUESTION: {question}")

    rag_signals = [
        "policy",
        "policies",
        "sop",
        "procedure",
        "procedures",
        "rule",
        "rules",
        "annual leave",
        "maternity leave",
        "leave policy",
        "leave request",
        "leave requests",
        "how do employees",
        "where do employees",
        "what are employees entitled",
        "document",
        "documents",
        "company policy",
        "company policies",
        "internal knowledge",
    ]

    sql_signals = [
        "how many users",
        "how many active users",
        "how many inactive users",
        "number of users",
        "number of active users",
        "number of inactive users",
        "count users",
        "count of users",
        "registered users",
        "active users",
        "inactive users",

        "how many employees",
        "how many active employees",
        "how many inactive employees",
        "number of employees",
        "number of active employees",
        "number of inactive employees",
        "count employees",
        "count of employees",
        "registered employees",
        "active employees",
        "inactive employees",

        "how many documents",
        "number of documents",
        "count documents",
        "count of documents",

        "how many conversations",
        "number of conversations",
        "count conversations",
        "count of conversations",

        "database",
        "database records",
        "database data",
        "records",
        "statistics",
    ]

    has_rag_signal = any(
        signal in question_lower
        for signal in rag_signals
    )

    has_sql_signal = any(
        signal in question_lower
        for signal in sql_signals
    )

    print(f"RAG SIGNAL: {has_rag_signal}")
    print(f"SQL SIGNAL: {has_sql_signal}")

    if has_rag_signal and has_sql_signal:

        print("ROUTE = HYBRID")

        return {
            "route": "hybrid"
        }

    if has_rag_signal:

        print("ROUTE = RAG")

        return {
            "route": "rag"
        }

    if has_sql_signal:

        print("ROUTE = SQL")

        return {
            "route": "sql"
        }

    history = state["history"]

    print(
        "NO DETERMINISTIC SIGNAL - USING LLM FALLBACK"
    )

    prompt = f"""
You are an intent classifier for an enterprise AI assistant.

Classify the question into exactly ONE category.

RAG:
Questions about:
- company policies
- documents
- SOPs
- rules
- procedures
- leave policies
- internal knowledge

SQL:
Questions about:
- database data
- users
- employees
- records
- counts
- statistics
- stored documents
- conversations

HYBRID:
Questions requiring BOTH:
- database information
AND
- company document or policy information

Conversation history:
{history}

Current question:
{question}

Return ONLY one word:

RAG
SQL
HYBRID
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

    classification = (
        response["message"]["content"]
        .strip()
        .upper()
    )

    print(
        f"LLM CLASSIFICATION: {classification}"
    )

    if classification == "HYBRID":

        print("ROUTE = HYBRID")

        return {
            "route": "hybrid"
        }

    if classification == "SQL":

        print("ROUTE = SQL")

        return {
            "route": "sql"
        }

    print("ROUTE = RAG")

    return {
        "route": "rag"
    }


# SQL agent

def run_sql_agent(state: RouterState):

    print("EXECUTING SQL AGENT")

    result = sql_agent.invoke(
        {
            "question": state["question"],
            "sql": "",
            "answer": "",
        }
    )

    return {
        "agent": "SQL Agent",
        "sql_answer": result["answer"],
        "answer": result["answer"],
        "sources": [],
    }


# RAG agent

def run_rag_agent(state: RouterState):

    print("EXECUTING RAG AGENT")

    result = rag_agent.invoke(
        {
            "question": state["question"],
            "user_id": state["user_id"],
            "context": "",
            "answer": "",
            "sources": [],
        }
    )

    return {
        "agent": "RAG Agent",
        "rag_answer": result["answer"],
        "answer": result["answer"],
        "sources": result["sources"],
    }


# Hybrid planner

def plan_hybrid_question(state: RouterState):

    question = state["question"]
    history = state["history"]

    question_lower = question.lower()

    sql_keywords = [
        "user",
        "users",
        "employee",
        "employees",
        "registered",
        "database",
        "record",
        "records",
        "count",
        "how many",
        "number of",
        "statistics",
        "conversation",
        "conversations",
    ]

    rag_keywords = [
        "policy",
        "policies",
        "sop",
        "procedure",
        "procedures",
        "rule",
        "rules",
        "document",
        "documents",
        "leave",
        "maternity",
        "annual leave",
        "company policy",
        "internal knowledge",
    ]

    if " and " in question_lower:

        parts = question.split(" and ", 1)

        first_part = parts[0].strip()
        second_part = parts[1].strip()

        first_lower = first_part.lower()
        second_lower = second_part.lower()

        first_is_sql = any(
            keyword in first_lower
            for keyword in sql_keywords
        )

        second_is_sql = any(
            keyword in second_lower
            for keyword in sql_keywords
        )

        first_is_rag = any(
            keyword in first_lower
            for keyword in rag_keywords
        )

        second_is_rag = any(
            keyword in second_lower
            for keyword in rag_keywords
        )

        print(f"FIRST PART SQL: {first_is_sql}")
        print(f"FIRST PART RAG: {first_is_rag}")
        print(f"SECOND PART SQL: {second_is_sql}")
        print(f"SECOND PART RAG: {second_is_rag}")

        # RAG + SQL

        if first_is_rag and second_is_sql:

            print("HYBRID SPLIT = RAG + SQL")

            return {
                "sql_question": second_part,
                "rag_question": first_part,
            }

        # SQL + RAG

        if first_is_sql and second_is_rag:

            print("HYBRID SPLIT = SQL + RAG")

            return {
                "sql_question": first_part,
                "rag_question": second_part,
            }

        # If the first part contains clear policy/leave
        # language, treat it as RAG even if it also contains
        # words such as "how many" or "employees".

        if first_is_rag and not second_is_rag:

            if second_is_sql:

                print("HYBRID SPLIT = RAG + SQL")

                return {
                    "sql_question": second_part,
                    "rag_question": first_part,
                }

        if second_is_rag and not first_is_rag:

            if first_is_sql:

                print("HYBRID SPLIT = SQL + RAG")

                return {
                    "sql_question": first_part,
                    "rag_question": second_part,
                }

    prompt = f"""
You are a question planner for an enterprise AI assistant.

The user asked a hybrid question requiring both database
information and document/policy information.

Split the question into EXACTLY two standalone questions.

SQL_QUESTION:
Only the part requiring database information.

RAG_QUESTION:
Only the part requiring information from company documents,
policies, SOPs, rules, procedures, or internal knowledge.

IMPORTANT:

1. Do not add information.
2. Do not invent questions.
3. Preserve the original wording and intent.
4. SQL question must contain ONLY the database part.
5. RAG question must contain ONLY the document/policy part.
6. If a question contains both "how many" and policy/leave
   language, classify that part as RAG when its subject is
   the policy or document.
7. Return ONLY these two lines.

Example:

Input:
How many employees are registered and what does the leave
policy say about annual leave?

Output:
SQL_QUESTION: How many employees are registered?
RAG_QUESTION: What does the leave policy say about annual leave?

Example:

Input:
According to the leave policy, how many annual leave days
are employees entitled to, and how many employees are registered?

Output:
SQL_QUESTION: How many employees are registered?
RAG_QUESTION: According to the leave policy, how many annual leave days are employees entitled to?

Conversation history:
{history}

Current question:
{question}

SQL_QUESTION:
RAG_QUESTION:
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

    output = (
        response["message"]["content"]
        .strip()
    )

    sql_question = ""
    rag_question = ""

    for line in output.splitlines():

        line = line.strip()

        if line.upper().startswith(
            "SQL_QUESTION:"
        ):

            sql_question = line.split(
                ":",
                1
            )[1].strip()

        elif line.upper().startswith(
            "RAG_QUESTION:"
        ):

            rag_question = line.split(
                ":",
                1
            )[1].strip()

    sql_question = (
        sql_question
        .strip('"')
        .strip("'")
        .strip()
    )

    rag_question = (
        rag_question
        .strip('"')
        .strip("'")
        .strip()
    )

    return {
        "sql_question": sql_question,
        "rag_question": rag_question,
    }


# Hybrid synthesizer
# Hybrid synthesizer
def synthesize_hybrid_answer(
    question: str,
    sql_answer: str,
    rag_answer: str,
):
    prompt = f"""
You are the final answer synthesizer for an enterprise AI assistant.

User question:
{question}

SQL result:
{sql_answer}

RAG result:
{rag_answer}

Rules:
1. Answer the complete user question.
2. Use BOTH SQL and RAG results.
3. Never omit a relevant result.
4. If SQL contains a number, explicitly include it.
5. If RAG contains policy or document information, explicitly include it.
6. Do not invent information.
7. Keep the answer concise and natural.
8. Return only the final answer.

The answer must combine all relevant information from both results.
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

    final_answer = response["message"]["content"].strip()

    print("HYBRID FINAL ANSWER:", final_answer)

    return final_answer

# Hybrid synthesizer


def run_hybrid_agents(state: RouterState):

    print("EXECUTING HYBRID AGENT")

    plan = plan_hybrid_question(state)

    sql_question = plan["sql_question"]
    rag_question = plan["rag_question"]

    print(
        f"HYBRID SQL QUESTION: {sql_question}"
    )

    print(
        f"HYBRID RAG QUESTION: {rag_question}"
    )

    if not sql_question or not rag_question:

        return {
            "agent": "Hybrid Agent",
            "sql_question": sql_question,
            "rag_question": rag_question,
            "sql_answer": "",
            "rag_answer": "",
            "answer": (
                "I couldn't safely split the question "
                "into its database and knowledge parts."
            ),
            "sources": [],
        }

    print("HYBRID -> SQL AGENT")

    sql_result = sql_agent.invoke(
        {
            "question": sql_question,
            "sql": "",
            "answer": "",
        }
    )

    print("HYBRID -> RAG AGENT")

    rag_result = rag_agent.invoke(
        {
            "question": rag_question,
            "user_id": state["user_id"],
            "context": "",
            "answer": "",
            "sources": [],
        }
    )

    sql_answer = sql_result["answer"]
    rag_answer = rag_result["answer"]

    print(
        f"HYBRID SQL RESULT: {sql_answer}"
    )

    print(
        f"HYBRID RAG RESULT: {rag_answer}"
    )

    print("HYBRID -> SYNTHESIZING")

    combined_answer = synthesize_hybrid_answer(
        question=state["question"],
        sql_answer=sql_answer,
        rag_answer=rag_answer,
    )

    print(
        f"HYBRID FINAL ANSWER: {combined_answer}"
    )

    return {
        "agent": "SQL Agent + RAG Agent",
        "sql_question": sql_question,
        "rag_question": rag_question,
        "sql_answer": sql_answer,
        "rag_answer": rag_answer,
        "answer": combined_answer,
        "sources": rag_result["sources"],
    }


# LangGraph

def route_question(state: RouterState):

    if state["route"] == "sql":
        return "sql"

    if state["route"] == "hybrid":
        return "hybrid"

    return "rag"


graph = StateGraph(RouterState)

graph.add_node(
    "resolve",
    resolve_question,
)

graph.add_node(
    "classify",
    classify_question,
)

graph.add_node(
    "sql",
    run_sql_agent,
)

graph.add_node(
    "rag",
    run_rag_agent,
)

graph.add_node(
    "hybrid",
    run_hybrid_agents,
)

graph.set_entry_point(
    "resolve"
)

graph.add_edge(
    "resolve",
    "classify",
)

graph.add_conditional_edges(
    "classify",
    route_question,
    {
        "sql": "sql",
        "rag": "rag",
        "hybrid": "hybrid",
    },
)

graph.add_edge(
    "sql",
    END,
)

graph.add_edge(
    "rag",
    END,
)

graph.add_edge(
    "hybrid",
    END,
)

router_agent = graph.compile()