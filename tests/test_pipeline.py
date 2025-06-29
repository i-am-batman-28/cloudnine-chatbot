import pytest
from app.chatbot_pipeline import ChatbotPipeline, PipelineStep
from modules.intent_classifier import IntentClassifier
from modules.entity_extractor import EntityExtractor
from modules.memory import ConversationMemory

@pytest.fixture
def pipeline():
    return ChatbotPipeline()

@pytest.fixture
def memory():
    return ConversationMemory()

@pytest.fixture
def intent_classifier():
    return IntentClassifier()

@pytest.fixture
def entity_extractor():
    return EntityExtractor()

def test_pipeline_initialization(pipeline):
    """Test if pipeline initializes with correct steps"""
    assert pipeline is not None
    assert len(pipeline.pipeline_steps) > 0
    assert all(isinstance(step, PipelineStep) for step in pipeline.pipeline_steps)

def test_process_message(pipeline):
    """Test basic message processing"""
    session_id = "test_session"
    message = "I need to book an appointment"
    
    response, next_question, context = pipeline.process_message(session_id, message)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0

def test_conversation_memory(memory):
    """Test conversation memory management"""
    session_id = "test_session"
    
    memory.create_session(session_id)
    assert session_id in memory.sessions
    
    memory.update_session(
        session_id=session_id,
        user_message="Test message",
        bot_response="Test response",
        entities={"test_entity": "value"},
        intent="test_intent"
    )
    
    session = memory.get_session_info(session_id)
    assert session is not None
    assert session['turn_count'] == 1
    assert len(session['conversation_history']) == 1

def test_intent_classification(intent_classifier):
    """Test intent classification"""
    test_messages = [
        "I want to book an appointment",
        "What are your working hours?",
        "I need urgent medical help"
    ]
    
    for message in test_messages:
        intent, confidence = intent_classifier.classify_intent(message)
        assert intent is not None
        assert isinstance(intent, str)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

def test_entity_extraction(entity_extractor):
    """Test entity extraction"""
    test_message = "I have a headache and need to see a doctor in the neurology department"
    
    entities = entity_extractor.extract_entities(test_message)
    
    assert entities is not None
    assert isinstance(entities, dict)
    assert 'SYMPTOM' in entities
    assert 'DEPARTMENT' in entities
    
    assert any('headache' in symptom for symptom in entities['SYMPTOM'])
    assert any('neurology' in dept for dept in entities['DEPARTMENT'])

def test_medical_context_extraction(entity_extractor):
    """Test medical context extraction"""
    test_message = "I have severe chest pain and need urgent help"
    
    context = entity_extractor.extract_medical_context(test_message)
    
    assert context is not None
    assert isinstance(context, dict)
    assert 'symptoms' in context
    assert 'urgency_level' in context
    assert context['urgency_level'] in ['emergency', 'urgent', 'routine']

def test_pipeline_step_validation(pipeline):
    """Test pipeline step validation"""
    session_id = "test_session"
    test_responses = [
        "I need to see a doctor",
        "I have a severe headache",
        "Yes, I've been here before",
        "I prefer the neurology department"
    ]
    
    for response in test_responses:
        result = pipeline.process_message(session_id, response)
        assert all(isinstance(item, (str, dict, type(None))) for item in result)

def test_conversation_flow(pipeline, memory):
    """Test complete conversation flow"""
    session_id = "test_flow"
    
    memory.create_session(session_id)
    
    messages = [
        "I need to book an appointment",
        "I have a headache",
        "Yes, I've been here before",
        "I prefer the neurology department"
    ]
    
    for message in messages:
        response, next_question, context = pipeline.process_message(session_id, message)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Update conversation memory
        memory.update_session(
            session_id=session_id,
            user_message=message,
            bot_response=response
        )
    
    history = memory.get_conversation_history(session_id)
    assert len(history) == len(messages)