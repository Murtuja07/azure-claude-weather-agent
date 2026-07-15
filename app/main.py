import logging
import uuid
import os
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.agent import weather_agent
from app.config import get_settings
from app.models.chat import ChatRequest, ChatResponse



connection_string = os.getenv(
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

if connection_string:
    configure_azure_monitor(
        connection_string=connection_string
    )

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format=(
        "%(asctime)s %(levelname)s "
        "%(name)s %(message)s"
    ),
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Azure Claude Weather Agent",
    description=(
        "Weather assistant using Claude and Azure Maps."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id(
    request: Request,
    call_next,
):
    correlation_id = (
        request.headers.get("x-correlation-id")
        or str(uuid.uuid4())
    )

    response = await call_next(request)
    response.headers["x-correlation-id"] = correlation_id

    return response


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "Azure Claude Weather Agent",
        "status": "running",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "environment": settings.app_env,
    }


# @app.post(
#     "/chat",
#     response_model=ChatResponse,
# )
# async def chat(request: ChatRequest) -> ChatResponse:
#     try:
#         answer = await weather_agent.chat(request.message)

#         return ChatResponse(answer=answer)

#     except Exception:
#         logger.exception("Weather agent request failed.")

#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "The weather agent could not process "
#                 "the request."
#             ),
#         )

@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer = await weather_agent.chat(request.message)
        return ChatResponse(answer=answer)

    except Exception as exc:
        logger.exception("Weather agent request failed.")

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {str(exc)}",
        ) from exc