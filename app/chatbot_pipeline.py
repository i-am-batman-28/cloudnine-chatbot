from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
from modules.vector_store import VectorStoreManager
from modules.intent_classifier import IntentClassifier
from modules.entity_extractor import EntityExtractor
from modules.memory import ConversationMemory
from modules.rag_response import RAGResponseGenerator

@dataclass
class PipelineStep:
    question: str
    required_entities: List[str]
    validation_func: Optional[Callable] = None
    context_key: str = ""

class ChatbotPipeline:
    def __init__(self):
        self.conversation_memory = ConversationMemory()
        self.pipeline_steps = self._initialize_pipeline()
        self.vector_store = VectorStoreManager()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.rag_generator = RAGResponseGenerator()

    def _initialize_pipeline(self) -> List[PipelineStep]:
        return [
            PipelineStep(
                question="👋 Hi! How can I assist you with your healthcare needs today?",
                required_entities=["intent_confirmation"],
                context_key="greeting"
            ),
            PipelineStep(
                question="Could you share if you're experiencing any specific symptoms? 🏥",
                required_entities=["symptoms"],
                context_key="symptoms"
            ),
            PipelineStep(
                question="Have you visited Cloud9 Hospitals before? 🏨",
                required_entities=["previous_visit"],
                context_key="patient_history"
            ),
            PipelineStep(
                question="Would you prefer to schedule an appointment with a specific doctor or department? 👨‍⚕️",
                required_entities=["doctor", "department"],
                context_key="appointment_preference"
            )
        ]

    def process_message(self, message: str, session_id: str, context: Optional[Dict] = None) -> Dict:
        """Process user message and return appropriate response with next question"""

        session = self.conversation_memory.get_or_create_session(session_id)
        
        if "is_first_interaction" not in session:
            session["is_first_interaction"] = True
            session["current_step"] = 0

        intent, _ = self.intent_classifier.classify_intent(message)
        entities = self.entity_extractor.extract_entities(message)
        
        if session.get("is_first_interaction", True):
            session["is_first_interaction"] = False

        session['current_context'] = {
            'intent': intent,
            'entities': entities,
            'user_message': message
        }

        try:
            vector_results = self.vector_store.query_vector_store(
                query=message,
                k=3,
                filters={"priority": "high"} if intent in ["medical_inquiry", "emergency"] else None
            )
        except Exception as e:
            print(f"Error querying vector store: {e}")
            vector_results = []

        try:
            conversation_history = self.conversation_memory.get_conversation_history(session_id)
            rag_response = self.rag_generator.generate_response(
                query=message,
                context=session,
                conversation_history=conversation_history[:3]
            )
            if not rag_response:
                rag_response = "❓ I'm having trouble understanding. Could you please rephrase that?"

            if intent == "appointment_booking" and "appointment_time" in entities:
                rag_response = f"📅 Perfect! I've noted your preferred appointment time. {rag_response}"

        except Exception as e:
            print(f"Error in RAG response generation: {str(e)}")
            rag_response = "⚠️ I'm experiencing technical difficulties. Please try again in a moment."

        self.conversation_memory.update_session(
            session_id,
            message,
            rag_response,
            entities,
            intent
        )

        try:
            next_question = self._get_next_question(session, intent, entities)
        except Exception as e:
            print(f"Error getting next question: {e}")
            next_question = None

        try:
            suggested_actions = self._get_suggested_actions(intent, entities)
        except Exception as e:
            print(f"Error getting suggested actions: {e}")
            suggested_actions = []

        return {
            "response": rag_response,
            "next_question": next_question,
            "session_id": session_id,
            "context": session,
            "suggested_actions": suggested_actions
        }

    def _get_next_question(self, session: Dict, intent: str, entities: Dict) -> Optional[str]:
        """Determine the next question based on conversation state"""
        try:
            if intent in ["goodbye", "thanks"]:
                return None
                
            if session.get("is_first_interaction", True):
                session["is_first_interaction"] = False
                return self.pipeline_steps[0].question

            if intent in ["medical_inquiry", "emergency", "symptom_inquiry"] and not session.get("asked_symptoms", False):
                session["asked_symptoms"] = True
                return "Could you share if you're experiencing any specific symptoms? 🏥"

            if intent == "appointment_booking" and not session.get("asked_appointment", False):
                session["asked_appointment"] = True
                return "Would you prefer to schedule an appointment with a specific doctor or department? 👨‍⚕️"

            return None
        except Exception as e:
            print(f"Error in _get_next_question: {str(e)}")
            return None

    def _get_suggested_actions(self, intent: str, entities: Dict) -> List[str]:
        """Generate suggested actions based on intent and entities"""
        suggestions = []
        try:
            if intent == "appointment_booking":
                if "appointment_time" not in entities:
                    suggestions.extend([
                        "📅 Select a date",
                        "⏰ Choose time slot",
                        "👨‍⚕️ View available doctors"
                    ])
                else:
                    suggestions.extend([
                        "✅ Confirm appointment",
                        "📍 Get directions",
                        "📝 Add to calendar"
                    ])
            elif intent == "symptom_inquiry":
                suggestions.extend([
                    "Find relevant department",
                    "Book urgent consultation",
                    "View medical guidelines"
                ])
            elif intent == "medical_records":
                suggestions.extend([
                    "Download reports",
                    "View prescription history",
                    "Schedule follow-up"
                ])
            if not suggestions:
                suggestions.extend([
                    "Book an appointment",
                    "View our services",
                    "Contact support"
                ])
        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
            return []
        return suggestions[:3]

    def reset_session(self, session_id: str):
        """Reset the conversation state for a session"""
        self.conversation_memory.clear_session(session_id)
