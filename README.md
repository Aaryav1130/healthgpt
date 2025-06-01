# 🏥 HealthGPT — Production-Grade Medical RAG System

[![CI](https://github.com/YOUR_USERNAME/healthgpt/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/healthgpt/actions)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript)](https://typescriptlang.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-ready Medical Question Answering system built on Retrieval-Augmented Generation (RAG). Upload medical PDFs and get accurate, source-cited answers in real time — powered by **LangGraph**, **FAISS**, **BGE Embeddings**, **Cross-Encoder Reranking**, and **Llama 3.2 via Ollama** with **Server-Sent Events** streaming.

---

## 📸 Demo

![HealthGPT Demo](docs/demo.gif)

---

## 🏗️ Architecture
Medical PDFs

│

▼

┌─────────────────────────────────────────────────────────┐

│                   INGESTION PIPELINE                    │

│  PyMuPDF → RecursiveCharacterTextSplitter (512 tokens)  │

│       → BGE-small-en-v1.5 Embeddings (CPU)              │

│       → FAISS IndexFlatIP + BM25Okapi                   │

└─────────────────────────┬───────────────────────────────┘

│

▼

┌─────────────────────────────────────────────────────────┐

│                  LANGGRAPH RAG PIPELINE                 │

│                                                         │

│  [retrieve] → Hybrid Search (FAISS + BM25 via RRF)     │

│      ↓                                                  │

│  [rerank]  → Cross-Encoder (ms-marco-MiniLM-L-6-v2)    │

│      ↓                                                  │

│  [build_context] → Quality filter + context assembly   │

└─────────────────────────┬───────────────────────────────┘

│

▼

┌─────────────────────────────────────────────────────────┐

│                    LLM + STREAMING                      │

│   Llama 3.2:3b-instruct (Ollama) → SSE token stream    │

│   FastAPI /chat/stream → React EventSource             │

└─────────────────────────────────────────────────────────┘

**Why this architecture stands out:**
- **2-stage retrieval** (Hybrid Search → Cross-Encoder Rerank) — the same pattern used at Google, Meta, and OpenAI for production RAG
- **LangGraph DAG** — not just a function chain; a proper stateful, inspectable pipeline with conditional routing
- **SSE Streaming** — real-time token delivery matching how ChatGPT works
- **Runs on CPU-only hardware** — quantized LLM inference via Ollama; no GPU required

---

## ✨ Key Features

| Feature | Details |
|---|---|
| 🔍 **Hybrid Search** | Dense (FAISS cosine similarity) + Sparse (BM25) with Reciprocal Rank Fusion |
| 🎯 **Cross-Encoder Reranking** | 2-stage retrieval; ms-marco-MiniLM-L-6-v2 for precision boosting |
| 🧠 **LangGraph Orchestration** | Stateful DAG: Retrieve → Rerank → BuildContext → Stream |
| ⚡ **SSE Streaming** | Real-time token-by-token response delivery via Server-Sent Events |
| 📄 **PDF Ingestion** | PyMuPDF extraction + semantic chunking with overlap |
| 📊 **RAG Evaluation** | RAGAS metrics: Faithfulness, Answer Relevancy, Context Recall |
| 📈 **Monitoring** | Prometheus metrics endpoint; Grafana-ready |
| 🐳 **Containerized** | Full Docker Compose stack: backend + frontend + prometheus |
| 🔄 **CI/CD** | GitHub Actions: lint, test, Docker build on every push |
| 🔒 **API Security** | API key middleware on all endpoints |

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — async REST API + SSE streaming
- [LangGraph](https://langchain-ai.github.io/langgraph/) — RAG pipeline orchestration as a DAG
- [FAISS](https://faiss.ai/) — vector similarity search (CPU)
- [BGE-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) — sentence embeddings
- [BM25Okapi](https://github.com/dorianbrown/rank_bm25) — sparse keyword retrieval
- [ms-marco-MiniLM-L-6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2) — cross-encoder reranker
- [Ollama](https://ollama.com/) — local LLM serving (Llama 3.2:3b quantized)
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction
- [RAGAS](https://docs.ragas.io/) — RAG evaluation framework
- [Prometheus Client](https://github.com/prometheus/client_python) — metrics

**Frontend**
- [React 19](https://react.dev/) + [TypeScript 6](https://typescriptlang.org/) + [Vite 8](https://vitejs.dev/)
- [Tailwind CSS v4](https://tailwindcss.com/) — utility-first styling
- [Lucide React](https://lucide.dev/) — icons
- [Framer Motion](https://www.framer.com/motion/) — animations

**Infrastructure**
- [Docker](https://docker.com/) + [Docker Compose](https://docs.docker.com/compose/)
- [GitHub Actions](https://docs.github.com/en/actions) — CI/CD
- [Prometheus](https://prometheus.io/) — metrics collection
- [Nginx](https://nginx.org/) — frontend serving (production)

---

## 📁 Project Structure
healthgpt/

├── backend/

│   ├── app/

│   │   ├── main.py                    # FastAPI entry point + CORS + lifespan

│   │   ├── api/routes/

│   │   │   ├── chat.py                # POST /chat/stream (SSE)

│   │   │   ├── documents.py           # POST /documents/upload

│   │   │   └── health.py              # GET /health

│   │   ├── core/

│   │   │   ├── config.py              # Pydantic-settings config

│   │   │   ├── logging.py             # Structured JSON logging (structlog)

│   │   │   └── security.py            # API key middleware

│   │   ├── services/

│   │   │   ├── ingestion.py           # PDF → chunks → embeddings → FAISS

│   │   │   ├── retriever.py           # Hybrid search (FAISS + BM25 + RRF)

│   │   │   ├── reranker.py            # Cross-encoder reranking

│   │   │   ├── llm.py                 # Ollama streaming interface

│   │   │   └── langgraph_pipeline.py  # LangGraph RAG DAG

│   │   ├── models/

│   │   │   ├── request.py             # Pydantic request schemas

│   │   │   └── response.py            # Pydantic response schemas

│   │   └── utils/

│   │       ├── pdf_loader.py          # PyMuPDF text extraction

│   │       └── chunker.py             # RecursiveCharacterTextSplitter

│   ├── evaluation/

│   │   ├── evaluate.py                # RAGAS evaluation pipeline

│   │   └── test_queries.json          # Ground truth QA pairs

│   ├── tests/

│   │   ├── test_ingestion.py

│   │   ├── test_retrieval.py

│   │   └── test_api.py

│   ├── monitoring/metrics.py          # Prometheus metrics

│   ├── requirements.txt

│   └── Dockerfile

├── frontend/

│   ├── src/

│   │   ├── components/

│   │   │   ├── ChatInterface.tsx      # Main chat UI

│   │   │   ├── MessageBubble.tsx      # Message + source citations

│   │   │   ├── SourceCard.tsx         # Retrieved document card

│   │   │   ├── UploadModal.tsx        # PDF upload modal

│   │   │   └── StreamingText.tsx      # Real-time token rendering

│   │   ├── hooks/

│   │   │   └── useStreamingChat.ts    # SSE streaming hook

│   │   └── api/

│   │       └── client.ts              # Axios + fetch API client

│   ├── package.json

│   ├── vite.config.ts

│   └── Dockerfile

├── infra/

│   ├── nginx/nginx.conf

│   └── prometheus/prometheus.yml

├── .github/workflows/

│   ├── ci.yml

│   └── cd.yml

├── docker-compose.yml

└── README.md

---

## ⚡ Quick Start

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| Ollama | Latest | Local LLM serving |
| Docker | 24+ | Containerized deployment |

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/healthgpt.git
cd healthgpt
```

### 2. Pull the LLM model

```bash
ollama pull llama3.2:3b-instruct-q4_K_M
```

> **Hardware note:** Runs on CPU-only. Tested on Intel Core i5/i7 with 8GB RAM. Inference is ~3–8 tokens/sec on CPU.

### 3. Start the backend

```bash
cd backend
cp .env.example .env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# In a separate terminal
ollama serve

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the frontend

```bash
cd frontend
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm install
npm run dev
```

Open **http://localhost:5173** 🚀

### 5. Test via API

```bash
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main symptoms described?", "stream": false}'
```

---

## 🐳 Docker Compose (Production)

```bash
docker-compose up --build

# Services:
# Frontend:    http://localhost:3000
# Backend API: http://localhost:8000
# API Docs:    http://localhost:8000/api/docs
# Prometheus:  http://localhost:9090
```

---

## ⚙️ Configuration

All settings via `backend/.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:3b-instruct-q4_K_M
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1024
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DEVICE=cpu
TOP_K_DENSE=10
TOP_K_BM25=10
TOP_K_RERANK=5
CHUNK_SIZE=512
CHUNK_OVERLAP=64
```

---

## 📊 RAG Evaluation

```bash
cd backend
python evaluation/evaluate.py
```

Metrics: **Faithfulness** · **Answer Relevancy** · **Context Recall** · **Context Precision**

---

## 🔍 API Reference

Full interactive docs at **http://localhost:8000/api/docs**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/chat/stream` | Stream RAG response (SSE) |
| `POST` | `/api/v1/documents/upload` | Upload and ingest PDF |
| `GET` | `/api/v1/documents/status` | Index status and chunk count |
| `GET` | `/metrics` | Prometheus metrics |

---

## 🧪 Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --tb=short
```

---

## 🔬 How the RAG Pipeline Works

### Stage 1 — Ingestion
1. PDF text extracted via **PyMuPDF**
2. Text split into 512-token chunks with 64-token overlap
3. Chunks embedded using **BGE-small-en-v1.5** (normalized for cosine similarity)
4. Stored in **FAISS IndexFlatIP** + **BM25Okapi**

### Stage 2 — Hybrid Search + RRF
1. Top-10 candidates from FAISS (dense)
2. Top-10 candidates from BM25 (sparse)
3. Merged using **Reciprocal Rank Fusion**

### Stage 3 — Cross-Encoder Reranking
1. All candidates scored by **ms-marco-MiniLM-L-6-v2**
2. Top-5 selected by rerank score

### Stage 4 — Generation + Streaming
1. LangGraph assembles context with source citations
2. **Llama 3.2** generates via Ollama streaming API
3. Tokens streamed to frontend via **SSE**

---

## 🎯 Design Decisions & Trade-offs

**Why FAISS over Pinecone/Weaviate?**
FAISS runs fully locally with zero API costs. For CPU-constrained hardware this is the right trade-off. At production scale a managed vector DB (Qdrant, Weaviate) would be appropriate.

**Why Llama 3.2:3b quantized?**
The q4_K_M quantization fits in 2–3GB RAM and runs on CPU-only hardware. This demonstrates understanding of real deployment constraints.

**Why LangGraph over a simple function chain?**
LangGraph gives us a proper DAG with named nodes, inspectable state, and conditional routing without refactoring. This is how production ML pipelines are built.

**Why SSE over WebSockets?**
SSE is HTTP-native and perfectly suited for one-directional streaming. WebSockets add unnecessary bidirectional complexity for this use case.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit (`git commit -m 'feat: add your feature'`)
4. Push (`git push origin feat/your-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📚 References

- [Building A Generative AI Platform — Huyen Chip](https://huyenchip.com/2024/07/25/genai-platform.html)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Building Effective Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [MTEB Leaderboard — Best Embedding Models](https://huggingface.co/spaces/mteb/leaderboard)
- [Nearest Neighbor Indexes — Pinecone](https://www.pinecone.io/learn/series/faiss/vector-indexes/)
- [RAGAS Evaluation Framework](https://docs.ragas.io/)
- [GPT in 60 Lines of NumPy](https://jaykmody.com/blog/gpt-from-scratch/)

---

<div align="center">
  <strong>Built with ❤️ for the AI engineering community</strong><br/>
  <sub>⭐ Star this repo if you found it useful!</sub>
</div>