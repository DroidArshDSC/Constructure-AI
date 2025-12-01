import chromadb
from app.core.llm import embed_text
from app.core.config import CHROMA_DIR

# ---------------------------------------------------------
# Create or load Chroma persistent client
# ---------------------------------------------------------
client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_or_create_collection(
    name="project_chunks",
    metadata={"hnsw:space": "cosine"}
)


# ---------------------------------------------------------
# Insert Chunks (during ingestion)
# ---------------------------------------------------------
def insert_chunks(chunks: list[dict]):
    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [
        {"page": c["page"], "file_name": c["file_name"]}
        for c in chunks
    ]

    embeddings = embed_text(texts)

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )


# ---------------------------------------------------------
# STANDARD SEARCH (used for /chat)
# ---------------------------------------------------------
def search_chunks(query: str, k: int = 5):
    q_embed = embed_text([query])[0]
    results = collection.query(
        query_embeddings=[q_embed],
        n_results=k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Normalize to consistent format
    return [
        {
            "text": doc,
            "file_name": meta["file_name"],
            "page": meta["page"]
        }
        for doc, meta in zip(documents, metadatas)
    ]


# ---------------------------------------------------------
# OPTIMIZED KEYWORD-BASED SEARCH (for door schedules)
# ---------------------------------------------------------
def search_chunks_by_keyword(keyword: str, k: int = 8):
    """
    Smart retrieval for construction drawings:
    - Fetch top-K candidates via embedding similarity.
    - Filter results to pages that likely contain schedules
      (AE6xx sheets, 'DOOR', 'SCHEDULE', tabular OCR text).
    - Falls back safely if filtering removes all chunks.
    """

    q_embed = embed_text([keyword])[0]

    results = collection.query(
        query_embeddings=[q_embed],
        n_results=k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    candidates = [
        {
            "text": doc,
            "file_name": meta["file_name"],
            "page": meta["page"]
        }
        for doc, meta in zip(documents, metadatas)
    ]

    # ---------------------------------------------------------
    # Filtering Logic (AE601, DOOR SCHEDULE HEURISTICS)
    # ---------------------------------------------------------
    filtered = []
    for chunk in candidates:
        text = chunk["text"].upper()

        # Architectural schedule signals
        if (
            "AE601" in text or
            "DOOR" in text or
            "SCHEDULE" in text or
            "TYPE" in text or
            "FRAME" in text or
            "WIDTH" in text or
            "HEIGHT" in text
        ):
            filtered.append(chunk)

    # Fallback: if no chunks match heuristic, return original
    if not filtered:
        return candidates

    return filtered
