
from fastapi import APIRouter, HTTPException, Depends, Security
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
from src.utils.auth_utils import authenticate_user, create_access_token, verify_password, get_password_hash
from src.database import get_db, User
from src.models.database import PersonalizationSettingsDB
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.jwt import JWTError
from pydantic import BaseModel
from src.utils.auth_utils import SECRET_KEY, ALGORITHM, TokenData, verify_token

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


# Authentication Models
class RegisterRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    username: Optional[str] = None
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    username: Optional[str] = None


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


@rag_app.post("/auth/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    try:
        # Check if user already exists (email is required, username is optional)
        existing_user_by_email = db.query(User).filter(User.email == request.email).first()
        if existing_user_by_email:
            raise HTTPException(
                status_code=409,
                detail="A user with this email already exists"
            )

        # Only check username if it's provided
        if request.username:
            existing_user_by_username = db.query(User).filter(User.username == request.username).first()
            if existing_user_by_username:
                raise HTTPException(
                    status_code=409,
                    detail="A user with this username already exists"
                )

        # Ensure password is not longer than 72 bytes for bcrypt
        password = request.password
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate password to 72 bytes if it's too long
            password = password_bytes[:72].decode('utf-8', errors='ignore')

        # Hash the password
        hashed_password = get_password_hash(password)

        # Create new user
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            email=request.email,
            username=request.username,
            password_hash=hashed_password
        )

        # Add to database
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
        except Exception as db_error:
            db.rollback()
            logger.error(f"Database error in register: {db_error}")
            raise HTTPException(status_code=500, detail="Database error occurred")

        return RegisterResponse(
            user_id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            message="User registered successfully"
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in register: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@rag_app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    try:
        # Ensure password is not longer than 72 bytes for bcrypt
        password = request.password
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate password to 72 bytes if it's too long
            password = password_bytes[:72].decode('utf-8', errors='ignore')

        # Authenticate user with the validated password
        user = authenticate_user(request.email, password, db)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        # Create access token
        access_token_expires = timedelta(minutes=30)  # 30 minutes
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            username=user.username
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


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


# Security scheme for JWT token
security = HTTPBearer()


# Function to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
    except (JWTError, ExpiredSignatureError):
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# Personalization Settings Models
class PersonalizationSettingsRequest(BaseModel):
    experience_level: Optional[str] = "beginner"
    preferred_hardware_examples: Optional[str] = "simulator"
    language_preference: Optional[str] = "en"


class PersonalizationSettingsResponse(BaseModel):
    user_id: str
    experience_level: Optional[str] = "beginner"
    preferred_hardware_examples: Optional[str] = "simulator"
    language_preference: Optional[str] = "en"


@rag_app.get("/user/personalization", response_model=PersonalizationSettingsResponse)
async def get_user_personalization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's personalization settings"""
    try:
        # Try to get existing personalization settings
        settings = db.query(PersonalizationSettingsDB).filter(
            PersonalizationSettingsDB.user_id == current_user.id
        ).first()

        if not settings:
            # Create default settings if they don't exist
            settings = PersonalizationSettingsDB(
                user_id=current_user.id,
                experience_level="beginner",
                preferred_hardware_examples="simulator",
                language_preference="en"
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return PersonalizationSettingsResponse(
            user_id=settings.user_id,
            experience_level=settings.experience_level,
            preferred_hardware_examples=settings.preferred_hardware_examples,
            language_preference=settings.language_preference
        )

    except Exception as e:
        logger.error(f"Error getting personalization settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@rag_app.put("/user/personalization", response_model=PersonalizationSettingsResponse)
async def update_user_personalization(
    request: PersonalizationSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's personalization settings"""
    try:
        # Try to get existing settings
        settings = db.query(PersonalizationSettingsDB).filter(
            PersonalizationSettingsDB.user_id == current_user.id
        ).first()

        if not settings:
            # Create new settings if they don't exist
            settings = PersonalizationSettingsDB(
                user_id=current_user.id,
                experience_level=request.experience_level,
                preferred_hardware_examples=request.preferred_hardware_examples,
                language_preference=request.language_preference
            )
            db.add(settings)
        else:
            # Update existing settings
            settings.experience_level = request.experience_level
            settings.preferred_hardware_examples = request.preferred_hardware_examples
            settings.language_preference = request.language_preference

        db.commit()
        db.refresh(settings)

        return PersonalizationSettingsResponse(
            user_id=settings.user_id,
            experience_level=settings.experience_level,
            preferred_hardware_examples=settings.preferred_hardware_examples,
            language_preference=settings.language_preference
        )

    except Exception as e:
        logger.error(f"Error updating personalization settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
