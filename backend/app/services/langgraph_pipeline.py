from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import StateGraph, END
from app.services.retriever import hybrid_search
from app.services.reranker import rerank
from app.core.logging import logger
import operator

class RAGState(TypedDict):
    query: str
    retrieved_chunks: List[Dict]
    reranked_chunks: List[Dict]
    final_context: List[Dict]
    conversation_history: List[Dict]
    error: str

def retrieve_node(state: RAGState) -> RAGState:
    """Node 1: Hybrid retrieval from FAISS + BM25."""
    logger.info("RAG Node: Retrieving", query=state["query"][:50])
    try:
        chunks = hybrid_search(state["query"])
        return {**state, "retrieved_chunks": chunks}
    except Exception as e:
        logger.error("Retrieval failed", error=str(e))
        return {**state, "error": str(e), "retrieved_chunks": []}

def rerank_node(state: RAGState) -> RAGState:
    """Node 2: Cross-encoder reranking."""
    if not state["retrieved_chunks"]:
        return {**state, "reranked_chunks": []}

    logger.info("RAG Node: Reranking", candidates=len(state["retrieved_chunks"]))
    reranked = rerank(state["query"], state["retrieved_chunks"])
    return {**state, "reranked_chunks": reranked}

def build_context_node(state: RAGState) -> RAGState:
    """Node 3: Build final context (filter low-quality chunks)."""
    chunks = state["reranked_chunks"]
    # Filter: only keep chunks with rerank_score > threshold
    filtered = [c for c in chunks if c.get("rerank_score", 0) > -5.0]
    return {**state, "final_context": filtered or chunks[:3]}

def should_continue(state: RAGState) -> str:
    if state.get("error"):
        return "error"
    return "continue"

def build_rag_graph() -> StateGraph:
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("build_context", build_context_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "build_context")
    graph.add_edge("build_context", END)

    return graph.compile()

# Singleton compiled graph
_rag_graph = None

def get_rag_graph():
    global _rag_graph
    if _rag_graph is None:
        _rag_graph = build_rag_graph()
    return _rag_graph