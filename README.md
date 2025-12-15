# Physical AI & Humanoid Robotics: Complete Autonomous System

## Project Status: ✅ COMPLETE

This repository contains a **COMPLETE** implementation of an autonomous humanoid robot system with integrated documentation and RAG chatbot functionality. The project successfully implements all four modules as specified in the original requirements.

## Architecture Overview

The system consists of:

1. **Frontend**: Docusaurus-based documentation site with integrated chatbot widget
2. **Backend**: FastAPI-based RAG system with OpenAI integration
3. **Perception**: Computer vision and sensing modules
4. **Planning**: Cognitive planning for action synthesis from natural language
5. **Control**: Low-level motion and navigation controllers

## Key Features Delivered

### ✅ Four Complete Learning Modules
- Module 1: The Robotic Nervous System (ROS 2) - Complete with chapters and exercises
- Module 2: The Digital Twin (Gazebo & Unity) - Complete with simulation environments
- Module 3: The AI-Robot Brain (NVIDIA Isaac) - Complete with perception and planning systems
- Module 4: Vision-Language-Action (VLA) - Complete with voice interface and cognitive planning

### ✅ AI-Powered Components
- Whisper-based speech recognition
- Large Language Model integration for natural language understanding
- Retrieval-Augmented Generation (RAG) for contextual responses
- Computer vision for object detection and scene understanding

### ✅ Robotics Infrastructure
- ROS 2 ecosystem integration
- Physics simulation with realistic parameters
- Multi-sensor fusion (LiDAR, IMU, cameras, etc.)
- Motion planning and control systems

### ✅ Educational Content
- Comprehensive documentation with learning objectives
- Hands-on exercises with solutions
- Code examples with proper explanations
- Real-world applications and use cases

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

Create a `.env` file with the following environment variables:

```env
# Backend Environment Variables
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_cluster_url
DATABASE_URL=postgresql://user:password@host:port/dbname
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key

# Frontend Environment Variables
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CHATBOT_ENABLED=true
REACT_APP_SITE_URL=http://localhost:3000
```

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

## Development

### Adding New Content

1. Create new markdown files in `frontend/docs/moduleX/`
2. Update `frontend/sidebars.js` with the new content
3. Rebuild the frontend with `npm run build`

### Extending Functionality

The system is designed with modularity in mind. New capabilities can be added by:

1. Creating new API endpoints in the backend
2. Adding new React components in the frontend
3. Updating the cognitive planner to recognize new intent types

## API Endpoints

The backend provides the following REST API:

- `POST /api/v1/ask-general`: Ask general questions about book content
- `POST /api/v1/ask-selected`: Ask questions about selected text
- `POST /api/v1/embed-chunk`: Embed content for RAG functionality
- `POST /api/v1/translate-urdu`: Translate content to Urdu
- `POST /api/v1/personalize-content`: Get personalized content
- `GET /api/v1/health`: Health check endpoint

## Troubleshooting

### Common Issues

1. **API Keys**: Ensure all required API keys are set in the .env file
2. **Port Conflicts**: Backend runs on 8000, frontend on 3000 by default
3. **Dependencies**: Make sure to install both backend and frontend dependencies

### Verifying Components

1. Check backend status: `curl http://localhost:8000/health`
2. Check frontend: Navigate to `http://localhost:3000` in your browser
3. Verify API connectivity: Ensure frontend can reach backend API

## Performance Optimization

For optimal performance:
- Use a GPU for running more complex models
- Optimize vector database queries
- Cache frequently accessed content
- Implement proper logging and monitoring

## Contributing

Contributions are welcome! Please submit issues and pull requests through the GitHub repository.

## License

This project is licensed under the MIT License.