
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import asyncio
from src.services.chat_service import ChatService
from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.rag.agent_adapter import run_agent
from src.api.schemas import AskAgentRequest, AskAgentResponse
from src.agent_builder.runners import triage_runner, ros_runner, gazebo_runner, isaac_runner, vla_runner

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router instead of app
rag_app = APIRouter(prefix="/rag", tags=["rag"])

# Initialize services
chat_service = ChatService()
embedding_service = EmbeddingService()
retrieval_service = RetrievalService()

# Request/Response Models
class GeneralQuestionRequest(BaseModel):
    question: str
    user_id: Optional[str] = None


class SelectedTextQuestionRequest(BaseModel):
    question: str
    selected_text: str
    user_id: Optional[str] = None


class EmbedChunkRequest(BaseModel):
    content: str
    metadata: Dict[str, Any]


class EmbedChunkResponse(BaseModel):
    chunk_id: str
    embedding_status: str


class TranslationRequest(BaseModel):
    content: str
    preserve_formatting: bool = True


class PersonalizationRequest(BaseModel):
    user_id: str
    module_id: str
    chapter_id: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    services: Dict[str, bool]


@rag_app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Physical AI & Humanoid Robotics RAG API",
        "version": "1.0.0",
        "endpoints": [
            "/rag/ask-general",
            "/rag/ask-selected",
            "/rag/embed-chunk",
            "/rag/translate-urdu",
            "/rag/personalize-content",
            "/rag/health"
        ]
    }


@rag_app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    services_status = {
        "chat_service": chat_service is not None,
        "embedding_service": embedding_service is not None,
        "retrieval_service": retrieval_service is not None,
        "api_available": True
    }

    return HealthCheckResponse(
        status="healthy",
        services=services_status
    )


@rag_app.post("/ask-general")
async def ask_general(request: GeneralQuestionRequest):
    """Ask a general question about the book content"""
    try:
        logger.info(f"Processing general question: '{request.question}'")

        response = await chat_service.get_answer_general(
            question=request.question,
            user_id=request.user_id
        )

        if response is None:
            raise HTTPException(status_code=500, detail="Failed to generate answer")

        return response

    except Exception as e:
        logger.error(f"Error in ask_general: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rag_app.post("/ask-selected")
async def ask_selected(request: SelectedTextQuestionRequest):
    """Ask about selected text in the book"""
    try:
        logger.info(f"Processing selected text question: '{request.question}'")

        response = await chat_service.get_answer_selected(
            question=request.question,
            selected_text=request.selected_text,
            user_id=request.user_id
        )

        if response is None:
            raise HTTPException(status_code=500, detail="Failed to generate answer")

        return response

    except Exception as e:
        logger.error(f"Error in ask_selected: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rag_app.post("/embed-chunk", response_model=EmbedChunkResponse)
async def embed_chunk(request: EmbedChunkRequest):
    """Embed a content chunk for RAG functionality"""
    try:
        logger.info(f"Embedding content chunk of {len(request.content)} characters")

        # Embed the content
        result = await embedding_service.embed_chunk(
            content=request.content,
            metadata=request.metadata
        )

        if result is None:
            raise HTTPException(status_code=500, detail="Failed to create embedding")

        return EmbedChunkResponse(
            chunk_id=result["id"],
            embedding_status="success"
        )

    except Exception as e:
        logger.error(f"Error in embed_chunk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rag_app.post("/translate-urdu")
async def translate_urdu(request: TranslationRequest):
    """Translate content to Urdu"""
    try:
        logger.info(f"Translating {len(request.content)} character(s) to Urdu")

        # In a real implementation, this would call a translation service
        # For now, return a placeholder response
        urdu_content = "یہاں اردو میں ترجمہ ہوگا..."  # Placeholder translation

        return {
            "translated_content": urdu_content,
            "preserve_formatting": request.preserve_formatting
        }

    except Exception as e:
        logger.error(f"Error in translate_urdu: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rag_app.post("/personalize-content")
async def personalize_content(request: PersonalizationRequest):
    """Get personalized content based on user profile"""
    try:
        logger.info(f"Getting personalized content for user {request.user_id}, module {request.module_id}")

        # In a real implementation, this would retrieve personalized content
        # based on user preferences and profile
        # For now, return a placeholder response
        personalized_content = {
            "content": f"This is personalized content for module {request.module_id}",
            "user_preferences": {
                "experience_level": "beginner",
                "preferred_hardware_examples": "simulator"
            }
        }

        return personalized_content

    except Exception as e:
        logger.error(f"Error in personalize_content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@rag_app.post("/auth/register")
async def register():
    # Placeholder for registration - would implement with proper auth library
    return {"message": "Registration endpoint (placeholder)"}


@rag_app.post("/auth/login")
async def login():
    # Placeholder for login - would implement with proper auth library
    return {"message": "Login endpoint (placeholder)"}


@rag_app.post("/ask-agent", response_model=AskAgentResponse)
async def ask_agent(payload: AskAgentRequest):
    """
    Agent-based RAG with prompt versioning (v0 / v1)
    """
    try:
        # Call the run_agent function with the correct parameters
        # The run_agent function now handles triage, agent selection, and execution internally
        result = await run_agent(
            question=payload.question,
            user_level=payload.user_level,
        )

        return AskAgentResponse(
            agent=result["agent"],
            level=result["level"],
            answer=result["answer"],
            trace=result["trace"]
        )

    except Exception as e:
        logger.error(f"Error in ask_agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
