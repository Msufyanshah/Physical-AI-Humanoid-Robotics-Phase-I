from openai import OpenAI
import os
import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.model = "text-embedding-3-small"
        self.embedding_dim = 1536

        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

        if not self.client:
            logger.warning("OPENAI_API_KEY not found. Embeddings will be simulated.")

    def embed(self, text: str) -> List[float]:
        if not self.client:
            return [0.01] * self.embedding_dim

        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
