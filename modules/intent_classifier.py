from typing import Dict, List, Tuple
from transformers import pipeline
from app.config import NLP_CONFIG
import json
import numpy as np

class IntentClassifier:
    def __init__(self):
        self.config = NLP_CONFIG['INTENT_CLASSIFIER']
        self.intents = self._load_intents()
        self.classifier = pipeline(
            "text-classification",
            model=self.config['MODEL_TYPE'],
            return_all_scores=True
        )

    def _load_intents(self) -> Dict:
        """Load and parse intents from the processed data file"""
        try:
            with open('data/processed/intents.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to default intents if file not found
            return {
                "intents": [
                    {
                        "name": "appointment_booking",
                        "patterns": [
                            "I want to book an appointment",
                            "Schedule a consultation",
                            "Book a doctor visit"
                        ],
                        "responses": [
                            "I'll help you book an appointment. Could you specify which department or doctor you'd like to see?"
                        ]
                    },
                    {
                        "name": "symptom_inquiry",
                        "patterns": [
                            "I have a headache",
                            "My stomach hurts",
                            "I'm feeling sick"
                        ],
                        "responses": [
                            "I understand you're not feeling well. Could you tell me more about your symptoms?"
                        ]
                    },
                    {
                        "name": "department_info",
                        "patterns": [
                            "What departments do you have",
                            "Show me your specialties",
                            "What medical services do you offer"
                        ],
                        "responses": [
                            "I'll be happy to tell you about our departments and specialties."
                        ]
                    },
                    {
                        "name": "emergency",
                        "patterns": [
                            "This is an emergency",
                            "I need urgent help",
                            "Critical situation"
                        ],
                        "responses": [
                            "If this is a medical emergency, please call emergency services immediately at [EMERGENCY_NUMBER]."
                        ]
                    },
                    {
                        "name": "general_inquiry",
                        "patterns": [
                            "What are your working hours",
                            "Where are you located",
                            "Do you accept insurance"
                        ],
                        "responses": [
                            "I'll help you with that information."
                        ]
                    }
                ]
            }

    def classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify the intent of user input text"""
        # Get classification scores for all intents
        scores = self._get_intent_scores(text)
        
        # Get the highest scoring intent
        max_intent = max(scores.items(), key=lambda x: x[1])
        
        return max_intent[0], max_intent[1]

    def _get_intent_scores(self, text: str) -> Dict[str, float]:
        """Calculate confidence scores for each intent"""
        scores = {}
        
        # Calculate similarity scores between input and each intent pattern
        for intent in self.intents['intents']:
            pattern_scores = []
            for pattern in intent['patterns']:
                # Use transformer model to get similarity score
                result = self.classifier(text + " [SEP] " + pattern)
                pattern_scores.append(result[0][1]['score'])  # Assuming binary classification
            
            # Take the maximum score among patterns for this intent
            scores[intent['name']] = max(pattern_scores)
        
        return scores

    def get_response(self, intent: str) -> str:
        """Get a random response for the given intent"""
        for intent_data in self.intents['intents']:
            if intent_data['name'] == intent:
                return np.random.choice(intent_data['responses'])
        return "I'm not sure how to respond to that. Could you please rephrase?"

    def add_training_example(self, intent: str, pattern: str):
        """Add a new training example to the intent patterns"""
        for intent_data in self.intents['intents']:
            if intent_data['name'] == intent:
                if pattern not in intent_data['patterns']:
                    intent_data['patterns'].append(pattern)
                break