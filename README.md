# JARVIS — Personal AI Assistant (Local, Gemini + RAG)

A locally-run chatbot with:
- **Gemini API** for language generation (free tier)
- **RAG** (Retrieval-Augmented Generation) over your own documents, running fully locally
  (sentence-transformers + FAISS — no API key needed for this part)
- **Persistent chat history** saved to a local SQLite database
- **Optional**: a Colab notebook to LoRA fine-tune a small open-source model on your own
  persona/data, which the backend can use *instead of* Gemini if you want

```
jarvis-project/
├── backend/          FastAPI server (Python)
├── frontend/          React + Vite chat UI
├── colab/              Optional fine-tuning notebook
└── README.md
```



##  Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then open .env and paste your GEMINI_API_KEY
```

Run the server:

```bash
uvicorn main:app --reload --port 8000
```



##  Frontend setup

In a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Open the URL it prints (usually http://localhost:5173).

That's it — you now have a locally running Jarvis with a chat UI.

##  Teach it about your own stuff (RAG)

Either:
- Drop `.txt`, `.md`, or `.pdf` files into `backend/documents/` and restart the backend, or
- Use the **"Upload document"** button in the sidebar — it re-indexes automatically, no restart needed.

Ask a question about the content and Jarvis will retrieve the relevant chunks and cite the
source file under its answer.

## 5. Chat history

Every message is saved to `backend/jarvis_history.db`. Sessions appear in the sidebar; click one
to reload that conversation. This persists across restarts of both frontend and backend.

## 6. (Optional) Fine-tune your own small model on Colab

Open `colab/finetune_jarvis.ipynb` in Google Colab (upload it, or open via
File → Upload notebook). It walks through:
1. Loading a small open model (TinyLlama-1.1B-Chat)
2. LoRA fine-tuning it on example Jarvis-style Q&A pairs (edit these with your own data)
3. Merging and downloading the fine-tuned model

**Be aware:** this trains a small model's *persona/style*, not a large reasoning model. Gemini
will still be much smarter for actual question-answering. Most people should leave
`USE_LOCAL_FINETUNED_MODEL=false` and treat the notebook as a fun experiment. If you do want to
use it: unzip the downloaded model into `backend/finetuned_jarvis_model/`, then in `backend/.env`
set:

```
USE_LOCAL_FINETUNED_MODEL=true
LOCAL_MODEL_PATH=./finetuned_jarvis_model
```

and restart the backend. You'll also need to `pip install torch transformers` in the backend venv
for this path (not included in requirements.txt by default, since most people won't use it).

## Troubleshooting

- **"Backend offline" in the UI** → make sure `uvicorn` is running on port 8000.
- **Gemini errors / empty replies** → check `GEMINI_API_KEY` in `backend/.env` is set and valid.
- **RAG not finding your document** → confirm the file extension is `.txt`, `.md`, or `.pdf`, and
  check the backend terminal for errors during indexing.
- **CORS errors in browser console** → the backend only allows `localhost:5173` by default; edit
  the `allow_origins` list in `backend/main.py` if you're serving the frontend elsewhere.
