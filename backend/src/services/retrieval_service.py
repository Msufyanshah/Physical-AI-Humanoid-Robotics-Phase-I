from typing import List, Dict, Optional
import logging
from .vector_store import QdrantService
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Service for retrieving relevant content chunks based on user queries
    """
    
    def __init__(self):
        """
        Initialize the retrieval service
        """
        self.vector_store = QdrantService()
        self.embedding_service = EmbeddingService()
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve the most relevant content chunks for a given query
        """
        try:
            # Create embedding for the query
            query_embedding = self.embedding_service.create_embedding(query)
            if not query_embedding:
                logger.error("Failed to create embedding for query")
                return []
            
            # Search for similar content in the vector store
            results = self.vector_store.search_vectors(
                query_vector=query_embedding,
                top_k=top_k,
                filters=filters
            )
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {e}")
            return []
    
    def retrieve_chunks_by_module(self, query: str, module_id: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks specifically for a given module
        """
        filters = {"module_id": module_id}
        return self.retrieve_relevant_chunks(query, top_k, filters)
    
    def retrieve_chunks_by_chapter(self, query: str, chapter_id: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks specifically for a given chapter
        """
        filters = {"chapter_id": chapter_id}
        return self.retrieve_relevant_chunks(query, top_k, filters)
    
    def rerank_chunks(self, query: str, chunks: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Rerank chunks based on semantic relevance to the query and other heuristics
        """
        # This is a simple implementation - in a real scenario, you might use
        # more sophisticated reranking approaches
        try:
            # Sort by similarity score first (which is already done by Qdrant)
            # Then could apply other heuristics if needed
            reranked_chunks = sorted(chunks, key=lambda x: x['score'], reverse=True)
            
            # Apply additional heuristics if needed:
            # - Prefer chunks with higher token density if quality correlates with it
            # - Prefer chunks with certain keywords
            # - Balance diversity and relevance
            
            return reranked_chunks[:top_k]
        except Exception as e:
            logger.error(f"Error reranking chunks: {e}")
            return chunks[:top_k]
    
    def format_retrieved_content(self, chunks: List[Dict]) -> str:
        """
        Format retrieved content for use in prompt
        """
        formatted_content = []
        for chunk in chunks:
            payload = chunk.get('payload', {})
            content = payload.get('content', '')
            source = payload.get('section_title', 'Unknown Section')
            formatted_content.append(f"Source: {source}\nContent: {content}\n")
        
        return "\n".join(formatted_content)
    
    def retrieve_and_format(self, query: str, top_k: int = 5) -> Dict:
        """
        Retrieve relevant chunks and format them for LLM consumption
        """
        try:
            # Retrieve relevant chunks
            raw_chunks = self.retrieve_relevant_chunks(query, top_k)
            
            # Rerank if needed
            reranked_chunks = self.rerank_chunks(query, raw_chunks, top_k)
            
            # Format the content
            formatted_content = self.format_retrieved_content(reranked_chunks)
            
            return {
                "chunks": reranked_chunks,
                "formatted_content": formatted_content,
                "sources": [chunk.get('id') for chunk in reranked_chunks]
            }
        except Exception as e:
            logger.error(f"Error in retrieve_and_format: {e}")
            return {
                "chunks": [],
                "formatted_content": "",
                "sources": []
            }