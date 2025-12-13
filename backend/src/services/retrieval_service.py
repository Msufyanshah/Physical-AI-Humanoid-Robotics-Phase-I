import os
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.services.embedding_service import EmbeddingService

# Try to import Qdrant components
QDRANT_AVAILABLE = True
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("Qdrant client not available. Vector retrieval functionality will be simulated.")

class RetrievalService:
    """
    Service for retrieving relevant information using vector similarity
    """

    def __init__(self):
        """
        Initialize the retrieval service
        """
        # Check if Qdrant is available
        if QDRANT_AVAILABLE and os.getenv("QDRANT_URL") and os.getenv("QDRANT_API_KEY"):
            try:
                # Initialize Qdrant client
                self.qdrant_client = QdrantClient(
                    url=os.getenv("QDRANT_URL"),
                    api_key=os.getenv("QDRANT_API_KEY")
                )

                # Collection name for our book content
                self.collection_name = "book_content_chunks"

                # Initialize embedding service
                self.embedding_service = EmbeddingService()

                # Create the collection if it doesn't exist
                self._initialize_collection()

                self.service_available = True
                logger.info("Retrieval service initialized with Qdrant")

            except Exception as e:
                logger.error(f"Could not connect to Qdrant: {e}")
                self.service_available = False
        else:
            logger.warning("Qdrant not available, initializing with simulated functionality")
            self.service_available = False
            self.qdrant_client = None
            self.collection_name = "book_content_chunks"
            self.embedding_service = EmbeddingService()
    
    def _initialize_collection(self):
        """
        Initialize the Qdrant collection if it doesn't exist
        """
        if not self.service_available:
            logger.warning("Qdrant not available, skipping collection initialization")
            return

        try:
            # Check if collection exists
            self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception:
            # Create collection with appropriate vector size for our embedding model
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),  # Ada-002 gives 1536-dim vectors
            )
            logger.info(f"Created collection '{self.collection_name}'")

    async def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve the most relevant content chunks for a query
        """
        if not self.service_available:
            # Simulate retrieval when Qdrant is not available
            logger.warning(f"Qdrant not available, simulating retrieval for query: {query[:50]}...")
            # Return dummy results
            simulated_results = []
            for i in range(min(top_k, 3)):  # Simulate up to 3 results
                simulated_results.append({
                    "id": f"simulated_chunk_{i}",
                    "content": f"This is simulated content related to your query: '{query[:30]}...'",
                    "metadata": {"source": "simulated", "confidence": 0.7},
                    "similarity_score": 0.7 - (i * 0.1)  # Decreasing score
                })
            return simulated_results

        try:
            # Create embedding for the query
            query_embedding = await self.embedding_service.create_embedding(query)
            if not query_embedding:
                logger.error("Could not create embedding for query")
                return None

            # Search in Qdrant for similar vectors
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )

            # Format results
            relevant_chunks = []
            for result in search_results:
                chunk = {
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "similarity_score": result.score
                }
                relevant_chunks.append(chunk)

            return relevant_chunks

        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {e}")
            # Return simulated results in case of error
            simulated_results = []
            for i in range(2):  # Simulate 2 results as fallback
                simulated_results.append({
                    "id": f"fallback_chunk_{i}",
                    "content": f"Fallback content related to your query: '{query[:30]}...'",
                    "metadata": {"source": "fallback", "confidence": 0.5},
                    "similarity_score": 0.5
                })
            return simulated_results
    
    async def store_content_chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a content chunk in the vector database
        """
        if not self.service_available:
            # Simulate storage when Qdrant is not available
            logger.warning(f"Qdrant not available, simulating storage for content: {content[:50]}...")
            # Simulate success
            chunk_id = f"simulated_chunk_{abs(hash(content[:50]))}"
            logger.info(f"Simulated storing chunk {chunk_id}")
            return True

        try:
            # Create an embedding for the content
            embedding = await self.embedding_service.create_embedding(content)
            if not embedding:
                logger.error("Could not create embedding for content chunk")
                return False

            # Generate a unique ID for the chunk
            chunk_id = f"chunk_{abs(hash(content[:50]))}"  # Simple ID generation based on content

            # Prepare the point to insert
            point = models.PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata or {},
                    "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                }
            )

            # Upsert the point into the collection
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            logger.info(f"Stored chunk {chunk_id} in collection")
            return True

        except Exception as e:
            logger.error(f"Error storing content chunk: {e}")
            return False
    
    async def retrieve_and_format_context(self, query: str, top_k: int = 5) -> Optional[Dict[str, Any]]:
        """
        Retrieve relevant chunks and format them as context for the LLM
        """
        try:
            # Get relevant chunks
            relevant_chunks = await self.retrieve_relevant_chunks(query, top_k)
            if not relevant_chunks:
                return None

            # Format as context string
            context_parts = []
            sources = []

            for chunk in relevant_chunks:
                context_parts.append(f"Source: {chunk.get('metadata', {}).get('source', 'unknown')}\n{chunk['content']}")
                sources.append(chunk['id'])

            formatted_context = "\n\n".join(context_parts)

            return {
                "formatted_context": formatted_context,
                "retrieved_chunks": relevant_chunks,
                "sources": sources
            }

        except Exception as e:
            logger.error(f"Error retrieving and formatting context: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the stored content
        """
        if not self.service_available:
            # Return simulated stats when Qdrant is not available
            logger.warning("Qdrant not available, returning simulated statistics")
            return {
                "vectors_count": 0,
                "collection_name": self.collection_name,
                "status": "simulated"
            }

        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "vectors_count": collection_info.points_count,
                "collection_name": self.collection_name,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error getting collection statistics: {e}")
            return {"error": str(e)}