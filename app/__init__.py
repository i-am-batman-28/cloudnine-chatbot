# This file marks the app directory as a Python package.
# It allows importing modules from this directory.

__version__ = "1.0.0"

# Import main components for easier access
from .chatbot_pipeline import ChatbotPipeline
from .empathy_layer import EmpathyLayer

__all__ = ['ChatbotPipeline', 'EmpathyLayer']
