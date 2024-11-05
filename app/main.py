from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from .api import webhook
from .config import get_settings
from .db.database import init_db
from .monitoring import init_monitoring
from .services.message_processor import MessageProcessor
from .services.queue_service import QueueService
import logging
import asyncio

settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="A webhook service for processing LLM requests",
    version="1.0.0"
)


init_monitoring(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    redis_instance = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)
    

    await init_db()
    

    processor = MessageProcessor()
    queue_service = QueueService()
    

    asyncio.create_task(queue_service.process_messages(processor.process_message))

app.include_router(webhook.router, prefix="/api/v1", tags=["webhook"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 