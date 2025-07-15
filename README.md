# Cloud9 Hospitals Chatbot 🏥

An intelligent, empathetic chatbot designed to enhance patient experience at Cloud9 Hospitals. This AI-powered assistant provides contextual support for appointments, medical inquiries, and general information while maintaining a compassionate approach to healthcare communication. The chatbot features smart response formatting, context-aware suggestions, and multilingual support to ensure a seamless patient experience.

## 🌟 Features

- **Smart Conversation Flow**: Pipeline-based conversation management with context-aware responses
- **Empathetic Communication**: Built-in empathy layer for compassionate healthcare interactions
- **Intelligent Suggestions**: Context-based action suggestions that appear only when relevant
- **Multi-Intent Recognition**: Accurate identification and handling of multiple user intents
- **Entity Extraction**: Smart identification of symptoms, departments, doctors, and appointments
- **Knowledge Integration**: RAG (Retrieval Augmented Generation) for accurate medical information
- **Multilingual Support**: Seamless communication in multiple languages
- **Dynamic UI**: Modern, responsive interface with emoji-enhanced messages
- **Web Data Integration**: Automatic updates from Cloud9 Hospitals website
- **WhatsApp Integration**: Direct patient communication through WhatsApp messaging

## 🛠️ Technical Architecture

### Core Components

1. **Chatbot Pipeline**
   - Smart Intent Classification
   - Context-Aware Entity Extraction
   - Dynamic Memory Management
   - Intelligent Response Generation
   - Empathy Layer Integration

2. **NLP Modules**
   - Advanced Intent Classifier (Transformer-based)
   - Enhanced Entity Extractor (SpaCy)
   - RAG Response Generator with Context Awareness
   - Multilingual Processing Support

3. **Data Management**
   - Automated Web Scraper
   - Smart Data Parser
   - Vector-Based Knowledge Base
   - Real-time Context Store

4. **User Interface**
   - FastAPI Backend with CORS Support
   - Modern React Frontend
   - Real-time Response Formatting
   - Dynamic Suggestion System
   - WhatsApp Messaging Integration

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn package manager
- pip package manager
- Plivo WhatsApp Business Account

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd cloudnine_chatbot
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Download required NLP models
python -m spacy download en_core_web_sm
```

3. Set up the frontend:
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### Configuration

1. Backend Configuration:
```bash
# Copy the example environment file
cp .env.example .env

# Update the .env file with your settings
CHATBOT_HOST=0.0.0.0
CHATBOT_PORT=8000
CHATBOT_DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000

# Plivo WhatsApp Configuration
PLIVO_AUTH_ID=your_plivo_auth_id
PLIVO_AUTH_TOKEN=your_plivo_auth_token
PLIVO_WHATSAPP_NUMBER=your_whatsapp_number
```

2. Frontend Configuration:
```bash
# Navigate to frontend directory
cd frontend

# Create .env file for frontend
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### Running the Application

1. Start the Backend Server:
```bash
# Activate virtual environment if not already activated
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Start the FastAPI server
python run.py
```

2. Start the Frontend Development Server:
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start the React development server
npm start
```

The application will be available at:
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /chat`: Main chatbot interaction endpoint
  - Handles message processing with context awareness
  - Supports multilingual input
  - Returns formatted responses with relevant suggestions

- `POST /whatsapp/webhook`: WhatsApp integration endpoint
  - Handles incoming WhatsApp messages
  - Processes messages through chatbot pipeline
  - Sends formatted responses back to WhatsApp

- `GET /health`: Health check endpoint
  - Monitors API availability
  - Returns service status

## 🧪 Testing

### Backend Tests

1. Run the complete test suite:
```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Run all tests
python -m pytest tests/
```

2. Generate coverage report:
```bash
# Run tests with coverage
python -m pytest --cov=app tests/

# Generate HTML coverage report
python -m pytest --cov=app --cov-report=html tests/
```

### Frontend Tests

1. Run React component tests:
```bash
# Navigate to frontend directory
cd frontend

# Run tests
npm test
```

2. Run end-to-end tests:
```bash
# In frontend directory
npm run test:e2e
```

## 📊 Data Management

### Knowledge Base Updates

1. Update hospital data:
```bash
# Scrape latest data
python -m scraper.scraper

# Process and validate data
python -m scraper.parser
```

2. Verify data integrity:
```bash
# Check data consistency
python -m scraper.validate

# Update vector store
python -m modules.vector_store --update
```

## 🤝 Contributing

### Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines for Python code
   - Use ESLint and Prettier for JavaScript/React code
   - Maintain consistent naming conventions

2. **Branch Strategy**
   - `main`: Production-ready code
   - `develop`: Development branch
   - Feature branches: `feature/your-feature-name`
   - Bug fixes: `fix/bug-description`

3. **Commit Messages**
   - Use clear, descriptive commit messages
   - Follow conventional commits format
   - Reference issues when applicable

### Submission Process

1. Fork the repository
2. Create a feature branch from `develop`
3. Implement your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a Pull Request

### Code Review Process

- All submissions require review
- Address review comments promptly
- Maintain a constructive dialogue
- Follow the project's code of conduct

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Cloud9 Hospitals for the opportunity to enhance patient care
- Open-source community for the amazing tools and libraries
- Healthcare professionals for domain expertise and guidance
- Contributors who help improve the chatbot