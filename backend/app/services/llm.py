import httpx
import json
from typing import AsyncGenerator
from app.core.config import settings
from app.core.logging import logger

SYSTEM_PROMPT = """You are HealthGPT, a medical information assistant powered by RAG (Retrieval-Augmented Generation).

INSTRUCTIONS:
- Answer ONLY based on the provided context from medical documents.
- If the context does not contain enough information, say: "I don't have sufficient information in the provided documents to answer this accurately."
- Always cite the source document and page number.
- Do NOT hallucinate or guess medical facts.
- Use clear, professional medical language.
- Format your response with clear sections when appropriate.

IMPORTANT: You are an information assistant, not a doctor. Always recommend consulting a healthcare professional for medical decisions."""

async def stream_response(
    query: str,
    context_chunks: list,
    conversation_history: list = None
) -> AsyncGenerator[str, None]:
    """
    Stream LLM response using Ollama's streaming API.
    """
    # Build context string with source citations
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['source']}, Page {chunk['page_num']}]\n{chunk['text']}"
        )
    context_str = "\n\n---\n\n".join(context_parts)

    user_message = f"""CONTEXT FROM MEDICAL DOCUMENTS:
{context_str}

USER QUESTION: {query}

Please answer based on the above context. Cite the source numbers in your response."""

    messages = []
    if conversation_history:
        messages.extend(conversation_history[-6:])  # Keep last 3 turns
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": settings.llm_model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": True,
        "options": {
            "temperature": settings.llm_temperature,
            "num_predict": settings.llm_max_tokens,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
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
