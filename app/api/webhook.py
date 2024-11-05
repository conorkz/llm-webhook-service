from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from ..models import WebhookRequest, WebhookResponse
from ..services.llm_service import LLMService
from ..config import get_settings
from ..db.models import Message
from ..db.database import AsyncSessionLocal
import httpx
import uuid
from datetime import datetime
import asyncio
from fastapi_limiter.depends import RateLimiter

router = APIRouter()
settings = get_settings()

@router.post("/webhook", 
    response_model=WebhookResponse,
    dependencies=[Depends(RateLimiter(times=settings.RATE_LIMIT_REQUESTS, 
                                    seconds=settings.RATE_LIMIT_PERIOD))])
async def webhook(
    request: WebhookRequest,
    background_tasks: BackgroundTasks,
    llm_service: LLMService = Depends(LLMService)
):
    request_id = str(uuid.uuid4())
    

    async with AsyncSessionLocal() as session:
        message = Message(
            id=request_id,
            message=request.message,
            callback_url=str(request.callback_url),
            status="processing",
            created_at=datetime.utcnow()
        )
        session.add(message)
        await session.commit()
    

    background_tasks.add_task(
        process_webhook_request,
        request_id,
        request.message,
        request.callback_url,
        llm_service
    )
    
    return WebhookResponse(
        request_id=request_id,
        status="processing",
        message="Request accepted for processing",
        created_at=datetime.utcnow()
    )

async def process_webhook_request(
    request_id: str,
    message: str,
    callback_url: str,
    llm_service: LLMService
):
    async with AsyncSessionLocal() as session:
        try:
            db_message = await session.get(Message, request_id)
            if not db_message:
                return


            response = await llm_service.generate_response(message)
            

            db_message.response = response
            db_message.status = "completed"
            db_message.processed_at = datetime.utcnow()
            await session.commit()
            

            async with httpx.AsyncClient() as client:
                await client.post(
                    str(callback_url),
                    json={
                        "request_id": request_id,
                        "status": "completed",
                        "response": response,
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
                
        except Exception as e:

            if db_message:
                db_message.status = "error"
                db_message.error = str(e)
                await session.commit()
            

            async with httpx.AsyncClient() as client:
                await client.post(
                    str(callback_url),
                    json={
                        "request_id": request_id,
                        "status": "error",
                        "error": str(e),
                        "created_at": datetime.utcnow().isoformat()
                    }
                ) 