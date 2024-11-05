from .llm_service import LLMService
from .queue_service import QueueService
from ..db.database import AsyncSessionLocal
from ..db.models import Message
from sqlalchemy import select
from datetime import datetime
import logging
import httpx

logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self):
        self.llm_service = LLMService()
        self.queue_service = QueueService()

    async def process_message(self, message_data: dict):
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(Message).where(Message.id == message_data["id"])
                result = await session.execute(stmt)
                message = result.scalar_one_or_none()
                
                if not message:
                    logger.error(f"Message {message_data['id']} not found in database")
                    return

                response = await self.llm_service.generate_response(message.message)
                

                message.response = response
                message.status = "completed"
                message.processed_at = datetime.utcnow()
                await session.commit()
                
                async with httpx.AsyncClient() as client:
                    await client.post(
                        str(message.callback_url),
                        json={
                            "request_id": message.id,
                            "status": "completed",
                            "response": response,
                            "created_at": datetime.utcnow().isoformat()
                        }
                    )
                    
            except Exception as e:
                logger.error(f"Error processing message {message_data['id']}: {e}")
                if message:
                    message.status = "error"
                    message.error = str(e)
                    await session.commit()
                

                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            str(message_data["callback_url"]),
                            json={
                                "request_id": message_data["id"],
                                "status": "error",
                                "error": str(e),
                                "created_at": datetime.utcnow().isoformat()
                            }
                        )
                except Exception as callback_error:
                    logger.error(f"Error sending callback for {message_data['id']}: {callback_error}") 