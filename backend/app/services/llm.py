import os
from groq import AsyncGroq
from typing import AsyncGenerator
from app.core.config import settings
from app.core.logging import logger

SYSTEM_PROMPT = """You are HealthGPT, a medical information assistant powered by RAG.

INSTRUCTIONS:
- Answer ONLY based on the provided context from medical documents.
- If context is insufficient, say: "I don't have enough information in the provided documents."
- Always cite the source document and page number.
- Do NOT hallucinate medical facts.
- Use clear, professional medical language.
- IMPORTANT: You are an information assistant, not a doctor. Always recommend consulting a healthcare professional."""

async def stream_response(
    query: str,
    context_chunks: list,
    conversation_history: list = None
) -> AsyncGenerator[str, None]:

    # Use Groq if API key available, else fall back to Ollama
    groq_key = os.getenv("GROQ_API_KEY", "")

    if groq_key:
        async for token in _stream_groq(query, context_chunks, conversation_history, groq_key):
            yield token
    else:
        async for token in _stream_ollama(query, context_chunks, conversation_history):
            yield token

async def _stream_groq(query, context_chunks, conversation_history, api_key):
    """Groq streaming — for production deployment."""
    client = AsyncGroq(api_key=api_key)

    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['source']}, Page {chunk['page_num']}]\n{chunk['text']}"
        )
    context_str = "\n\n---\n\n".join(context_parts)

    user_message = f"""CONTEXT FROM MEDICAL DOCUMENTS:
{context_str}

USER QUESTION: {query}

Please answer based on the above context. Cite source numbers in your response."""

    messages = []
    if conversation_history:
        messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": user_message})

    stream = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        temperature=0.1,
        max_tokens=1024,
        stream=True,
    )

    async for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        if token:
            yield token

async def _stream_ollama(query, context_chunks, conversation_history):
    """Ollama streaming — for local development."""
    import httpx
    import json

    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['source']}, Page {chunk['page_num']}]\n{chunk['text']}"
        )
    context_str = "\n\n---\n\n".join(context_parts)

    user_message = f"""CONTEXT FROM MEDICAL DOCUMENTS:
{context_str}

USER QUESTION: {query}"""

    messages = []
    if conversation_history:
        messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": settings.llm_model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": True,
        "options": {"temperature": 0.1, "num_predict": 1024}
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
