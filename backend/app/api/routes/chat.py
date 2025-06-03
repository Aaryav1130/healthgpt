from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from app.models.request import ChatRequest
from app.models.response import ChatResponse, SourceDocument
from app.services.langgraph_pipeline import get_rag_graph
from app.services.llm import stream_response
from app.core.logging import logger
from app.monitoring.metrics import QUERY_COUNTER, RETRIEVAL_LATENCY
import time
import json

router = APIRouter(prefix="/chat", tags=["chat"])

async def event_stream(query: str, chunks: list, history: list):
    """Server-Sent Events generator."""
    # First, send the source documents as metadata
    sources = [
        {
            "source": c["source"],
            "page_num": c["page_num"],
            "text": c["text"][:200] + "...",
            "rerank_score": c.get("rerank_score"),
        }
        for c in chunks
    ]
    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

    # Then stream the LLM response token by token
    async for token in stream_response(query, chunks, history):
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Main RAG endpoint with streaming response.
    Flow: Query → LangGraph(Retrieve → Rerank → BuildContext) → Stream LLM
    """
    start = time.time()
    QUERY_COUNTER.inc()

    try:
        # Run LangGraph RAG pipeline
        graph = get_rag_graph()
        state = graph.invoke({
            "query": request.query,
            "retrieved_chunks": [],
            "reranked_chunks": [],
            "final_context": [],
            "conversation_history": [
                {"role": m.role, "content": m.content}
                for m in request.conversation_history
            ],
            "error": "",
        })

        chunks = state["final_context"]
        elapsed = time.time() - start
        RETRIEVAL_LATENCY.observe(elapsed)

        logger.info(
            "RAG pipeline complete",
            query_len=len(request.query),
            chunks_found=len(chunks),
            latency_ms=round(elapsed * 1000, 2)
        )

        if not chunks:
            async def no_context_stream():
                msg = "I couldn't find relevant information in the medical documents. Please upload relevant PDFs first."
                yield f"data: {json.dumps({'type': 'sources', 'sources': []})}\n\n"
                yield f"data: {json.dumps({'type': 'token', 'content': msg})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return StreamingResponse(no_context_stream(), media_type="text/event-stream")

        return StreamingResponse(
            event_stream(
                request.query,
                chunks,
                [{"role": m.role, "content": m.content} for m in request.conversation_history]
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.error("Chat error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))