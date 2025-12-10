import openai
import os
from typing import Dict, List, Optional
import logging
import asyncio
from src.services.retrieval_service import RetrievalService
from src.services.validation import validate_question_data, validate_answer_data

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service for handling chat interactions with the RAG system
    """

    def __init__(self):
        """
        Initialize the chat service
        """
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.retrieval_service = RetrievalService()
        self.model = "gpt-3.5-turbo"  # Default model, could be configurable

    async def get_answer_general(self, question: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get an answer to a general question about the book content
        """
        try:
            # Validate the question
            question_data = {
                "id": "temp",
                "question_text": question,
                "question_type": "general"
            }
            validation_result = validate_question_data(question_data)
            if validation_result["errors"]:
                return None

            # Retrieve relevant content using the RAG system
            retrieval_result = self.retrieval_service.retrieve_and_format(
                query=question,
                top_k=5
            )

            # If no relevant content found, return a fallback message
            if not retrieval_result["chunks"]:
                return {
                    "answer": "I couldn't find relevant information in the book to answer your question. Please refer to the appropriate chapter.",
                    "source_chunks": [],
                    "confidence_score": 0.0
                }

            # Format the prompt with retrieved content
            prompt = self._build_prompt(
                question=question,
                context=retrieval_result["formatted_content"],
                is_selected_text_query=False
            )

            # Generate the answer using OpenAI
            answer = await self._call_openai(prompt)

            if not answer:
                return None

            # Return the result
            return {
                "answer": answer,
                "source_chunks": retrieval_result["sources"],
                "confidence_score": 0.9  # Placeholder confidence score
            }
        except Exception as e:
            logger.error(f"Error in get_answer_general: {e}")
            return None

    async def get_answer_selected(self, question: str, selected_text: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get an answer to a question about selected text
        """
        try:
            # Validate the question
            question_data = {
                "id": "temp",
                "question_text": question,
                "question_type": "selected_text",
                "selected_text": selected_text
            }
            validation_result = validate_question_data(question_data)
            if validation_result["errors"]:
                return None

            # For selected text queries, we use the selected text as context directly
            # but might also retrieve similar content for additional context
            retrieval_result = self.retrieval_service.retrieve_and_format(
                query=question,
                top_k=3
            )

            # Combine the selected text with any retrieved context
            context = f"Selected text: {selected_text}\n\nAdditional context: {retrieval_result['formatted_content']}"

            # Format the prompt with selected text and retrieved content
            prompt = self._build_prompt(
                question=question,
                context=context,
                is_selected_text_query=True
            )

            # Generate the answer using OpenAI
            answer = await self._call_openai(prompt)

            if not answer:
                return None

            # Return the result
            return {
                "answer": answer,
                "source_chunks": [selected_text[:100] + "..."] + retrieval_result["sources"],  # Include selected text snippet and other sources
                "confidence_score": 0.95  # Higher confidence for selected text queries
            }
        except Exception as e:
            logger.error(f"Error in get_answer_selected: {e}")
            return None

    def _build_prompt(self, question: str, context: str, is_selected_text_query: bool = False) -> str:
        """
        Build a prompt for the OpenAI model with the context and question
        """
        if is_selected_text_query:
            prompt = f"""
            The user has selected the following text from the book and has a question about it.

            Selected Text:
            {context}

            User's Question:
            {question}

            Please provide a helpful answer based on the book content that relates to the selected text.
            If the selected text doesn't directly answer the question, use the additional context provided.
            Always cite which parts of the book you're referencing in your answer.
            """
        else:
            prompt = f"""
            Based on the following book content, please answer the user's question.

            Context:
            {context}

            Question:
            {question}

            Provide an answer based only on the provided context.
            Always cite which parts of the book you're referencing in your answer.
            If the context doesn't contain sufficient information to answer the question,
            indicate that the user should refer to a specific part of the book.
            """

        return prompt

    async def _call_openai(self, prompt: str) -> Optional[str]:
        """
        Call the OpenAI API to generate a response
        """
        try:
            response = await self.client.chat.completions.async_create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided book content. Always cite which parts of the book you're referencing in your answer. If the provided context doesn't contain the information needed, indicate that the user should refer to the book directly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1000
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None