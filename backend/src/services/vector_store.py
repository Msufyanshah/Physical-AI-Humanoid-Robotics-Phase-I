from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from typing import List, Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)

class QdrantService:
    """
    Service for managing interactions with Qdrant vector database
    for storing and retrieving book content embeddings
    """
    
    def __init__(self, collection_name: str = "book_content_chunks"):
        """
        Initialize Qdrant service
        """
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            # If running locally, you might use:
            # host="localhost",
            # port=6333
        )
        self._initialize_collection()
    
    def _initialize_collection(self):
        """
        Initialize the collection with proper vector parameters
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} already exists")
        except Exception:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),  # Assuming OpenAI embeddings
            )
            logger.info(f"Created collection {self.collection_name}")
    
    def create_collection(self) -> bool:
        """
        Create a new collection with the proper schema
        """
        try:
            if not self.collection_exists():
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),  # Assuming OpenAI embeddings
                )
                logger.info(f"Created collection {self.collection_name}")
                return True
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                return False
        except Exception as e:
            logger.error(f"Error creating collection {self.collection_name}: {e}")
            return False
    
    def collection_exists(self) -> bool:
        """
        Check if the collection exists
        """
        try:
            self.client.get_collection(self.collection_name)
            return True
        except Exception:
            return False
    
    def upsert_vectors(self, points: List[Dict]) -> bool:
        """
        Upsert vectors to the collection
        Each point should contain: id, vector, payload
        Payload should include: content, chapter_id, module_id, etc.
        """
        try:
            # Prepare points for upsert
            qdrant_points = []
            for point in points:
                qdrant_points.append(models.PointStruct(
                    id=point["id"],
                    vector=point["vector"],
                    payload=point["payload"]  # Contains content, metadata, etc.
                ))
            
            # Upsert the points
            self.client.upsert(
                collection_name=self.collection_name,
                points=qdrant_points
            )
            
            logger.info(f"Upserted {len(points)} vectors to collection {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error upserting vectors to collection {self.collection_name}: {e}")
            return False
    
    def search_vectors(self, query_vector: List[float], top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar vectors in the collection
        """
        try:
            # Prepare filters if provided
            search_filters = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )
                if filter_conditions:
                    search_filters = models.Filter(must=filter_conditions)
            
            # Perform the search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=search_filters,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            logger.info(f"Found {len(formatted_results)} results for search query")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching vectors in collection {self.collection_name}: {e}")
            return []
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict]:
        """
        Get a specific chunk by its ID
        """
        try:
            records = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id],
                with_payload=True,
                with_vectors=False
            )
            
            if records:
                record = records[0]
                return {
                    "id": record.id,
                    "payload": record.payload
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving chunk with ID {chunk_id}: {e}")
            return None