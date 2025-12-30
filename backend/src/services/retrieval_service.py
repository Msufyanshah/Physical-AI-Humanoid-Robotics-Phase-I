import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

from src.services.embedding_service import EmbeddingService

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("Qdrant client not installed")

class RetrievalService:
    def __init__(self):
        self.collection_name = "book_content_chunks"
        self.embedding_service = EmbeddingService()
        self.qdrant_client = None

        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if QDRANT_AVAILABLE and qdrant_url:
            try:
                if qdrant_api_key:
                    self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
                else:
                    self.qdrant_client = QdrantClient(url=qdrant_url)
                self._ensure_collection()
                logger.info("Connected to Qdrant")
            except Exception as e:
                logger.error(f"Qdrant connection failed: {e}")
                self.qdrant_client = None
        else:
            logger.warning("Qdrant not configured; running in no-op mode")

    def _ensure_collection(self):
        collections = self.qdrant_client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_service.embedding_dim,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")

    async def store_content_chunk(self, content: str, metadata: dict):
        if not self.qdrant_client:
            logger.warning("Qdrant unavailable; skipping storage")
            return

        vector = self.embedding_service.embed(content)

        # Generate a valid ID for Qdrant (using UUID to ensure uniqueness and proper format)
        import uuid
        point_id = str(uuid.uuid4())

        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": content,
                        "id": point_id,  # Also store the ID in the payload for reference
                        **metadata
                    }
                )
            ]
        )

    async def retrieve_relevant_chunks(self, query: str, top_k: int = 5):
        """
        Retrieve relevant text chunks based on a query string
        """
        if not self.qdrant_client:
            logger.warning("Qdrant unavailable; returning empty results")
            return []

        try:
            # Embed the query
            query_vector = self.embedding_service.embed(query)

            # Search in Qdrant using query_points method
            search_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k,
                with_payload=True
            )

            # Format results
            formatted_results = []
            for result in search_results.points:
                formatted_results.append({
                    "id": result.id,
                    "content": result.payload.get("text", ""),
                    "metadata": result.payload,
                    "similarity_score": result.score
                })

            logger.info(f"Retrieved {len(formatted_results)} relevant chunks for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {e}")
            return []

    async def retrieve_and_format_context(self, query: str, top_k: int = 5):
        """
        Retrieve relevant text chunks and format them for context
        """
        results = await self.retrieve_relevant_chunks(query, top_k)

        # Format the context from the results
        formatted_context = "\n\n".join([result["content"] for result in results])

        # Extract sources
        sources = list(set([result["metadata"].get("source", "Unknown") for result in results]))

        return {
            "formatted_context": formatted_context,
            "sources": sources,
            "chunks": results
        }
