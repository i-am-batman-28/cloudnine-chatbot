import os
import sys
from pathlib import Path
import logging
import uvicorn

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.config import API_CONFIG
from app.main import app
from modules.vector_store import VectorStoreManager
from modules.rag_response import RAGResponseGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chatbot.log')
    ]
)

logger = logging.getLogger(__name__)

def init_data_directories():
    """Initialize necessary data directories"""
    try:
        data_dirs = [
            Path('data/raw/cloudnine_scraped'),
            Path('data/processed')
        ]
        
        for dir_path in data_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized directory: {dir_path}")
            
    except Exception as e:
        logger.error(f"Error initializing data directories: {str(e)}")
        raise

def init_vector_store():
    """Initialize and verify vector store"""
    try:
        vector_store = VectorStoreManager()
        
        test_query = "What services do you offer?"
        results = vector_store.query_vector_store(test_query, k=1)
        
        if results:
            logger.info("✅ Vector store initialized and verified")
            return True
        else:
            logger.warning("⚠️ Vector store query returned no results, running setup...")
            success = vector_store.setup_vector_store()
            if success:
                logger.info("✅ Vector store setup completed successfully")
            else:
                logger.error("❌ Vector store setup failed")
            return success
            
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        return False

def init_rag_components():
    """Initialize RAG components"""
    try:
        rag_generator = RAGResponseGenerator()
        test_query = "Hello, how can you help me?"
        response = rag_generator.generate_response(test_query)
        
        if response:
            logger.info("✅ RAG components initialized successfully")
            return True
        else:
            logger.error("❌ RAG components failed to generate response")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing RAG components: {str(e)}")
        return False

def main():
    """Main entry point of the application"""
    try:
        init_data_directories()
        
        if not init_vector_store():
            logger.error("❌ Failed to initialize vector store")
            return
            
        if not init_rag_components():
            logger.error("❌ Failed to initialize RAG components")
            return
        
        logger.info("🚀 Starting Cloud9 Hospitals Chatbot API")
        logger.info(f"API Version: {API_CONFIG['API_VERSION']}")
        logger.info(f"Debug Mode: {API_CONFIG['DEBUG']}")
        
        uvicorn.run(
            "app.main:app",
            host=API_CONFIG['HOST'],
            port=API_CONFIG['PORT'],
            reload=API_CONFIG['DEBUG']
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start the application: {str(e)}")
        raise

if __name__ == "__main__":
    main()
