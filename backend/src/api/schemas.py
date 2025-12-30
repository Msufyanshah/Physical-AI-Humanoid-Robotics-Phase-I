from pydantic import BaseModel
from typing import Any, Dict


class AskAgentRequest(BaseModel):
    question: str
    user_level: str


class AskAgentResponse(BaseModel):
    agent: str
    level: str
    answer: str
    trace: Dict[str, Any]
