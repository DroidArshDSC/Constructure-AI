import json
from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------------------
# 1. Embeddings  (Used by ingestion + retrieval)
# ---------------------------------------------------------
def embed_text(texts: list[str]):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]


# ---------------------------------------------------------
# 2. RAG Chat Answer Generation
# ---------------------------------------------------------
def generate_answer(query: str, retrieved_chunks: list[dict]):
    # Build LLM context
    context_blocks = []
    citations = []

    for chunk in retrieved_chunks:
        context_blocks.append(
            f"[{chunk['file_name']} - page {chunk['page']}]\n{chunk['text']}"
        )
        citations.append({
            "file_name": chunk["file_name"],
            "page": chunk["page"]
        })

    context = "\n\n".join(context_blocks)

    prompt = f"""
You are a construction project assistant.
Answer the question using ONLY the context below.
If the answer does not appear in the context, say "Not found in the provided documents."

Context:
{context}

---
User question: {query}

Provide an answer with inline citations like (file:page).
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    answer = response.choices[0].message.content
    return answer, citations


# ---------------------------------------------------------
# 3. Structured Door Schedule Extraction (Optimized)
# ---------------------------------------------------------
def extract_schedule(chunks: list[dict]):
    """
    chunks: [
      { 'text': '...', 'file_name': '...', 'page': 12 },
      ...
    ]
    """

    context_blocks = []
    citations = []

    # Filter out huge noisy chunks (drawings generate long OCR text)
    filtered = [c for c in chunks if len(c["text"]) < 2200]

    for chunk in filtered:
        context_blocks.append(
            f"[{chunk['file_name']} - page {chunk['page']}]\n{chunk['text']}"
        )
        citations.append({
            "file_name": chunk["file_name"],
            "page": chunk["page"]
        })

    context = "\n\n".join(context_blocks)

    # LLM Extraction Prompt
    prompt = f"""
Extract the DOOR SCHEDULE from the construction drawing text.

Focus ONLY on the door schedule table (typically AE601).
Ignore general notes, drawing titles, legends, etc.

Return ONLY valid JSON in this exact format:

[
  {{
    "mark": "",
    "width_in": null,
    "height_in": null,
    "material": "",
    "fire_rating": "",
    "frame_type": "",
    "remarks": ""
  }}
]

Rules:
- If a value is missing, leave it "" or null.
- Do NOT include any text outside of the JSON.
- Do NOT summarize.
- Only return the structured table rows in JSON.

Context:
{context}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content

    # ---------------------------------------------------------
    # JSON Repair (ensures no model hallucinated whitespace/text)
    # ---------------------------------------------------------
    try:
        json_str = raw[raw.find("["): raw.rfind("]") + 1]
        data = json.loads(json_str)
    except Exception:
        data = []

    return {
        "data": data,
        "citations": citations
    }
