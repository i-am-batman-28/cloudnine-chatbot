import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

API_CONFIG = {
    'HOST': os.getenv('CHATBOT_HOST', '0.0.0.0'),
    'PORT': int(os.getenv('CHATBOT_PORT', 8000)),
    'DEBUG': os.getenv('CHATBOT_DEBUG', 'False').lower() == 'true',
    'API_VERSION': '1.0.0',
    'API_TITLE': 'Cloud9 Hospitals Chatbot API',
    'API_DESCRIPTION': 'An empathetic healthcare chatbot for Cloud9 Hospitals'
}

DATA_CONFIG = {
    'RAW_DATA_DIR': BASE_DIR / 'data' / 'raw' / 'cloudnine_scraped',
    'PROCESSED_DATA_DIR': BASE_DIR / 'data' / 'processed',
    'INTENTS_FILE': BASE_DIR / 'data' / 'processed' / 'intents.json',
    'DUMMY_DIALOGS_FILE': BASE_DIR / 'data' / 'dummy_dialogs.json'
}

SCRAPER_CONFIG = {
    'BASE_URL': 'https://www.cloudninecare.com',  
    'HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    },
    'TIMEOUT': 30,
    'RETRY_ATTEMPTS': 3,
    'DELAY_BETWEEN_REQUESTS': 2  # seconds
}

NLP_CONFIG = {
    'INTENT_CLASSIFIER': {
        'MODEL_TYPE': 'distilbert-base-uncased',
        'MAX_LENGTH': 128,
        'BATCH_SIZE': 16
    },
    'ENTITY_EXTRACTOR': {
        'MODEL_TYPE': 'en_core_web_sm',
        'CUSTOM_ENTITIES': ['SYMPTOM', 'DEPARTMENT', 'DOCTOR', 'TREATMENT']
    }
}

PIPELINE_CONFIG = {
    'MAX_TURNS': 10,
    'CONFIDENCE_THRESHOLD': 0.7,
    'DEFAULT_LANGUAGE': 'en',
    'SESSION_TIMEOUT': 3600,  # 1 hour in seconds
    'MAX_RESPONSE_LENGTH': 200
}

EMPATHY_CONFIG = {
    'EMOTION_DETECTION_THRESHOLD': 0.6,
    'DEFAULT_EMPATHY_LEVEL': 'medium',
    'EMERGENCY_KEYWORDS': [
        'emergency', 'urgent', 'immediate',
        'severe', 'critical', 'life-threatening'
    ],
    'SENSITIVE_TOPICS': [
        'cancer', 'terminal', 'death',
        'chronic', 'pain', 'anxiety'
    ]
}

LOG_CONFIG = {
    'VERSION': 1,
    'DISABLE_EXISTING_LOGGERS': False,
    'FORMATTERS': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'HANDLERS': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'chatbot.log',
            'mode': 'a',
        },
    },
    'LOGGERS': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}