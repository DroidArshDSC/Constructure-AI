from fastapi import APIRouter
from pydantic import BaseModel
from app.core.vectorstore import search_chunks
from app.core.llm import generate_answer

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/")
async def chat(req: ChatRequest):
    retrieved = search_chunks(req.query)
    answer, citations = generate_answer(req.query, retrieved)
    return {"answer": answer, "citations": citations}
