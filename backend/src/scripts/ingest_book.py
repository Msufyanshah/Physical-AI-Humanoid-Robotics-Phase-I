from pathlib import Path
import asyncio
from src.services.retrieval_service import RetrievalService

# Resolve project root
BASE_DIR = Path(__file__).resolve().parents[3]

DOCS_DIR = BASE_DIR / "frontend" / "docs"

if not DOCS_DIR.exists():
    raise FileNotFoundError(f"Docs directory not found: {DOCS_DIR}")

def read_all_docs():
    documents = []
    for file in DOCS_DIR.rglob("*"):
        if file.suffix.lower() in {".txt", ".md"}:
            documents.append({
                "path": str(file),
                "content": file.read_text(encoding="utf-8")
            })
    return documents

def chunk_document(content: str, max_chunk_size: int = 2000) -> list:
    """
    Split a large document into smaller chunks.
    This is a simple implementation that splits by newlines respecting max_chunk_size.
    """
    if len(content) <= max_chunk_size:
        return [content]

    chunks = []
    current_chunk = ""

    # Split content by paragraphs or sentences
    paragraphs = content.split('\n\n')

    for paragraph in paragraphs:
        if len(paragraph) > max_chunk_size:
            # If the paragraph itself is too large, split it further (by sentences)
            sentences = paragraph.split('. ')
            current_sub_chunk = ""

            for sentence in sentences:
                test_chunk = current_sub_chunk + ". " + sentence if current_sub_chunk else sentence

                if len(test_chunk) <= max_chunk_size:
                    current_sub_chunk = test_chunk
                else:
                    if current_sub_chunk:
                        chunks.append(current_sub_chunk)
                    current_sub_chunk = sentence if len(sentence) <= max_chunk_size else sentence[:max_chunk_size]

            if current_sub_chunk:
                chunks.append(current_sub_chunk)
        else:
            test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph

            if len(test_chunk) <= max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

async def ingest():
    retrieval = RetrievalService()
    docs = read_all_docs()

    print(f"Ingesting {len(docs)} documents...")

    for doc in docs:
        # Split large documents into smaller chunks
        chunks = chunk_document(doc["content"], max_chunk_size=2000)

        for i, chunk in enumerate(chunks):
            # Add chunk number to metadata for reference
            chunk_metadata = {
                "source": doc["path"],
                "chunk_index": i,
                "chunk_count": len(chunks)
            }

            await retrieval.store_content_chunk(
                content=chunk,
                metadata=chunk_metadata
            )

    print("Ingestion completed successfully.")

if __name__ == "__main__":
    asyncio.run(ingest())
