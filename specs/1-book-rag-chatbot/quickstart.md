# Quickstart Guide: Physical AI & Humanoid Robotics Book

**Feature**: 1-book-rag-chatbot
**Date**: 2025-12-10
**Status**: Draft

## Overview

This guide provides a quick introduction to setting up and running the Physical AI & Humanoid Robotics technical book with integrated RAG chatbot. It covers the essential steps to get the project running locally for development and testing.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: v18+ (for Docusaurus frontend)
- **npm**: v8+ or **yarn**: v1.22+ 
- **Python**: v3.11+ (for backend services)
- **Git**: latest version
- **Docker**: for containerized development (optional but recommended)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Msufyanshah/Physical-AI-Humanoid-Robotics-Phase-I.git
cd Physical-AI-Humanoid-Robotics-Phase-I
```

### 2. Set Up the Frontend (Docusaurus Book)

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install

# Start the development server
npm run start
# or
yarn start
```

The book will be available at `http://localhost:3000`.

### 3. Set Up the Backend (RAG Services)

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your actual values:
# - QDRANT_API_KEY
# - QDRANT_URL
# - DATABASE_URL (Neon Postgres)
# - OPENAI_API_KEY

# Run the backend server
python -m uvicorn src.main:app --reload
```

The backend API will be available at `http://localhost:8000`.

## Key Components

### Frontend Components (Docusaurus)

- `src/components/ChatWidget`: The RAG chatbot widget that can be embedded in book pages
- `src/components/Personalization`: Controls for content personalization
- `src/components/Translation`: Urdu translation functionality
- `docs/`: Contains all book content organized by modules

### Backend Endpoints

- `POST /ask-general`: Ask a general question about the book content
- `POST /ask-selected`: Ask a question about selected text
- `POST /embed-chunk`: Embed content for RAG functionality
- `POST /auth/register`: User registration
- `POST /auth/login`: User authentication
- `POST /personalize-content`: Get personalized content
- `POST /translate-urdu`: Translate content to Urdu

## Running the Complete System

### 1. Environment Setup

```bash
# Create environment files for both frontend and backend with required API keys
# Backend (.env file):
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_url
DATABASE_URL=your_neon_postgres_url
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key

# Frontend (.env file):
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CHATBOT_ENABLED=true
```

### 2. Start Both Services

```bash
# Terminal 1: Start the frontend
cd frontend
npm run start

# Terminal 2: Start the backend
cd backend
# Activate virtual environment first
python -m uvicorn src.main:app --reload
```

## Testing the RAG Chatbot

1. Navigate to the book (frontend) at `http://localhost:3000`
2. Find a page with the chatbot widget
3. Ask a question using the "Ask the Book" interface
4. For questions about selected text, highlight the text and use the context-aware question option

## Adding New Content

1. Add new markdown files to the appropriate module directory in `frontend/docs/`
2. Update `frontend/sidebars.js` to include the new content in the navigation
3. If adding code examples, ensure they follow the book's reproducibility standards
4. Run `npm run build` in the frontend directory to test the build with your new content

## Running Tests

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend
python -m pytest
```

## Deployment

### GitHub Pages (Frontend)
```bash
cd frontend
npm run build
npm run deploy
```

### Backend Deployment
- Ensure your cloud services (Qdrant Cloud, Neon Postgres) are set up
- Deploy the FastAPI backend to your preferred cloud platform (e.g., Heroku, Render, Vercel, or AWS)

## Troubleshooting

### Common Issues

1. **Backend not connecting to Qdrant**:
   - Verify your QDRANT_API_KEY and QDRANT_URL are correct in the .env file
   - Ensure your Qdrant Cloud instance is active

2. **Frontend can't connect to backend**:
   - Check that both services are running
   - Verify the REACT_APP_API_URL is set correctly

3. **RAG responses are not relevant**:
   - Ensure the content has been properly embedded using the `/embed-chunk` endpoint
   - Check that the Qdrant database contains your book content embeddings