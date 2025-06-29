from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os
import uvicorn
from pathlib import Path

from app.chatbot_pipeline import ChatbotPipeline
from app.empathy_layer import EmpathyLayer

project_root = Path(__file__).parent.parent

app = FastAPI(
    title="Cloud9 Hospitals Chatbot API",
    description="An empathetic healthcare chatbot for Cloud9 Hospitals",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend port
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

chatbot_pipeline = ChatbotPipeline()
empathy_layer = EmpathyLayer()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    next_question: Optional[str] = None
    session_id: str
    context: Optional[Dict] = None
    suggested_actions: Optional[List[str]] = None

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Process chat messages and return formatted responses"""
    def format_response(text: str, points: List[str] = None) -> str:
        if "appointment" in text.lower():
            text = "🗓 " + text
        elif "emergency" in text.lower():
            text = "🚨 " + text
        elif "doctor" in text.lower() or "medical" in text.lower():
            text = "👨‍⚕️ " + text
        elif "pregnancy" in text.lower() or "baby" in text.lower():
            text = "👶 " + text
        
        if points:
            formatted_points = "\n\n" + "\n".join([f"• {point}" for point in points])
            text += formatted_points
        
        if len(text) > 100:
            text += "\n\n💫 Is there anything else you'd like to know?"
        
        return text
    try:
        if not chat_message.message.strip():
            return ChatResponse(
                response=format_response("I didn't receive any message. Could you please try again?"),
                session_id=chat_message.session_id or "new_session"
            )

        pipeline_response = chatbot_pipeline.process_message(
            chat_message.message,
            chat_message.session_id or "new_session",
            chat_message.context or {}
        )
        
        if not pipeline_response or "response" not in pipeline_response:
            raise HTTPException(status_code=500, detail="Failed to generate response")

        try:
            enhanced_response = empathy_layer.enhance_response(
                pipeline_response["response"],
                pipeline_response["context"]
            )
        except Exception as empathy_error:
            print(f"Error in empathy enhancement: {str(empathy_error)}")
            enhanced_response = pipeline_response["response"]
        
        return ChatResponse(
            response=enhanced_response,
            session_id=pipeline_response["session_id"],
            next_question=pipeline_response.get("next_question"),
            context=pipeline_response["context"],
            suggested_actions=pipeline_response.get("suggested_actions", [])
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Cloud9 Hospitals Chatbot API is running"}

@app.get("/intents")
async def get_intents():
    try:
        intents_path = project_root / "data/processed/intents.json"
        with open(intents_path, "r") as f:
            intents = json.load(f)
        return intents
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to load intents")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
