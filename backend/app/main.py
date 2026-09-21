import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.postgres import check_postgres
from app.db.qdrant import check_qdrant

from app.routes.documents import router as documents_router
from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router
from app.routes.auth import router as auth_router
from app.routes import admin

from app.events.producer import event_producer
from app.core.logging import setup_logging


setup_logging()


app = FastAPI(
    title="NexusCopilot API",
    description="Enterprise AI Knowledge & Operations Copilot",
    version="1.0.0",
)


@app.middleware("http")
async def request_id_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID"
    )

    if not request_id:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    try:
        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:
        raise


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        str(uuid.uuid4()),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong while processing your request.",
            "request_id": request_id,
        },
        headers={
            "X-Request-ID": request_id,
        },
    )


# Connect Kafka producer when API starts
event_producer.connect()


app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(auth_router)
app.include_router(admin.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "NexusCopilot API is running"
    }


@app.get("/health")
def health():
    postgres_status = "healthy"
    qdrant_status = "healthy"
    kafka_status = "healthy"

    try:
        check_postgres()
    except Exception:
        postgres_status = "unhealthy"

    try:
        check_qdrant()
    except Exception:
        qdrant_status = "unhealthy"

    if not event_producer.enabled:
        kafka_status = "unhealthy"

    overall_status = (
        "healthy"
        if (
            postgres_status == "healthy"
            and qdrant_status == "healthy"
            and kafka_status == "healthy"
        )
        else "degraded"
    )

    return {
        "status": overall_status,
        "api": "healthy",
        "postgres": postgres_status,
        "qdrant": qdrant_status,
        "kafka": kafka_status,
    }