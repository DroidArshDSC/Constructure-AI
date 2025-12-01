from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ingest, chat, extract, eval

app = FastAPI(title="Constructure AI - Project Brain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(extract.router, prefix="/extract", tags=["Extraction"])
app.include_router(eval.router, prefix="/eval", tags=["Evaluation"])


@app.get("/")
def root():
    return {"status": "ok"}
