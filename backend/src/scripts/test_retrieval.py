import asyncio
from src.services.retrieval_service import RetrievalService

async def test():
    retrieval = RetrievalService()
    result = await retrieval.retrieve_and_format_context(
        query="Explain Isaac Asimov's view on robotics",
        top_k=3
    )

    print("\n--- CONTEXT ---\n")
    print(result["formatted_context"])
    print("\n--- SOURCES ---\n")
    print(result["sources"])

asyncio.run(test())
