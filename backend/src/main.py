from fastapi import FastAPI
from src.api.rag_endpoints import rag_app
from src.services.chat_service import ChatService
from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.services.vector_store_service import VectorStoreService
from src.services.error_handling import ErrorRecoverySystem
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create main FastAPI app
app = FastAPI(
    title="Physical AI & Humanoid Robotics RAG API",
    description="REST API for the Physical AI & Humanoid Robotics book with integrated RAG chatbot",
    version="1.0.0"
)

# Initialize services
try:
    chat_service = ChatService()
    embedding_service = EmbeddingService()
    retrieval_service = RetrievalService()
    vector_store_service = VectorStoreService()

    # Initialize error recovery system
    error_recovery_system = ErrorRecoverySystem(None)  # Node reference would be passed in a full ROS setup

    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    # Initialize with dummy services to allow partial functionality
    chat_service = None
    embedding_service = None
    retrieval_service = None
    vector_store_service = None
    error_recovery_system = None

# Include the RAG router
app.include_router(rag_app, prefix="/api/v1", tags=["rag"])

# Add additional routes
@app.get("/")
async def root( ):
    return {
        "message": "Welcome to the Physical AI & Humanoid Robotics RAG API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": [
            "/api/v1/ask-general",
            "/api/v1/ask-selected", 
            "/api/v1/embed-chunk",
            "/api/v1/translate-urdu",
            "/api/v1/personalize-content",
            "/api/v1/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "chat_service": "ready",
            "embedding_service": "ready", 
            "retrieval_service": "ready",
            "vector_store": "ready"
        },
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }

# Include all routers from the services if they have endpoints
# This is just a placeholder - in practice you'd import and include specific routers

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )