
import os
import sys
from pathlib import Path
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
import subprocess

project_root = Path(__file__).parent
sys.path.append(str(project_root))

def setup_logging():
    """Configure logging settings"""
    log_dir = project_root / 'logs'
    if not log_dir.exists():
        log_dir.mkdir(parents=True)

    logger.remove()  
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        log_dir / "initialization.log",
        rotation="100 MB",
        retention="10 days",
        level="DEBUG"
    )

def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'data/raw/cloudnine_scraped',
        'data/raw/cloudnine_scraped/guidelines',
        'data/processed',
        'logs',
        'models'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            logger.info(f"Created directory: {dir_path}")

def install_dependencies():
    """Install required Python packages"""
    try:
        logger.info("Installing dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        logger.info("Successfully installed dependencies")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        return False

def run_scraper():
    """Run the Cloud9 web scraper"""
    try:
        logger.info("Starting web scraping...")
        from scraper.cloudnine_scraper import CloudNineScraper
        
        scraper = CloudNineScraper()
        scraper.scrape_all()
        logger.info("Web scraping completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during web scraping: {str(e)}")
        return False

def initialize_vector_store():
    """Initialize and populate the vector store"""
    try:
        logger.info("Initializing vector store...")
        from scripts.init_vector_store import main as init_vector_store
        
        init_vector_store()
        logger.info("Vector store initialization completed")
        return True
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        return False

def start_services():
    """Start the FastAPI server and Streamlit UI"""
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Start FastAPI server
            logger.info("Starting FastAPI server...")
            fastapi_future = executor.submit(
                subprocess.run,
                ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                cwd=str(project_root)
            )

            logger.info("Starting Streamlit UI...")
            streamlit_future = executor.submit(
                subprocess.run,
                ["streamlit", "run", "frontend/chatbot_ui.py", "--server.port", "8501"],
                cwd=str(project_root)
            )

            fastapi_future.result()
            streamlit_future.result()

    except Exception as e:
        logger.error(f"Error starting services: {str(e)}")
        return False

def main():
    """Main initialization function"""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting chatbot initialization...")

        ensure_directories()

        if not install_dependencies():
            logger.error("Failed to install dependencies")
            sys.exit(1)

        initialization_steps = [
            ("Web scraping", run_scraper),
            ("Vector store initialization", initialize_vector_store)
        ]

        for step_name, step_func in initialization_steps:
            logger.info(f"Starting {step_name}...")
            if not step_func():
                logger.error(f"{step_name} failed")
                sys.exit(1)
            logger.info(f"{step_name} completed successfully")

        logger.info("Starting services...")
        start_services()

    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()