import os
import openai
from typing import List, Dict, Any, Optional
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client if API key exists, otherwise set to None
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    client = openai.OpenAI(api_key=openai_api_key)
    API_AVAILABLE = True
else:
    logger.warning("OPENAI_API_KEY not found in environment. Embedding functionality will be simulated.")
    client = None
    API_AVAILABLE = False

class EmbeddingService:
    """
    Service for handling text embeddings
    """
    
    def __init__(self):
        """
        Initialize the embedding service
        """
        self.model = "text-embedding-ada-002"
        self.client = client
        
    async def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for a single text
        """
        if not API_AVAILABLE:
            # Simulate embedding when API is not available
            # In real implementation, we might have a local model or use a different approach
            logger.warning("API not available, simulating embedding for: {}".format(text[:50]))
            # Return a dummy embedding of appropriate size (for ada-002: 1536 dimensions)
            return [0.01] * 1536

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )

            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return None
    
    async def create_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Create embeddings for multiple texts
        """
        if not API_AVAILABLE:
            # Simulate embeddings for multiple texts when API is not available
            logger.warning(f"API not available, simulating embeddings for {len(texts)} texts")
            # Return dummy embeddings for each text
            return [[0.01] * 1536 for _ in texts]

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            return embeddings

        except Exception as e:
            logger.error(f"Error creating multiple embeddings: {e}")
            return None
    
    async def embed_text_chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Embed a text chunk with associated metadata
        """
        try:
            embedding = await self.create_embedding(text)
            if embedding is None:
                return None

            chunk_id = f"chunk_{abs(hash(text[:50]))}"  # Simple ID generation using hash of text

            return {
                "id": chunk_id,
                "embedding": embedding,
                "text": text,
                "metadata": metadata or {},
                "length": len(text)
            }

        except Exception as e:
            logger.error(f"Error embedding text chunk: {e}")
            return None
    
    async def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors
        """
        try:
            # Convert to numpy arrays
            arr1 = np.array(vec1)
            arr2 = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0