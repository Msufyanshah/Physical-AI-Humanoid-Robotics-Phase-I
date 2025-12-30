from datetime import datetime

def build_trace( 
    question: str,
    agent: str,
    level: str,
    prompt_version: str,
    context_chunks: list[str],
):
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "agent": agent,
        "level": level,
        "prompt_version": prompt_version,
        "context_chunks_used": len(context_chunks),
    }
