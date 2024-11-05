import pytest
from httpx import AsyncClient
from app.main import app
from app.services.queue_service import QueueService
from app.db.database import AsyncSessionLocal, init_db
from app.db.models import Message
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from app.config import get_settings
import asyncio
from sqlalchemy import select

settings = get_settings()

@pytest.fixture(autouse=True)
async def setup_test_app():

    await init_db()
    

    redis_instance = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)
    yield
    await FastAPILimiter.close()

@pytest.mark.asyncio
async def test_webhook_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/webhook", json={
            "message": "test message",
            "callback_url": "https://webhook.site/test"
        })
        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["status"] == "processing"

@pytest.mark.asyncio
async def test_message_processing():
    queue_service = QueueService()
    try:
        await queue_service.connect()
        

        async with AsyncSessionLocal() as session:
            message = Message(
                id="test-id",
                message="test message",
                callback_url="https://webhook.site/test",
                status="processing"
            )
            session.add(message)
            await session.commit()
        
        message_data = {
            "id": "test-id",
            "message": "test message",
            "callback_url": "https://webhook.site/test"
        }
        
        await queue_service.publish_message(message_data)
        

        await asyncio.sleep(2)
        

        async with AsyncSessionLocal() as session:
            stmt = select(Message).where(Message.id == "test-id")
            result = await session.execute(stmt)
            message = result.scalar_one_or_none()
            
            assert message is not None
            assert message.status in ["completed", "error"]
            
    finally:

        if queue_service.connection:
            await queue_service.connection.close()
        

        async with AsyncSessionLocal() as session:
            stmt = select(Message).where(Message.id == "test-id")
            result = await session.execute(stmt)
            message = result.scalar_one_or_none()
            if message:
                await session.delete(message)
                await session.commit()