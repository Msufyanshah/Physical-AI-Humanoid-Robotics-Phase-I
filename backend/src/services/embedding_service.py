import openai
import os
from typing import List, Dict, Optional
import logging
from .validation import validate_code_example_data

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for creating embeddings of text content using OpenAI API
    """

    def __init__(self):
        """
        Initialize the embedding service
        """
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-ada-002"  # Default model for embeddings

    def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create an embedding for a single text
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return None

    def create_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Create embeddings for multiple texts
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            embeddings = [item.embedding for item in response.data]
            return embeddings
        except Exception as e:
            logger.error(f"Error creating multiple embeddings: {e}")
            return None

    def create_content_embedding(self, content: str, metadata: Dict) -> Optional[Dict]:
        """
        Create an embedding for content with additional metadata
        """
        embedding = self.create_embedding(content)
        if embedding:
            return {
                "vector": embedding,
                "content": content,
                "metadata": metadata
            }
        return None

    async def embed_chunk(self, content: str, metadata: Dict) -> Optional[Dict]:
        """
        Embed a content chunk and prepare it for storage
        """
        try:
            embedding = self.create_embedding(content)
            if not embedding:
                return None

            chunk_id = metadata.get("chunk_id") or self._generate_chunk_id()

            return {
                "id": chunk_id,
                "vector": embedding,
                "payload": {
                    "content": content,
                    "chapter_id": metadata.get("chapter_id"),
                    "module_id": metadata.get("module_id"),
                    "section_title": metadata.get("section_title"),
                    "word_count": metadata.get("word_count", 0),
                    "source_url": metadata.get("source_url", ""),
                    "start_pos": metadata.get("start_pos", 0),
                    "end_pos": metadata.get("end_pos", len(content))
                }
            }
        except Exception as e:
            logger.error(f"Error embedding chunk: {e}")
            return None

    def _generate_chunk_id(self) -> str:
        """
        Generate a unique chunk ID
        """
        import uuid
        return str(uuid.uuid4())