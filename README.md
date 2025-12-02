# 🏗️ Constructure AI — Applied LLM Engineer Technical Project

A production-ready Retrieval-Augmented Generation (RAG) system built for construction-domain document intelligence.
This implementation ingests project PDFs (plans, wage determinations, schedules), embeds them into a vector store, and exposes APIs for Q&A and structured extraction.

Designed for real-world reliability, LLM-safe prompting, and fast deployment across a containerized backend and a Vite/React frontend.

## 🚀 Architecture Overview

### Backend (FastAPI)
- PDF ingestion + text chunking
- Embedding generation (OpenAI)
- Vector search (ChromaDB)
- RAG pipeline (context assembly + LLM answer generation)
- Structured extraction endpoint (door schedules)
- Deployed on Render via Docker

### Frontend (Vite + React + Tailwind)
- File upload UI
- Chat interface
- Structured extraction viewer
- Status feedback, toast notifications
- Deployed on Vercel

### Storage
- Chroma persistent store
- Mounted disk on Render


## ⚙️ Features

### PDF Ingestion
- Handles multi-page PDFs
- Adaptive chunking to avoid token overflow
- Embedding + upsert into Chroma
- Returns chunk count for transparency

### RAG Chat
- Query → retrieve top-k chunks → answer
- Inline citations: (file:page)
- Context-bounded prompting to avoid hallucinations

### Door Schedule Extraction
- Pulls table-like schedule information from construction drawings
- Uses targeted retrieval + structured LLM output schema

### Frontend UX
- File picker + upload progress
- Session history
- Chat terminal with skeleton loaders
- Extraction results in scrollable JSON viewer
- Slash-safe API routing (no double slash failures)

## Local Development

### Backend
```bash
cd backend/app
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
uvicorn app.main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

### Frontend
```bash
cd constructure-frontend
npm install
npm run dev
```

Frontend runs at: `http://127.0.0.1:5173`

## Operational Notes
- Chunking tuned to avoid OpenAI embedding length limits
- Memory-safe ingestion (large PDFs processed in batches)
- Normalized API routing (prevents `//ingest/` double-slash errors)
- CORS enabled for cross-origin frontend access

## Summary
Constructure AI delivers a clean, production-grade RAG stack capable of handling real construction documentation.
The system is architected for reliability, fast iteration, and enterprise-grade performance — aligned with the expectations of an Applied LLM Engineer assignment.