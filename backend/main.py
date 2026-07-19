import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db
import rag_engine
from config import DOCUMENTS_DIR, USE_LOCAL_FINETUNED_MODEL

if USE_LOCAL_FINETUNED_MODEL:
    import local_llm_client as llm
else:
    import gemini_client as llm

app = FastAPI(title="Jarvis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db.init_db()
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    # Build the RAG index once at startup if it doesn't exist yet
    rag_engine.build_index_from_documents()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    sources: list[str]


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "Message cannot be empty")

    session_id = req.session_id or str(uuid.uuid4())
    db.ensure_session(session_id, req.message)

    history = db.get_history(session_id)
    retrieved = rag_engine.retrieve(req.message, top_k=4)

    reply = llm.generate_reply(req.message, retrieved, history)

    db.save_message(session_id, "user", req.message)
    db.save_message(session_id, "assistant", reply)

    sources = sorted(set(c["source"] for c in retrieved))
    return ChatResponse(reply=reply, session_id=session_id, sources=sources)


@app.get("/api/sessions")
def sessions():
    return db.list_sessions()


@app.get("/api/history/{session_id}")
def history(session_id: str):
    return db.get_history(session_id, limit=200)


@app.delete("/api/history/{session_id}")
def clear_history(session_id: str):
    db.clear_session(session_id)
    return {"status": "cleared"}


@app.post("/api/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".txt", ".md", ".pdf")):
        raise HTTPException(400, "Only .txt, .md, or .pdf files are supported")

    dest = os.path.join(DOCUMENTS_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    n_chunks = rag_engine.add_document_and_reindex(dest)
    return {"status": "indexed", "filename": file.filename, "total_chunks_in_index": n_chunks}


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "local-finetuned" if USE_LOCAL_FINETUNED_MODEL else "gemini"}
