import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, JARVIS_SYSTEM_PROMPT

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

_model = None


def get_model():
    global _model
    if _model is None:
        _model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=JARVIS_SYSTEM_PROMPT,
        )
    return _model


def build_prompt(user_message: str, retrieved_chunks: list, history: list) -> str:
    context_block = ""
    if retrieved_chunks:
        joined = "\n\n".join(
            f"[Source: {c['source']}]\n{c['text']}" for c in retrieved_chunks
        )
        context_block = f"\n\nRelevant context retrieved from your documents:\n{joined}\n"

    history_block = ""
    if history:
        turns = []
        for h in history[-10:]:
            speaker = "User" if h["role"] == "user" else "Jarvis"
            turns.append(f"{speaker}: {h['content']}")
        history_block = "\n\nRecent conversation:\n" + "\n".join(turns)

    return (
        f"{history_block}\n"
        f"{context_block}\n"
        f"User: {user_message}\n"
        f"Jarvis:"
    )


def generate_reply(user_message: str, retrieved_chunks: list, history: list) -> str:
    if not GEMINI_API_KEY:
        return (
            "I can't reach Gemini yet -- no GEMINI_API_KEY is set in your .env file. "
            "Grab a free key at https://aistudio.google.com/apikey and add it to backend/.env."
        )

    model = get_model()
    prompt = build_prompt(user_message, retrieved_chunks, history)
    response = model.generate_content(prompt)
    return response.text.strip()
