import pytest
from modules.intent_classifier import IntentClassifier
from app.empathy_layer import EmpathyLayer

@pytest.fixture
def intent_classifier():
    return IntentClassifier()

@pytest.fixture
def empathy_layer():
    return EmpathyLayer()

def test_intent_classification_basic(intent_classifier):
    """Test basic intent classification"""
    test_cases = [
        ("I want to book an appointment", "appointment_booking"),
        ("My head hurts", "symptom_inquiry"),
        ("What departments do you have", "department_info"),
        ("This is an emergency", "emergency"),
        ("What are your working hours", "general_inquiry")
    ]

    for message, expected_intent in test_cases:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent == expected_intent
        assert 0 <= confidence <= 1

def test_intent_confidence_scores(intent_classifier):
    """Test confidence scores for intent classification"""
    message = "I need to see a doctor urgently"
    scores = intent_classifier._get_intent_scores(message)

    assert isinstance(scores, dict)
    assert all(0 <= score <= 1 for score in scores.values())
    assert len(scores) > 0

def test_intent_response_generation(intent_classifier):
    """Test response generation for intents"""
    test_intents = [
        "appointment_booking",
        "symptom_inquiry",
        "department_info",
        "emergency",
        "general_inquiry"
    ]

    for intent in test_intents:
        response = intent_classifier.get_response(intent)
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

def test_intent_training_example_addition(intent_classifier):
    """Test adding new training examples"""
    intent = "appointment_booking"
    new_pattern = "I need to schedule a consultation"

    intent_classifier.add_training_example(intent, new_pattern)
    
    # Verify the pattern was added
    for intent_data in intent_classifier.intents['intents']:
        if intent_data['name'] == intent:
            assert new_pattern in intent_data['patterns']
            break

def test_empathy_emotion_detection(empathy_layer):
    """Test emotion detection in user messages"""
    test_cases = [
        ("I'm really worried about my test results", ["anxiety"]),
        ("My back is hurting a lot", ["pain"]),
        ("I need immediate help", ["urgency"]),
        ("I'm frustrated with the wait time", ["frustration"]),
        ("I don't understand what's happening", ["confusion"])
    ]

    for message, expected_emotions in test_cases:
        detected_emotions = empathy_layer.detect_emotion(message)
        assert all(emotion in detected_emotions for emotion in expected_emotions)

def test_empathy_response_enhancement(empathy_layer):
    """Test enhancement of responses with empathy"""
    test_cases = [
        {
            "base_response": "We'll schedule your appointment.",
            "user_message": "I'm worried about my symptoms",
            "context": {"urgency": "routine"}
        },
        {
            "base_response": "Let me check your test results.",
            "user_message": "I'm in a lot of pain",
            "context": {"urgency": "urgent"}
        },
        {
            "base_response": "A doctor will see you shortly.",
            "user_message": "This is an emergency",
            "context": {"urgency": "emergency"}
        }
    ]

    for case in test_cases:
        enhanced_response = empathy_layer.enhance_response(
            case["base_response"],
            case["user_message"],
            case["context"]
        )
        
        assert enhanced_response is not None
        assert len(enhanced_response) > len(case["base_response"])
        assert case["base_response"] in enhanced_response

def test_empathy_medical_context_analysis(empathy_layer):
    """Test medical context analysis"""
    test_contexts = [
        {"urgency": "emergency"},
        {"urgency": "urgent"},
        {"urgency": "routine"},
        {"urgency": "inquiry"}
    ]

    for context in test_contexts:
        severity = empathy_layer.analyze_medical_context(context)
        assert isinstance(severity, float)
        assert 0 <= severity <= 1

def test_empathy_response_personalization(empathy_layer):
    """Test response personalization"""
    test_cases = [
        {
            "response": "We'll help you with that.",
            "context": {"patient_name": "John"}
        },
        {
            "response": "Let me assist you.",
            "context": {"previous_visit": True}
        },
        {
            "response": "I'll check that for you.",
            "context": {"patient_name": "Sarah", "previous_visit": True}
        }
    ]

    for case in test_cases:
        personalized_response = empathy_layer.personalize_response(
            case["response"],
            case["context"]
        )
        
        assert personalized_response is not None
        assert len(personalized_response) > len(case["response"])
        
        if "patient_name" in case["context"]:
            assert case["context"]["patient_name"] in personalized_response

def test_empathy_template_selection(empathy_layer):
    """Test empathy template selection based on emotions"""
    emotions = ["anxiety", "pain", "urgency", "frustration", "confusion"]

    for emotion in emotions:
        templates = empathy_layer.empathy_templates.get(emotion, [])
        assert len(templates) > 0
        assert all(isinstance(template, str) for template in templates)

def test_empathy_response_consistency(empathy_layer):
    """Test consistency of empathetic responses"""
    message = "I'm worried about my condition"
    base_response = "We'll help you understand your condition better."

    # Generate multiple responses and check for consistency
    responses = [empathy_layer.enhance_response(base_response, message) for _ in range(5)]
    
    # All responses should contain the base response
    assert all(base_response in response for response in responses)
    # All responses should contain empathetic elements
    assert all("understand" in response.lower() or "worry" in response.lower() for response in responses)