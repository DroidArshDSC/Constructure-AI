from fastapi import APIRouter, UploadFile, File
from app.core.chunker import extract_text_and_chunks
from app.core.vectorstore import insert_chunks

router = APIRouter()

@router.post("/")
async def ingest_files(files: list[UploadFile] = File(...)):
    results = []
    for f in files:
        text, chunks = extract_text_and_chunks(f)
        insert_chunks(chunks)
        results.append({"file": f.filename, "chunks": len(chunks)})
    return {"status": "ok", "ingested": results}