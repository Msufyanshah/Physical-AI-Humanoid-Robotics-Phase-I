import os
from dotenv import load_dotenv
load_dotenv()

import openai
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client if API key exists, otherwise set to None
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai_client = openai.OpenAI(api_key=openai_api_key)
    API_AVAILABLE = True
else:
    logger.warning("OPENAI_API_KEY not found in environment. API functionality will be simulated.")
    openai_client = None
    API_AVAILABLE = False


class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float


class ChatService:
    """
    Service for handling chat interactions with the RAG system
    """

    def __init__(self):
        """
        Initialize the chat service
        """
        self.model = "openai"
        self.client = openai_client
    
    async def get_answer_general(self, question: str, context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get an answer to a general question using the RAG system
        """
        try:
            if not API_AVAILABLE:
                # Return a simulated response when API is not available
                return {
                    "answer": f"SIMULATED: This would answer the question '{question}' using context: {context[:50]+'...' if context and len(context) > 50 else context}",
                    "sources": ["simulated_response"],
                    "confidence": 0.7  # Lower confidence for simulated responses
                }

            # Build the prompt with context if available
            if context:
                prompt = f"""
                Based on the following book content, please answer the user's question:

                Context:
                {context}

                Question:
                {question}

                Provide an answer based only on the provided context.
                Always cite which parts of the book you're referencing in your answer.
                If the context doesn't contain sufficient information to answer the question,
                indicate that the user should refer to a specific part of the book.
                """
            else:
                prompt = f"""
                Please answer the following question about robotics and AI:

                Question:
                {question}

                Provide an accurate and helpful answer based on your knowledge of robotics and AI.
                """

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use string directly instead of self.model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a robotics and AI textbook. Always provide accurate information based on the context provided. If you don't have enough information to answer, indicate what information would be needed."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            answer = response.choices[0].message.content.strip()

            return {
                "answer": answer,
                "sources": ["book_content"] if context else ["general_knowledge"],
                "confidence": 0.9  # Placeholder for now
            }

        except Exception as e:
            logger.error(f"Error in get_answer_general: {e}")
            return {
                "answer": "Error processing your request. Please try again later.",
                "sources": ["error"],
                "confidence": 0.0
            }
    
    async def get_answer_selected(self, question: str, selected_text: str) -> Optional[Dict[str, Any]]:
        """
        Get an answer about specific selected text
        """
        try:
            if not API_AVAILABLE:
                # Return a simulated response when API is not available
                return {
                    "answer": f"SIMULATED: This would answer the question '{question}' about the selected text: {selected_text[:50]}...",
                    "sources": ["simulated_response"],
                    "confidence": 0.7  # Lower confidence for simulated responses
                }

            prompt = f"""
            The user has selected the following text from the book and has a question about it.

            Selected Text:
            {selected_text}

            User's Question:
            {question}

            Please provide a helpful answer based on the book content that relates to the selected text.
            If the selected text doesn't directly answer the question, use the additional context provided.
            Always cite which parts of the book you're referencing in your answer.
            """

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use string directly instead of self.model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions about selected text from a robotics textbook. Always reference the specific parts of the book that relate to the answer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            answer = response.choices[0].message.content.strip()

            return {
                "answer": answer,
                "sources": ["selected_text_context"],
                "confidence": 0.95  # Higher confidence for selected text queries
            }

        except Exception as e:
            logger.error(f"Error in get_answer_selected: {e}")
            return {
                "answer": "Error processing your request about the selected text. Please try again later.",
                "sources": ["error"],
                "confidence": 0.0
            }