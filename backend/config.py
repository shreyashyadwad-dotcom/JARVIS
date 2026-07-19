import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
USE_LOCAL_FINETUNED_MODEL = os.getenv("USE_LOCAL_FINETUNED_MODEL", "false").lower() == "true"
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "./finetuned_jarvis_model")

DB_PATH = os.path.join(os.path.dirname(__file__), "jarvis_history.db")
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")
RAG_STORE_DIR = os.path.join(os.path.dirname(__file__), "rag_store")

JARVIS_SYSTEM_PROMPT = """You are JARVIS, a calm, precise, and slightly witty personal AI assistant \
inspired by the assistant from Iron Man. You address the user respectfully, keep answers concise \
unless detail is requested, and you are proactive about pointing out useful information. \
When given retrieved context from the user's own documents, ground your answer in it and mention \
when you're relying on that context. If you don't know something and no context helps, say so plainly \
instead of inventing facts."""
