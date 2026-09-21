<div align="center">

# 🚀 NexusCopilot

### 🧠 Enterprise AI Knowledge & Operations Copilot

**Ask questions. Search knowledge. Query databases. Get grounded answers.**

<br/>

<img src="https://img.shields.io/badge/AI-Powered-7C3AED?style=for-the-badge&logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/RAG-Qdrant-FF4F00?style=for-the-badge"/>
<img src="https://img.shields.io/badge/LangGraph-Agentic_AI-1F6FEB?style=for-the-badge"/>
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge&logo=next.js&logoColor=white"/>

<br/>

<img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/Kafka-Event_Streaming-231F20?style=for-the-badge&logo=apachekafka&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/>

<br/><br/>

<a href="https://github.com/thepraveenrajput/nexus-copilot">
<img src="https://img.shields.io/github/stars/thepraveenrajput/nexus-copilot?style=for-the-badge&logo=github"/>
</a>

<a href="https://github.com/thepraveenrajput/nexus-copilot">
<img src="https://img.shields.io/github/forks/thepraveenrajput/nexus-copilot?style=for-the-badge&logo=github"/>
</a>

<a href="https://github.com/thepraveenrajput/nexus-copilot/actions">
<img src="https://img.shields.io/github/actions/workflow/status/thepraveenrajput/nexus-copilot/ci.yml?style=for-the-badge&label=CI"/>
</a>

</div>

---

# 🌟 What is NexusCopilot?

**NexusCopilot** is an enterprise-style AI copilot designed to provide a unified conversational interface over:

- 📚 **Enterprise documents**
- 🗄️ **Structured databases**
- 🔎 **Vector search**
- 🤖 **LLM-powered reasoning**
- ⚡ **Event-driven analytics**

Instead of forcing users to manually search through documents and databases, NexusCopilot allows them to simply ask questions in natural language.

## 💬 Example

```text
👤 How many employees are registered?

🤖 4 employees are currently registered.
```

```text
👤 How many days of annual leave are employees entitled to?

🤖 Employees are entitled to 20 days of annual leave.

   📄 Source: Leave Policy
   📖 Page: 1
```

And even:

```text
👤 How many employees are registered and
   what does the leave policy say about annual leave?

🤖 4 employees are registered.

   According to the leave policy,
   employees are entitled to 20 days of annual leave.
```

The third question demonstrates the **Hybrid SQL + RAG workflow**.

---

# 🧠 Why NexusCopilot?

Enterprise information usually exists in multiple places:

```text
                 🏢 Enterprise
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
     📄 Documents  🗄️ Database  📊 Reports
          │           │           │
          └───────────┼───────────┘
                      ▼
                 🤯 Information
                    Silos
```

NexusCopilot creates a unified AI layer over these sources:

```text
📄 Documents
      │
      ├──────────────┐
      │              │
      ▼              ▼
   🔎 RAG          🗄️ SQL
      │              │
      └──────┬───────┘
             ▼
        🧠 AI Router
             │
             ▼
        💬 Unified Answer
```

---

# 🏗️ System Architecture

```text
                         👤 USER
                            │
                            ▼
                  ┌──────────────────┐
                  │   🖥️ Next.js UI  │
                  │ React + TypeScript│
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │   ⚡ FastAPI      │
                  │    REST API       │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ 🧠 LangGraph     │
                  │ Question Router  │
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌────────────┐
        │ 🔎 RAG   │ │ 🗄️ SQL  │ │ 🔀 Hybrid  │
        │  Agent   │ │  Agent   │ │   Agent    │
        └────┬─────┘ └────┬─────┘ └─────┬──────┘
             │            │             │
             ▼            ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌────────────┐
        │ Qdrant   │ │PostgreSQL│ │ SQL + RAG  │
        └──────────┘ └──────────┘ └──────┬─────┘
                                         │
                                         ▼
                                   🧠 Synthesizer
                                         │
                                         ▼
                                   💬 Final Answer
                                         │
                                         ▼
                                      📚 Sources
```

---

# 🔥 Core Features

<table>
<tr>
<td width="50%">

### 🧠 Agentic Routing

Determines whether a question requires:

- 🔎 RAG
- 🗄️ SQL
- 🔀 Hybrid processing

</td>

<td width="50%">

### 📚 RAG

Retrieves relevant enterprise knowledge using:

- Embeddings
- Qdrant
- Semantic similarity
- Grounded generation

</td>
</tr>

<tr>
<td>

### 🗄️ Natural Language SQL

Ask database questions using normal language.

```text
"How many employees?"
```

→ SQL → PostgreSQL → Answer

</td>

<td>

### 🔐 Enterprise Security

Includes:

- JWT authentication
- RBAC
- User isolation
- Audit logging

</td>
</tr>

<tr>
<td>

### ⚡ Event Architecture

Kafka-based event processing for:

- Chat events
- Analytics
- Asynchronous processing

</td>

<td>

### 📊 Observability

Includes:

- Health checks
- Request IDs
- Centralized logging
- Error handling

</td>
</tr>
</table>

---

# 🔎 Retrieval-Augmented Generation

## 📥 Document Ingestion

```text
             📄 PDF / DOCX
                   │
                   ▼
           📥 Document Upload
                   │
                   ▼
            📖 Text Extraction
                   │
                   ▼
                  ✂️ Chunking
                   │
                   ▼
               🧮 Embeddings
                   │
                   ▼
             🔵 Qdrant Vector DB
```

The embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

produces vector representations used for semantic retrieval.

---

## 🔍 Query Retrieval

```text
             👤 Question
                  │
                  ▼
             🧮 Embedding
                  │
                  ▼
          🔎 Similarity Search
                  │
                  ▼
             📚 Top-K Chunks
                  │
                  ▼
              🧠 LLM Context
                  │
                  ▼
             💬 Grounded Answer
```

Each retrieved source contains metadata such as:

```text
📄 Document ID
📑 Filename
📖 Page Number
🧩 Chunk Index
📊 Similarity Score
📝 Retrieved Text
```

---

# 🔀 Hybrid Intelligence

Some questions require multiple sources.

Example:

```text
"How many employees are registered,
and where do employees submit leave requests?"
```

NexusCopilot can execute both workflows:

```text
                    👤 Question
                         │
                         ▼
                   🧠 LangGraph
                      Router
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
         🗄️ SQL Agent           🔎 RAG Agent
              │                     │
              ▼                     ▼
         PostgreSQL                Qdrant
              │                     │
              └──────────┬──────────┘
                         ▼
                   🧠 Synthesizer
                         │
                         ▼
                      💬 Answer
```

This architecture allows NexusCopilot to combine structured and unstructured enterprise knowledge.

---

# 🗄️ Natural Language → SQL

The SQL workflow follows:

```text
👤 Natural Language
        │
        ▼
🧠 Question Analysis
        │
        ▼
✍️ SQL Generation
        │
        ▼
🛡️ SQL Validation
        │
        ▼
🗄️ PostgreSQL
        │
        ▼
📊 Query Result
        │
        ▼
💬 Natural Language Answer
```

The system validates generated SQL before execution.

---

# 🔐 Authentication & RBAC

Authentication is implemented using JWT.

```text
          👤 User
             │
             ▼
          🔑 Login
             │
             ▼
         🎟️ JWT Token
             │
             ▼
       🔒 Protected API
             │
             ▼
        🛡️ RBAC Check
             │
             ▼
        📦 User Resource
```

### Security Controls

| Security Layer | Implementation |
|---|---|
| 🔑 Authentication | JWT |
| 🔐 Password Security | bcrypt |
| 🛡️ Authorization | RBAC |
| 👤 User Isolation | User-scoped retrieval |
| 📚 Document Isolation | User-scoped Qdrant filtering |
| 💬 Conversation Isolation | User-scoped access |
| 📝 Audit | Audit logs |
| 🚫 Secrets | Environment variables |

---

# ⚡ Kafka Event Architecture

NexusCopilot uses Apache Kafka for event-driven analytics.

```text
                     ⚡ FastAPI
                         │
                         ▼
                  📤 Event Producer
                         │
                         ▼
                  📨 Kafka Topic
                   "chat-events"
                         │
                         ▼
                  📥 Consumer
                         │
                         ▼
                    📊 Analytics
                         │
                         ▼
                    🗄️ PostgreSQL
```

Kafka is separated from the main request/response path so analytics processing can operate independently.

---

# 🏥 Health & Observability

NexusCopilot exposes:

```http
GET /health
```

Example:

```json
{
  "status": "healthy",
  "api": "healthy",
  "postgres": "healthy",
  "qdrant": "healthy",
  "kafka": "healthy"
}
```

## 🔎 Request Tracking

Every request receives:

```text
X-Request-ID
```

Example:

```text
X-Request-ID:
c61b5cb5-c54f-4b95-8fdb-5586d227913f
```

This helps correlate application requests with logs.

---

# 🐳 Infrastructure

Docker Compose manages the local infrastructure:

```text
┌────────────────────────────────────────────┐
│             🐳 Docker Compose              │
│                                            │
│   ┌────────────┐   ┌────────────┐          │
│   │ 🐘 Postgres│   │ 🔵 Qdrant  │          │
│   │   :5432    │   │   :6333    │          │
│   └────────────┘   └────────────┘          │
│                                            │
│          ┌─────────────────────┐           │
│          │ ⚡ Apache Kafka      │           │
│          │       :9092         │           │
│          └─────────────────────┘           │
│                                            │
└────────────────────────────────────────────┘
```

### Start infrastructure

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

### Check infrastructure

```bash
docker compose -f infrastructure/docker-compose.yml ps
```

### Stop infrastructure

```bash
docker compose -f infrastructure/docker-compose.yml stop
```

---

# 🧰 Tech Stack

<div align="center">

### 🎨 Frontend

<img src="https://skillicons.dev/icons?i=nextjs,react,typescript,tailwind"/>

### ⚙️ Backend

<img src="https://skillicons.dev/icons?i=python,fastapi"/>

### 🧠 AI / Data

<img src="https://skillicons.dev/icons?i=postgres,docker,kafka"/>

</div>

| Layer | Technology |
|---|---|
| 🎨 Frontend | Next.js, React, TypeScript, Tailwind CSS |
| ⚡ API | FastAPI |
| 🧠 Orchestration | LangGraph |
| 🤖 LLM | Ollama + Qwen 2.5 1.5B |
| 🧮 Embeddings | Sentence Transformers |
| 🔵 Vector DB | Qdrant |
| 🐘 Database | PostgreSQL |
| ⚡ Streaming | Apache Kafka |
| 🔐 Authentication | JWT + bcrypt |
| 📄 Documents | PyPDF + python-docx |
| 🐳 Containers | Docker + Docker Compose |
| 🔄 CI | GitHub Actions |

---

# 📁 Project Structure

```text
nexus-copilot/
│
├── 📂 .github/
│   └── 📂 workflows/
│       └── ⚙️ ci.yml
│
├── 📂 backend/
│   ├── 📂 app/
│   │   ├── 📂 agents/
│   │   │   ├── 🧠 rag_agent.py
│   │   │   ├── 🗄️ sql_agent.py
│   │   │   └── 🔀 router.py
│   │   ├── 📂 core/
│   │   │   ├── ⚙️ config.py
│   │   │   └── 📝 logging.py
│   │   ├── 📂 db/
│   │   │   ├── 🐘 postgres.py
│   │   │   ├── 🔵 qdrant.py
│   │   │   └── 🧮 embeddings.py
│   │   ├── 📂 events/
│   │   │   └── ⚡ producer.py
│   │   ├── 📂 models/
│   │   ├── 📂 routes/
│   │   ├── 📂 services/
│   │   └── 🚀 main.py
│   └── 🧪 tests/
│       └── test_rag_evaluation.py
│
├── 🐳 backend/Dockerfile
├── 📦 backend/requirements.txt
│
├── 📂 frontend/
│   ├── 📂 src/
│   ├── 📂 public/
│   ├── 📦 package.json
│   └── 📦 package-lock.json
│
├── 📂 infrastructure/
│   └── 🐳 docker-compose.yml
│
├── 📄 .gitignore
└── 📖 README.md
```

---

# 🚀 Getting Started

## 1️⃣ Clone

```bash
git clone https://github.com/thepraveenrajput/nexus-copilot.git

cd nexus-copilot
```

---

## 2️⃣ Start Infrastructure

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

---

## 3️⃣ Setup Backend

```bash
cd backend

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment

> ⚠️ The following values are development examples. Do not commit real secrets.

Create:

```text
backend/.env
```

Example:

```env
POSTGRES_USER=nexus
POSTGRES_PASSWORD=your_password
POSTGRES_DB=nexus_copilot

DATABASE_URL=postgresql+psycopg://nexus:your_password@localhost:5432/nexus_copilot

JWT_SECRET_KEY=your-development-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CHAT_TOPIC=chat-events
KAFKA_ANALYTICS_GROUP=nexus-analytics-consumer

QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=nexus_documents

OLLAMA_MODEL=qwen2.5:1.5b
```

---

## 5️⃣ Start Ollama

```bash
ollama pull qwen2.5:1.5b
```

---

## 6️⃣ Start Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

---

## 7️⃣ Start Frontend

Open another terminal:

```bash
cd frontend

npm ci

npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 🧪 Testing

Run the RAG evaluation:

```bash
cd backend

python -m pytest tests/test_rag_evaluation.py -v -s
```

The evaluation covers:

```text
✅ Annual leave retrieval
✅ Leave request location
✅ Unknown question handling
✅ Source grounding
✅ User document isolation
```

Current evaluation:

```text
4 passed
```

---

# 🔄 CI/CD

NexusCopilot uses GitHub Actions.

```text
                     📦 Git Push
                         │
                         ▼
                   ⚡ GitHub Actions
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        🐍 Backend              ⚛️ Frontend
              │                     │
              ▼                     ▼
       Compile Python             npm ci
                                    │
                                    ▼
                                npm build
```

Workflow:

```text
.github/workflows/ci.yml
```

Triggered by:

```text
🚀 Push → main
🔀 Pull Request → main
```

---

# 📊 Engineering Scope

NexusCopilot demonstrates concepts across multiple engineering layers:

```text
                 🧠 AI ENGINEERING
                        │
            ┌───────────┼───────────┐
            │           │           │
           RAG        Agents       LLMs
            │           │           │
            └───────────┼───────────┘
                        │
                        ▼
               ⚙️ BACKEND ENGINEERING
                        │
            ┌───────────┼───────────┐
            │           │           │
         FastAPI    PostgreSQL     Auth
            │           │           │
            └───────────┼───────────┘
                        │
                        ▼
               ⚡ DISTRIBUTED SYSTEMS
                        │
                   Kafka Events
                        │
                        ▼
                    🐳 DEVOPS
                        │
               Docker + GitHub Actions
```

---

# 🎯 Learning Objectives

The project was designed to understand how modern AI systems are built beyond simply calling an LLM API.

## 🧠 AI / ML

- Embeddings
- Vector search
- Retrieval-Augmented Generation (RAG)
- Semantic retrieval
- LLM integration
- Agent workflows
- LangGraph
- Grounded generation

## ⚙️ Backend

- REST API design
- FastAPI
- PostgreSQL
- SQLAlchemy
- Authentication
- RBAC
- Error handling
- Logging
- Health checks
- Request tracing

## ⚡ Distributed Systems

- Apache Kafka
- Event-driven architecture
- Producers
- Consumers
- Analytics pipelines

## 🐳 DevOps

- Docker
- Docker Compose
- Environment configuration
- Git
- GitHub
- GitHub Actions
- CI pipelines

---

# 📈 Current Status

| Component | Status |
|---|---|
| 🎨 Next.js Frontend | ✅ Complete |
| ⚡ FastAPI Backend | ✅ Complete |
| 📚 Document Ingestion | ✅ Complete |
| 🔎 RAG Pipeline | ✅ Complete |
| 🔵 Qdrant | ✅ Integrated |
| 🗄️ PostgreSQL | ✅ Integrated |
| 🧠 LangGraph Routing | ✅ Implemented |
| 🗄️ SQL Agent | ✅ Implemented |
| 🔀 Hybrid Workflow | ✅ Implemented |
| 🔐 JWT Authentication | ✅ Implemented |
| 🛡️ RBAC | ✅ Implemented |
| 👤 User Isolation | ✅ Implemented |
| 📝 Audit Logging | ✅ Implemented |
| ⚡ Kafka Events | ✅ Implemented |
| 🏥 Health Monitoring | ✅ Implemented |
| 🔎 Request IDs | ✅ Implemented |
| 🐳 Docker Infrastructure | ✅ Implemented |
| 🔄 GitHub Actions | ✅ Passing |

---

# 🚧 Future Roadmap

```text
                 Current
                    │
                    ▼
               🧠 NexusCopilot
                    │
            ┌───────┼───────┐
            │       │       │
            ▼       ▼       ▼
         ☁️ Cloud  📊 Eval  ⚡ Scale
            │       │       │
            ▼       ▼       ▼
         Azure   RAG Eval  Caching
                    │
                    ▼
              Advanced Agents
```

Potential future improvements:

- ☁️ Azure deployment
- 📊 Automated RAG evaluation
- 🧪 LLM evaluation metrics
- ⚡ Redis caching
- 📈 Advanced observability
- 🔐 Production secret management
- 📄 Automated document ingestion
- 🧠 Advanced agent orchestration
- 🚀 Model serving optimization
- 🔒 Fine-grained permissions

---

# 👨‍💻 Author

<div align="center">

## Praveen Singh

**B.Tech Computer Science & Engineering**

<br/>

<a href="https://github.com/thepraveenrajput">
<img src="https://img.shields.io/badge/GitHub-thepraveenrajput-181717?style=for-the-badge&logo=github"/>
</a>

<a href="https://linkedin.com/in/praveen-singh-dev">
<img src="https://img.shields.io/badge/LinkedIn-Praveen_Singh-0A66C2?style=for-the-badge&logo=linkedin"/>
</a>

</div>

---

<div align="center">

### ⭐ If you find this project interesting, consider giving it a star!

<br/>

**Built with ❤️ using modern software engineering practices**

</div>
