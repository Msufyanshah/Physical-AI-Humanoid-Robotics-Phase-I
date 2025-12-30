from src.agent_builder.base import BaseAgentRunner

class AgentBuilderRunner(BaseAgentRunner):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    def run(self, input: dict):
        """
        This will later call:
        - OpenAI Responses API
        - or Agent Builder SDK
        """
        text = input.get("input", "")

        if self.agent_name == "triage":
            # For triage, analyze the input to determine appropriate agent
            agent = self.triage_question(text)
            result_text = agent
        else:
            result_text = f"[{self.agent_name.upper()} AGENT] {text}"

        return type(
            "Result",
            (),
            {"output_text": result_text}
        )()

    def triage_question(self, question: str) -> str:
        """
        Analyze a question to determine which agent should handle it
        """
        question_lower = question.lower()

        # Keyword-based triage - ordered by specificity
        if any(keyword in question_lower for keyword in ["vision", "language", "action", "vla", "voice", "whisper", "vlm", "multimodal"]):
            return "vla"
        elif any(keyword in question_lower for keyword in ["isaac", "sim", "nvidia", "perception", "learning", "training"]):
            return "isaac"
        elif any(keyword in question_lower for keyword in ["gazebo", "simulation", "physics", "world", "sdf", "collision"]):
            return "gazebo"
        elif any(keyword in question_lower for keyword in ["ros", "node", "topic", "service", "action", "rclpy", "launch"]):
            return "ros"
        else:
            # Default to a more general agent if uncertain
            return "ros"  # Default fallback
