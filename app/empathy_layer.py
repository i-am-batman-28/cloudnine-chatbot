from typing import Dict, List, Optional, Union
from transformers import pipeline
from modules.vector_store import VectorStoreManager

class EmpathyLayer:
    def __init__(self):
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )

        self.vector_store = VectorStoreManager()

        self.emotion_keywords = {
            'anxiety': ['worried', 'anxious', 'nervous', 'scared', 'concerned'],
            'pain': ['hurt', 'painful', 'aching', 'sore', 'discomfort'],
            'urgency': ['emergency', 'immediate', 'urgent', 'critical'],
            'frustration': ['frustrated', 'annoyed', 'upset', 'angry'],
            'confusion': ['confused', 'unsure', 'unclear', "don't understand"]
        }

        self.empathy_templates = {
            'anxiety': [
                "I understand this might be causing you worry. We're here to help you through this.",
                "It's completely normal to feel anxious about your health. Let me assist you step by step."
            ],
            'pain': [
                "I'm sorry to hear you're in pain. We'll make sure you get the care you need.",
                "Thank you for sharing about your discomfort. We'll help you find relief."
            ],
            'urgency': [
                "I understand the urgency of your situation. Let's get you the help you need right away.",
                "Your immediate concern is our priority. We'll handle this as quickly as possible."
            ],
            'frustration': [
                "I can hear your frustration. Let's work together to resolve this.",
                "I apologize for any difficulties you're experiencing. I'm here to help make things right."
            ],
            'confusion': [
                "Let me clarify that for you in simpler terms.",
                "I'll be happy to explain this more clearly. Please don't hesitate to ask questions."
            ],
            'default': [
                "I'm here to help you with any questions or concerns you have.",
                "Your health and comfort are our top priority. How else can I assist you?"
            ]
        }

    def detect_emotion(self, message: str) -> List[Dict[str, float]]:
        try:
            emotions = self.emotion_classifier(message)[0]
            significant_emotions = [
                {"emotion": result["label"].lower(), "score": result["score"]}
                for result in emotions if result["score"] > 0.2
            ]
            if significant_emotions:
                return significant_emotions

            message = message.lower()
            for emotion, keywords in self.emotion_keywords.items():
                if any(keyword in message for keyword in keywords):
                    return [{"emotion": emotion, "score": 0.5}]

            return [{"emotion": "neutral", "score": 1.0}]
        except Exception:
            return [{"emotion": "default", "score": 1.0}]

    def analyze_medical_context(self, message: str, context: Optional[Dict] = None) -> Dict[str, Union[float, str]]:
        analysis = {
            "severity": 0.5,
            "medical_domain": "general",
            "urgency_level": "routine",
            "care_type": "standard"
        }

        if not context and not message:
            return analysis

        try:
            relevant_docs = self.vector_store.query_vector_store(query=message, k=2)
            for doc in relevant_docs:
                content = doc.page_content.lower()

                if any(dept in content for dept in ["emergency", "icu", "critical care"]):
                    analysis.update({
                        "medical_domain": "emergency",
                        "severity": 1.0,
                        "urgency_level": "immediate"
                    })
                elif any(dept in content for dept in ["cardiology", "neurology", "oncology"]):
                    analysis.update({
                        "medical_domain": "specialist",
                        "severity": 0.8
                    })

                if "pregnancy" in content or "maternity" in content:
                    analysis["care_type"] = "maternity"
                elif "pediatric" in content or "children" in content:
                    analysis["care_type"] = "pediatric"

        except Exception:
            if context:
                severity_map = {
                    'emergency': 1.0,
                    'urgent': 0.8,
                    'routine': 0.3,
                    'inquiry': 0.1
                }
                analysis["severity"] = severity_map.get(context.get('urgency', 'routine'), 0.5)

        return analysis

    def enhance_response(self, base_response: str, context: Optional[Dict] = None) -> str:
        try:
            user_message = context.get('current_context', {}).get('user_message', '') if context else ''
            emotions = self.detect_emotion(user_message)
            medical_context = self.analyze_medical_context(user_message, context)

            response_parts = []

            primary_emotion = emotions[0]["emotion"]
            emotion_score = emotions[0]["score"]

            if primary_emotion in self.empathy_templates and emotion_score > 0.3:
                response_parts.append(self.empathy_templates[primary_emotion][0])

            if medical_context.get("severity", 0) > 0.7:
                response_parts.append("I understand the urgency of your situation.")

            care_type = medical_context.get("care_type", "")
            if care_type == "maternity":
                response_parts.append("As this concerns your pregnancy, we'll ensure you receive specialized maternal care.")
            elif care_type == "pediatric":
                response_parts.append("When it comes to children's health, we take extra care to ensure their comfort and well-being.")

            if base_response:
                response_parts.append(base_response)

            if primary_emotion in ["anxiety", "fear"] or medical_context.get("severity", 0) > 0.5:
                response_parts.append("Please remember that you're in good hands with Cloud9 Hospitals.")

            if medical_context.get("urgency_level") == "immediate":
                response_parts.append("If you need immediate medical attention, please call our emergency number or visit our 24/7 emergency department.")

            return " ".join(filter(None, response_parts))

        except Exception as e:
            print(f"Error in enhance_response: {str(e)}")
            return base_response

    def personalize_response(self, response: str, user_context: Optional[Dict] = None) -> str:
        if not user_context:
            return response

        personalized_parts = []

        if 'patient_name' in user_context:
            personalized_parts.append(f"Hi {user_context['patient_name']}")

        if user_context.get('pregnancy_week'):
            personalized_parts.append(f"As you're in week {user_context['pregnancy_week']} of your pregnancy")

        if user_context.get('previous_visit'):
            visit_date = user_context.get('last_visit_date', '')
            if visit_date:
                personalized_parts.append(f"Based on your last visit on {visit_date}")
            else:
                personalized_parts.append("I can see from your records that you've been with us before")

        if user_context.get('preferred_doctor'):
            personalized_parts.append(f"I notice you usually consult with Dr. {user_context['preferred_doctor']}")

        if personalized_parts:
            response = ", ".join(personalized_parts) + ". " + response

        return response
