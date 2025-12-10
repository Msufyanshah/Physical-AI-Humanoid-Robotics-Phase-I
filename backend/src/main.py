from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from contextlib import asynccontextmanager
import json

from src.services.chat_service import ChatService
from src.services.retrieval_service import RetrievalService
from src.services.embedding_service import EmbeddingService
from src.services.vector_store import QdrantService

# Define Pydantic models for request/response
class GeneralQuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None

class SelectedTextQuestionRequest(BaseModel):
    question: str
    selected_text: str
    user_id: Optional[str] = None

class EmbedChunkRequest(BaseModel):
    content: str
    metadata: dict

class EmbedChunkResponse(BaseModel):
    chunk_id: str
    embedding_status: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None
    background: Optional[str] = "beginner"
    hardware_level: Optional[str] = "simulator-only"

class LoginRequest(BaseModel):
    email: str
    password: str

class PersonalizeContentRequest(BaseModel):
    user_id: str
    module_id: str
    chapter_id: Optional[str] = None

class TranslateRequest(BaseModel):
    content: str
    preserve_formatting: bool = True

class HealthCheck(BaseModel):
    status: str = "OK"

# Initialize services
chat_service = None
retrieval_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services on startup
    global chat_service, retrieval_service
    chat_service = ChatService()
    retrieval_service = RetrievalService()
    yield
    # Cleanup on shutdown if needed

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Physical AI & Humanoid Robotics RAG Chatbot API"}

@app.get("/health", response_model=HealthCheck)
def health_check():
    return HealthCheck(status="OK")

@app.post("/ask-general")
async def ask_general(request: GeneralQuestionRequest):
    """
    Submit a question to the RAG chatbot to get an answer based on the book content
    """
    try:
        # Use the chat service to answer the question
        result = await chat_service.get_answer_general(
            question=request.question,
            user_id=request.user_id
        )

        if not result:
            raise HTTPException(status_code=500, detail="Error generating answer")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask-selected")
async def ask_selected(request: SelectedTextQuestionRequest):
    """
    Submit a question about specific text selected in the book
    """
    try:
        # Use the chat service to answer the question about selected text
        result = await chat_service.get_answer_selected(
            question=request.question,
            selected_text=request.selected_text,
            user_id=request.user_id
        )

        if not result:
            raise HTTPException(status_code=500, detail="Error generating answer")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed-chunk", response_model=EmbedChunkResponse)
async def embed_chunk(request: EmbedChunkRequest):
    """
    Submit a content chunk to be embedded and stored in the vector database
    """
    try:
        # Initialize embedding and vector store services
        embedding_service = EmbeddingService()
        vector_store = QdrantService()

        # Create embedding for the content
        chunk_data = await embedding_service.embed_chunk(
            content=request.content,
            metadata=request.metadata
        )

        if not chunk_data:
            raise HTTPException(status_code=500, detail="Error creating embedding")

        # Upsert to vector store
        success = vector_store.upsert_vectors([chunk_data])

        if not success:
            raise HTTPException(status_code=500, detail="Error storing embedding")

        return EmbedChunkResponse(
            chunk_id=chunk_data["id"],
            embedding_status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/register")
async def register(request: RegisterRequest):
    """
    Create a new user account with BetterAuth
    """
    # This endpoint would integrate with BetterAuth
    # For now, we'll return a placeholder response
    return {
        "user_id": "user-placeholder-12345",
        "message": "User registered successfully (placeholder)"
    }

@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    Authenticate a user and return session token
    """
    # This endpoint would integrate with BetterAuth
    # For now, we'll return a placeholder response
    return {
        "token": "placeholder-jwt-token",
        "user_id": "user-placeholder-12345",
        "message": "Login successful (placeholder)"
    }

@app.post("/personalize-content")
async def personalize_content(request: PersonalizeContentRequest):
    """
    Retrieve book content tailored to the user's background and preferences
    """
    # This would retrieve personalized content based on user preferences
    # For now, we'll return a placeholder response
    return {
        "personalized_content": "Based on your background, we've included additional explanations...",
        "user_preferences": {
            "experience_level": "beginner",
            "preferred_hardware_examples": "simulator"
        }
    }

@app.post("/translate-urdu")
async def translate_urdu(request: TranslateRequest):
    """
    Convert book content to Urdu language
    """
    # This would translate content to Urdu
    # For now, we'll return a placeholder response
    return {
        "translated_content": "یہاں اردو میں ترجمہ ہوگا..."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)