import os
import httpx
import json
from typing import AsyncGenerator
from app.core.config import settings
from app.core.logging import logger

SYSTEM_PROMPT = """You are HealthGPT, a medical information assistant powered by RAG.

INSTRUCTIONS:
- Answer ONLY based on the provided context from medical documents.
- If context is insufficient say: "I don't have enough information in the provided documents."
- Always cite the source document and page number like [Source 1].
- Do NOT hallucinate or guess medical facts.
- Use clear professional medical language.
- Always recommend consulting a healthcare professional for medical decisions."""

def _build_messages(query: str, context_chunks: list, conversation_history: list):
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['source']}, Page {chunk['page_num']}]\n{chunk['text']}"
        )
    context_str = "\n\n---\n\n".join(context_parts)

    user_message = f"""CONTEXT FROM MEDICAL DOCUMENTS:
{context_str}

USER QUESTION: {query}

Answer based on the context above. Cite source numbers like [Source 1] in your response."""

    messages = []
    if conversation_history:
        messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": user_message})
    return messages

async def stream_response(
    query: str,
    context_chunks: list,
    conversation_history: list = None
) -> AsyncGenerator[str, None]:

    groq_key = os.getenv("GROQ_API_KEY", "")

    if groq_key:
        logger.info("Using Groq API for inference")
        async for token in _stream_groq(query, context_chunks, conversation_history or [], groq_key):
            yield token
    else:
        logger.info("Using Ollama for inference")
        async for token in _stream_ollama(query, context_chunks, conversation_history or []):
            yield token

async def _stream_groq(query, context_chunks, conversation_history, api_key):
    """Groq streaming — used in production deployment."""
    messages = _build_messages(query, context_chunks, conversation_history)

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                "temperature": 0.1,
                "max_tokens": 1024,
                "stream": True,
            }
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        token = chunk["choices"][0]["delta"].get("content", "")
                        if token:
                            yield token
                    except (json.JSONDecodeError, KeyError):
                        continue

async def _stream_ollama(query, context_chunks, conversation_history):
    """Ollama streaming — used in local development."""
    messages = _build_messages(query, context_chunks, conversation_history)

    payload = {
        "model": settings.llm_model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": True,
        "options": {
            "temperature": settings.llm_temperature,
            "num_predict": settings.llm_max_tokens,
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{settings.ollama_base_url}/api/chat",
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        token = data.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
