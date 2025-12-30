import json  
from typing import Dict, Any, Callable
import os
import sys


class ChatService:
    """
    Chat service that acts as a thin adapter between CLI/UI and backend RAG agents
    """

    def __init__(self):
        # ChatKit must not own prompts, workflows, or RAG logic
        self._run_agent_fn = None

    def _get_run_agent(self) -> Callable:
        """
        Lazy-load backend run_agent to avoid import / path issues
        """
        if self._run_agent_fn is None:
            backend_src_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "backend",
                "src",
            )

            if backend_src_path not in sys.path:
                sys.path.insert(0, backend_src_path)

            from rag.agent_adapter import run_agent

            self._run_agent_fn = run_agent

        return self._run_agent_fn

    def chat_with_agent(
        self,
        question: str,
        agent_type: str = "triage",
        user_level: str = "v0",
    ) -> Dict[str, Any]:
        """
        Send a question to backend RAG system and return response
        """

        try:
            run_agent = self._get_run_agent()

            # Backend handles triage + agent selection internally
            result = run_agent(
                question=question,
                user_level=user_level,
            )

            return {
                "agent": result.get("agent", "triage"),
                "user_level": user_level,
                "question": question,
                "response": result.get("answer", "No response generated"),
                "confidence": result.get("confidence", 0.8),
                "followup_suggestions": [
                    "Ask a more specific question",
                    "Request examples",
                    "Ask about related concepts",
                ],
            }

        except Exception as e:
            return {
                "agent": "error",
                "user_level": user_level,
                "question": question,
                "response": f"Backend error: {str(e)}",
                "confidence": 0.0,
                "followup_suggestions": [],
            }

    def get_agent_list(self) -> Dict[str, Any]:
        """
        Static description for CLI help (not authoritative)
        """
        return {
            "agents": {
                "vla": {
                    "description": "Vision-Language-Action systems",
                    "capabilities": [
                        "Language grounding",
                        "Action planning",
                        "Multimodal reasoning",
                    ],
                },
                "ros": {
                    "description": "ROS 2 robotics development",
                    "capabilities": [
                        "Nodes and topics",
                        "Launch systems",
                        "Robot middleware",
                    ],
                },
                "gazebo": {
                    "description": "Simulation and physics",
                    "capabilities": [
                        "World simulation",
                        "Sensors",
                        "Robot dynamics",
                    ],
                },
                "isaac": {
                    "description": "AI and perception",
                    "capabilities": [
                        "Computer vision",
                        "Synthetic data",
                        "Deep learning",
                    ],
                },
            },
            "user_levels": {
                "v0": "Beginner-friendly explanations",
                "v1": "Expert-level technical depth",
            },
        }
