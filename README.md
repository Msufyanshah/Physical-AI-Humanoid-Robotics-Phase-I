# Physical AI & Humanoid Robotics: Complete Autonomous System

This repository contains a complete autonomous humanoid robot pipeline that integrates perception, planning, control, and natural language understanding. The system implements a Docusaurus-based book with an integrated RAG chatbot for interacting with the content.

## Architecture Overview

The system consists of:

1. **Frontend**: Docusaurus-based documentation site with integrated chatbot widget
2. **Backend**: FastAPI-based RAG system with OpenAI integration
3. **Perception**: Computer vision and sensing modules
4. **Planning**: Cognitive planning for action synthesis from natural language
5. **Control**: Low-level motion and navigation controllers

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- OpenAI API key
- Qdrant Cloud account (free tier sufficient)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/msufyanshah/Physical-AI-Humanoid-Robotics-Phase-I.git
cd Physical-AI-Humanoid-Robotics-Phase-I
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup

```bash
cd frontend
npm install
# Build the site
npm run build
```

### 4. Environment Configuration

Create a `.env` file in the `backend/` directory with the following environment variables:

**Backend (.env in backend/ directory):**
```env
# Backend Environment Variables
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_cluster_url
DATABASE_URL=postgresql://user:password@host:port/dbname
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
```

**Frontend (.env in frontend/ directory):**
```env
# Frontend Environment Variables
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CHATBOT_ENABLED=true
REACT_APP_SITE_URL=http://localhost:3000
```

Use the provided .env.example files as templates for both the backend and frontend directories.

## Running the System

### 1. Start the Backend Service

```bash
cd backend
python -m uvicorn src.main:app --reload
```

The backend will start on `http://localhost:8000`

### 2. Start the Frontend Service

```bash
cd frontend
npm run serve
```

The frontend will start on `http://localhost:3000`

### 3. Using the System

Once both services are running:

1. Navigate to `http://localhost:3000` to access the book
2. Use the chatbot widget to ask questions about the book content
3. Try commands like:
   - "Tell me about ROS 2 architecture"
   - "How do I create a publisher in ROS 2?"
   - "What's the difference between topics and services?"

## Key Components

### Natural Language Understanding
- Processes natural language commands
- Translates to concrete robot actions
- Handles context and follow-up questions

### RAG System
- Retrieves relevant book content based on queries
- Generates contextual responses using OpenAI
- Maintains grounding in the book content

### Perception System
- Processes visual and other sensory inputs
- Detects and tracks objects
- Builds environmental understanding

### Control System
- Executes navigation and manipulation actions
- Interfaces with robot hardware
- Maintains stability and safety

## Agent Builder Integration

The system utilizes an agent builder workflow with the ID: `wf_693e80c4d9ec819095941b5c6ccb12e40204aab5616c9e64`

This workflow manages:
- Multi-level prompting (v0 for beginners, v1 for experts)
- Specialized agents for different domains (ROS, Gazebo, Isaac, VLA)
- Intelligent triage of user queries
- Context-aware response generation

## API Endpoints

The backend provides the following REST API:

- `POST /api/v1/ask-general`: Ask general questions about book content
- `POST /api/v1/ask-selected`: Ask questions about selected text
- `POST /api/v1/embed-chunk`: Embed content for RAG functionality
- `POST /api/v1/translate-urdu`: Translate content to Urdu
- `POST /api/v1/personalize-content`: Get personalized content
- `GET /api/v1/health`: Health check endpoint
- `POST /api/v1/ask-agent`: Agent-based RAG with prompt versioning

## Chat Interface

The system includes both a web interface and a command-line interface:

### Web Interface
Access through the Docusaurus site at the main page, which includes an integrated chatbot widget.

### Command-Line Interface
```bash
cd cli
python run_chat.py
```

This provides a command-line interface to test the chat functionality directly.

## Troubleshooting

### Common Issues

1. **API Keys**: Ensure all required API keys are set in the .env file
2. **Port Conflicts**: Backend runs on 8000, frontend on 3000 by default
3. **Dependencies**: Make sure to install both backend and frontend dependencies

### Verifying Components

1. Check backend status: `curl http://localhost:8000/health`
2. Check frontend: Navigate to `http://localhost:3000` in your browser
3. Verify API connectivity: Ensure frontend can reach backend API

## Contributing

This project follows the Spec-Kit methodology for AI-assisted development. All changes should go through the proper specification → task → implementation → validation workflow.

## License

This project is licensed under the MIT License.