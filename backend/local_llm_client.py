"""
Optional: use a model you fine-tuned yourself in the Colab notebook (colab/finetune_jarvis.ipynb)
instead of Gemini. Set USE_LOCAL_FINETUNED_MODEL=true in backend/.env and point LOCAL_MODEL_PATH
at the folder you downloaded from Colab.

Note: a small locally fine-tuned model (e.g. a LoRA-tuned 1-3B parameter model) will sound more
like "Jarvis" in persona/style but will generally reason far worse than Gemini. Most people should
keep USE_LOCAL_FINETUNED_MODEL=false and use Gemini for real answers, treating the fine-tuned model
as a fun side experiment. This file is provided so you can plug it in if you want to try it anyway.
"""
import os
from config import LOCAL_MODEL_PATH, JARVIS_SYSTEM_PROMPT

_tokenizer = None
_model = None


def _load():
    global _tokenizer, _model
    if _model is not None:
        return
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    if not os.path.isdir(LOCAL_MODEL_PATH):
        raise RuntimeError(
            f"LOCAL_MODEL_PATH '{LOCAL_MODEL_PATH}' does not exist. "
            "Run the Colab notebook, download the model folder, and set the correct path in .env."
        )

    _tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
    _model = AutoModelForCausalLM.from_pretrained(
        LOCAL_MODEL_PATH,
        torch_dtype=torch.float32,
    )
    _model.eval()


def generate_reply(user_message: str, retrieved_chunks: list, history: list) -> str:
    _load()
    import torch

    context_block = ""
    if retrieved_chunks:
        context_block = "\n".join(c["text"] for c in retrieved_chunks)

    history_text = ""
    for h in history[-6:]:
        speaker = "User" if h["role"] == "user" else "Jarvis"
        history_text += f"{speaker}: {h['content']}\n"

    prompt = (
        f"{JARVIS_SYSTEM_PROMPT}\n\n"
        f"Context:\n{context_block}\n\n"
        f"{history_text}User: {user_message}\nJarvis:"
    )

    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    with torch.no_grad():
        output = _model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=_tokenizer.eos_token_id,
        )
    text = _tokenizer.decode(output[0], skip_special_tokens=True)
    return text.split("Jarvis:")[-1].strip()
