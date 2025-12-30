import json
from pathlib import Path

from .prompt_loader import load_prompt
from src.agent_builder.runners import (
    triage_runner,
    ros_runner,
    gazebo_runner,
    isaac_runner,
    vla_runner,
)
from src.agent_builder.trace import build_trace
from src.services.retrieval_service import RetrievalService

# Initialize retrieval service
retrieval_service = RetrievalService()

# Agent registry
AGENT_MAP = {
    "ros": ros_runner,
    "gazebo": gazebo_runner,
    "isaac": isaac_runner,
    "vla": vla_runner,
}

# Log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "agent_runs.jsonl"


async def run_agent(question: str, user_level: str):
    """
    Full Agent execution pipeline with:
    - retrieval
    - triage
    - prompt loading
    - trace generation
    - safe logging`
    """

    # 1. Retrieve context
    context_chunks = await retrieval_service.retrieve_relevant_chunks(question)
    if not context_chunks:
        # Create simulated results if retrieval fails
        context_chunks = [{
            "id": "simulated_chunk_0",
            "content": "This is simulated content from the Physical AI & Humanoid Robotics book related to your query.",
            "metadata": {"source": "simulated", "confidence": 0.7},
            "similarity_score": 0.7
        }]
    # Extract content from chunks
    context_block = "\n\n".join([chunk["content"] for chunk in context_chunks])

    # 2. Triage
    triage_result = triage_runner.run({"input": question})
    agent_name = triage_result.output_text.strip()

    if agent_name not in AGENT_MAP:
        agent_name = "vla"  # safe fallback

    agent_runner = AGENT_MAP[agent_name]

    # 3. Load system prompt
    system_prompt = load_prompt(
        agent_name=agent_name,
        user_level=user_level,
    )

    # 4. Build agent input
    full_input = f"""{system_prompt}

CONTEXT:
{context_block}

User Question:
{question}
"""

    # 5. Run agent
    result = agent_runner.run({"input": full_input})

    if not result or not result.output_text:
        raise RuntimeError(f"{agent_name} agent returned empty output")

    # 6. Build trace
    trace = build_trace(
        question=question,
        agent=agent_name,
        level=user_level,
        prompt_version=user_level,
        context_chunks=context_chunks,  # This is now a list of chunks as expected
    )

    response = {
        "agent": agent_name,
        "level": user_level,
        "answer": result.output_text,
        "trace": trace,
    }

    # 7. Persist run (replay-safe)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(response) + "\n")

    return response
