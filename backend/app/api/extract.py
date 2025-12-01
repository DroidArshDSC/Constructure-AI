from fastapi import APIRouter
from app.core.vectorstore import search_chunks_by_keyword
from app.core.llm import extract_schedule

router = APIRouter()


# ---------------------------------------------------------
# Door Schedule Extraction Endpoint
# ---------------------------------------------------------
@router.post("/door-schedule")
async def door_schedule():
    """
    Extracts the door schedule from the indexed construction drawings.
    Uses optimized retrieval to target AE601 and schedule-related pages.
    """

    # Retrieve chunks relevant to the "door schedule"
    chunks = search_chunks_by_keyword("door schedule", k=8)

    # Soft filter for extremely long OCR text (helps speed + accuracy)
    chunks = [c for c in chunks if len(c["text"]) < 2500]

    # Extract structured schedule from filtered chunks
    result = extract_schedule(chunks)

    return result
