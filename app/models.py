from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class WebhookRequest(BaseModel):
    message: str
    callback_url: HttpUrl

class WebhookResponse(BaseModel):
    request_id: str
    status: str
    message: str
    created_at: datetime

class MessageHistory(BaseModel):
    id: str
    message: str
    response: str
    callback_url: HttpUrl
    created_at: datetime
    status: str 