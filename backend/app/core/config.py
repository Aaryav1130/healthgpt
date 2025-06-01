from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # App
    app_name: str = "HealthGPT"
    app_version: str = "1.0.0"
    debug: bool = False
    api_key: str = "dev-key"

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2:3b-instruct-q4_K_M"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_device: str = "cpu"

    # Reranker
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Vector Store
    faiss_index_path: str = "./vector_store/faiss_index"
    faiss_metadata_path: str = "./vector_store/metadata.json"

    # Retrieval
    top_k_dense: int = 10
    top_k_bm25: int = 10
    top_k_rerank: int = 5

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()