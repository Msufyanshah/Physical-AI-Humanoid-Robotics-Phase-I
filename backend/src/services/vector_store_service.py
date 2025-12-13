import os
from typing import List, Dict, Any, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service for managing vector storage and retrieval using Qdrant
    """
    
    def __init__(self, collection_name: str = "book_content_chunks"):
        """
        Initialize the vector store service
        """
        # Get Qdrant credentials from environment
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_url and qdrant_api_key:
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                prefer_grpc=True
            )
            self.API_AVAILABLE = True
        else:
            logger.warning("QDRANT credentials not found. Vector store functionality will be simulated.")
            self.client = None
            self.API_AVAILABLE = False
            
        self.collection_name = collection_name
        self.dimension = 1536  # Dimension for text-embedding-ada-002
        
        if self.API_AVAILABLE:
            # Initialize the collection
            self._initialize_collection()
    
    def _initialize_collection(self):
        """
        Initialize the Qdrant collection if it doesn't exist
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE)
            )
            logger.info(f"Created collection '{self.collection_name}' with {self.dimension}-dimension vectors")
    
    async def store_embedding(self, 
                              text_chunk: str, 
                              embedding: List[float], 
                              metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a text chunk with its embedding in the vector store
        """
        if not self.API_AVAILABLE:
            logger.warning("Vector store not available, simulating store operation")
            return True  # Simulate success
        
        try:
            # Generate a unique ID for this chunk
            import hashlib
            chunk_id = hashlib.md5((text_chunk + str(embedding[0])).encode()).hexdigest()
            
            # Prepare the point to insert
            point = models.PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "text_chunk": text_chunk,
                    "metadata": metadata or {},
                    "timestamp": __import__('datetime').datetime.datetime.utcnow().isoformat()
                }
            )
            
            # Upsert the point into the collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Stored embedding for chunk ID: {chunk_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            return False
    
    async def retrieve_similar(self, 
                               query_embedding: List[float], 
                               top_k: int = 5, 
                               filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve the most similar text chunks to a query embedding
        """
        if not self.API_AVAILABLE:
            logger.warning("Vector store not available, returning empty results")
            return []
        
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
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filters,
                limit=top_k,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "text_chunk": result.payload.get("text_chunk", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "similarity_score": result.score
                })
            
            logger.info(f"Retrieved {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving similar embeddings: {e}")
            return []
    
    async def retrieve_by_metadata(self, 
                                   metadata_filters: Dict[str, Any], 
                                   top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve embeddings based on metadata filters
        """
        if not self.API_AVAILABLE:
            logger.warning("Vector store not available, returning empty results")
            return []
        
        try:
            # Create filter conditions
            filter_conditions = []
            for key, value in metadata_filters.items():
                filter_conditions.append(
                    models.FieldCondition(
                        key=f"metadata.{key}",
                        match=models.MatchValue(value=value)
                    )
                )
            
            search_filter = models.Filter(must=filter_conditions)
            
            # Search with the filter
            results = self.client.search(
                collection_name=self.collection.name,
                query_filter=search_filter,
                limit=top_k,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "text_chunk": result.payload.get("text_chunk", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "similarity_score": result.score
                })
            
            logger.info(f"Retrieved {len(formatted_results)} chunks by metadata")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving by metadata: {e}")
            return []
    
    async def delete_by_id(self, chunk_id: str) -> bool:
        """
        Delete a specific chunk by ID
        """
        if not self.API_AVAILABLE:
            logger.warning("Vector store not available, simulating delete")
            return True  # Simulate success
        
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[chunk_id]
                )
            )
            
            logger.info(f"Deleted chunk with ID: {chunk_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chunk: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        """
        if not self.API_AVAILABLE:
            logger.warning("Vector store not available, returning simulated stats")
            return {
                "collection_name": self.collection_name,
                "point_count": 0,
                "status": "simulated"
            }
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "point_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}