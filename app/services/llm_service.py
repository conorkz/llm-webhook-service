import httpx
import json
from typing import Dict
import asyncio
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        
    async def generate_response(self, message: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "LLM Webhook Service"
                }
                
                payload = {
                    "model": "liquid/lfm-40b:free",
                    "messages": [{"role": "user", "content": message}]
                }
                
                logger.info(f"Sending request to OpenRouter with headers: {headers}")
                logger.info(f"Request payload: {payload}")
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response body: {response.text}")
                
                if response.status_code != 200:
                    error_message = f"OpenRouter API error: {response.text}"
                    logger.error(error_message)
                    raise Exception(error_message)
                    
                result = response.json()
                return result['choices'][0]['message']['content']
                
            except Exception as e:
                logger.error(f"Error in generate_response: {str(e)}")
                raise Exception(f"Failed to generate response from LLM: {str(e)}")