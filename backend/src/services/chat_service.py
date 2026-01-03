import os
import logging
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from pydantic import BaseModel

from src.services.retrieval_service import RetrievalService

import openai

load_dotenv()

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# OpenAI setup
# ------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    API_AVAILABLE = True
else:
    logger.warning("OPENAI_API_KEY not found. API calls disabled.")
    client = None
    API_AVAILABLE = False

# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float


# ------------------------------------------------------------------
# Chat Service
# ------------------------------------------------------------------
class ChatService:
    """
    Handles RAG-based chat responses
    """

    def __init__(self):
        self.client = client
        self.retrieval_service = RetrievalService()

    async def ask(self, question: str) -> Dict[str, Any]:
        """
        Main RAG-powered chat entry point
        """

        # 1. Retrieve context
        retrieval_result = await self.retrieval_service.retrieve_and_format_context(question)
        context = retrieval_result["formatted_context"]
        sources = retrieval_result["sources"]

        # 2. Enforce NO-HALLUCINATION
        if not context.strip():
            return {
                "answer": "I don't know based on the provided course materials.",
                "sources": [],
                "confidence": 0.0
            }

        # 3. Build strict RAG prompt
        prompt = f"""
You are a course assistant for the Physical AI & Humanoid Robotics program.

RULES:
- Answer ONLY from the provided context
- If the answer is not explicitly present, say "I don't know"
- Do not use outside knowledge

CONTEXT:
{context}

QUESTION:
{question}
"""

        # 4. API unavailable fallback
        if not API_AVAILABLE:
            return {
                "answer": "API unavailable. Unable to generate answer.",
                "sources": sources,
                "confidence": 0.0
            }

        # 5. LLM call
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a strict RAG-based assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=800
            )

            answer = response.choices[0].message.content.strip()

            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.9
            }

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "answer": "Error generating response.",
                "sources": sources,
                "confidence": 0.0
            }

    async def get_answer_general(self, question: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get answer for a general question about the book content
        """
        return await self.ask(question)

    async def get_answer_selected(self, question: str, selected_text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get answer for a question about selected text in the book
        """
        # Combine the selected text with the question for better context
        full_context = f"Selected text: {selected_text}\n\nQuestion about the selected text: {question}"
        return await self.ask(full_context)
