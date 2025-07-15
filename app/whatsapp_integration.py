from typing import Dict
from fastapi import APIRouter, Request
from dotenv import load_dotenv
import os
import json
import logging
from logging.handlers import RotatingFileHandler
import requests
from requests.auth import HTTPBasicAuth

from app.chatbot_pipeline import ChatbotPipeline

# Load environment variables
load_dotenv()

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'whatsapp.log')
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger("app.whatsapp_integration")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Plivo credentials
AUTH_ID = os.getenv('PLIVO_AUTH_ID')
AUTH_TOKEN = os.getenv('PLIVO_AUTH_TOKEN')
SOURCE_NUMBER = os.getenv('PLIVO_WHATSAPP_NUMBER')  # Example: +15557786898

class WhatsAppIntegration:
    def __init__(self):
        self.chatbot = ChatbotPipeline()
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        @self.router.post("/whatsapp/webhook")
        async def whatsapp_webhook(request: Request):
            content_type = request.headers.get('content-type', '')
            logger.info(f"Received webhook request with content-type: {content_type}")

            # Parse request body
            try:
                if 'application/json' in content_type:
                    body = await request.json()
                    logger.info(f"Received JSON payload: {body}")
                elif 'application/x-www-form-urlencoded' in content_type:
                    form_data = await request.form()
                    body = dict(form_data)
                    logger.info(f"Received form data: {body}")
                else:
                    logger.error(f"Unsupported content type: {content_type}")
                    return {"error": "Unsupported content type"}
            except Exception as e:
                logger.error(f"Failed to parse payload: {str(e)}")
                return {"error": "Invalid request format"}

            # Extract data
            incoming_msg = body.get('Body', '') or body.get('message', '')
            sender = body.get('From', '') or body.get('from', '')

            if not incoming_msg or not sender:
                logger.error("Missing message or sender in payload.")
                return {"error": "Missing required fields"}

            sender = sender.replace('whatsapp:', '')
            logger.info(f"Processing message from {sender}: {incoming_msg}")

            try:
                # Chatbot response
                response = self.chatbot.process_message(
                    message=incoming_msg,
                    session_id=sender,
                    context={"platform": "whatsapp"}
                )

                logger.info(f"Chatbot response: {response}")
                formatted_response = self._format_whatsapp_response(response)
                logger.info(f"Formatted response to {sender}: {formatted_response}")

                # Send back via WhatsApp
                result = await self.send_message(sender, formatted_response)
                logger.info(f"Plivo response: {result}")

                return {
                    "status": result.get("status"),
                    "from": sender,
                    "user_message": incoming_msg,
                    "bot_response": formatted_response,
                    "plivo_response": result
                }

            except Exception as e:
                logger.error(f"Processing error: {str(e)}")
                return {"error": str(e)}

    def _format_whatsapp_response(self, response: Dict) -> str:
        text = response.get('response', '')
        if response.get('suggested_actions'):
            text += "\n\n*Suggested Actions:*"
            for action in response['suggested_actions']:
                text += f"\n• {action}"
        if response.get('next_question'):
            text += f"\n\n{response['next_question']}"
        return text

    async def send_message(self, to: str, message: str) -> Dict:
        try:
            if not SOURCE_NUMBER or not to:
                raise ValueError("Missing source or destination number")

            if not to.startswith('+'):
                to = f'+{to}'

            url = f"https://api.plivo.com/v1/Account/{AUTH_ID}/Message/"
            payload = {
                "src": SOURCE_NUMBER,
                "dst": to,
                "text": message,
                "type": "whatsapp"
            }

            logger.info(f"Sending WhatsApp message to {to}")
            response = requests.post(
                url,
                json=payload,
                auth=HTTPBasicAuth(AUTH_ID, AUTH_TOKEN)
            )

            if response.ok:
                return {"status": "success", "response": response.json()}
            else:
                logger.error(f"Plivo error response: {response.text}")
                return {"status": "error", "response": response.json()}

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {"status": "error", "message": str(e)}
