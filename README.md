# 🏥 HealthGPT — Production-Grade Medical RAG System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?logo=typescript)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-ready Medical Question Answering system built on Retrieval-Augmented Generation (RAG). Upload medical PDFs and get accurate, source-cited answers in real time — powered by **LangGraph**, **FAISS**, **BGE Embeddings**, **Cross-Encoder Reranking**, and **Llama 3.2 via Ollama** with **Server-Sent Events** streaming.

## 📋 Table of Contents

- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [Architecture](#️-architecture)
- [Demo](#-demo)
- [Project Structure](#-project-structure)
- [Run the Chatbot](#-quick-start)
  - [Windows Setup (WSL + Ubuntu)](#-windows-setup-wsl--ubuntu----do-this-first)
  - [Clone the Repository](#1-clone-the-repository)
  - [Pull the LLM Model](#2-pull-the-llm-model)
  - [Backend Setup](#3-backend-setup)
  - [Frontend Setup](#4-frontend-setup
- [References](#-references)
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

---
## 🏗️ Architecture

```
                        ┌─────────────────┐
                        │   Medical PDFs  │
                        └────────┬────────┘
                                 │
                                 ▼
              ╔═══════════════════════════════════════╗
              ║          INGESTION PIPELINE           ║
              ║                                       ║
              ║  PyMuPDF                              ║
              ║     │  (PDF text extraction)          ║
              ║     ▼                                 ║
              ║  RecursiveCharacterTextSplitter       ║
              ║     │  (512 tokens, 64 overlap)       ║
              ║     ▼                                 ║
              ║  BGE-small-en-v1.5 Embeddings         ║
              ║     │  (CPU, normalized vectors)      ║
              ║     ▼                                 ║
              ║  FAISS IndexFlatIP  +  BM25Okapi      ║
              ║  (dense vector store) (sparse index)  ║
              ╚═══════════════════╤═══════════════════╝
                                  │
                                  ▼
              ╔═══════════════════════════════════════╗
              ║        LANGGRAPH RAG PIPELINE         ║
              ║                                       ║
              ║  ┌─────────────────────────────────┐  ║
              ║  │  Node 1: retrieve               │  ║
              ║  │  FAISS top-10 + BM25 top-10     │  ║
              ║  │  merged via Reciprocal Rank      │  ║
              ║  │  Fusion (RRF)                   │  ║
              ║  └──────────────┬──────────────────┘  ║
              ║                 │                      ║
              ║  ┌──────────────▼──────────────────┐  ║
              ║  │  Node 2: rerank                 │  ║
              ║  │  ms-marco-MiniLM-L-6-v2         │  ║
              ║  │  Cross-Encoder scores all pairs  │  ║
              ║  │  → selects top-5 by score        │  ║
              ║  └──────────────┬──────────────────┘  ║
              ║                 │                      ║
              ║  ┌──────────────▼──────────────────┐  ║
              ║  │  Node 3: build_context          │  ║
              ║  │  Quality filter + source tags   │  ║
              ║  │  + context assembly             │  ║
              ║  └──────────────┬──────────────────┘  ║
              ╚═════════════════╪═════════════════════╝
                                │
                                ▼
              ╔═══════════════════════════════════════╗
              ║           LLM + STREAMING             ║
              ║                                       ║
              ║  Llama 3.2:3b-instruct (Ollama)       ║
              ║     │  (quantized, CPU-only)          ║
              ║     ▼                                 ║
              ║  FastAPI SSE  →  React EventSource    ║
              ║  (token-by-token streaming)           ║
              ╚═══════════════════════════════════════╝
```

**Why this architecture stands out:**
- **2-stage retrieval** (Hybrid Search → Cross-Encoder Rerank) — the same pattern used at Google, Meta, and OpenAI for production RAG
- **LangGraph DAG** — not just a function chain; a proper stateful, inspectable pipeline with conditional routing
- **SSE Streaming** — real-time token delivery matching how ChatGPT works
- **Runs on CPU-only hardware** — quantized LLM inference via Ollama; no GPU required

---
## 📸 Demo

![HealthGPT Demo](docs/demo.gif)

> Upload any medical PDF → ask questions in natural language → get streaming answers with source citations

---

## 📁 Project Structure

```
healthgpt/
│
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry point, CORS, lifespan
│   │   │
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── chat.py           # POST /api/v1/chat/stream  (SSE)
│   │   │       ├── documents.py      # POST /api/v1/documents/upload
│   │   │       └── health.py         # GET  /health
│   │   │
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic-settings environment config
│   │   │   ├── logging.py            # Structured JSON logging
│   │   │   └── security.py           # API key middleware
│   │   │
│   │   ├── services/
│   │   │   ├── ingestion.py          # PDF → chunks → embeddings → FAISS + BM25
│   │   │   ├── retriever.py          # Hybrid search with RRF fusion
│   │   │   ├── reranker.py           # Cross-encoder reranking
│   │   │   ├── llm.py                # Ollama streaming client
│   │   │   └── langgraph_pipeline.py # LangGraph DAG orchestration
│   │   │
│   │   ├── models/
│   │   │   ├── request.py            # Pydantic request schemas
│   │   │   └── response.py           # Pydantic response schemas
│   │   │
│   │   ├── utils/
│   │   │   ├── pdf_loader.py         # PyMuPDF text extraction helper
│   │   │   └── chunker.py            # RecursiveCharacterTextSplitter
│   │   │
│   │   └── monitoring/
│   │       └── metrics.py            # Prometheus metrics definitions
│   │
│   ├── evaluation/
│   │   ├── evaluate.py               # RAGAS evaluation pipeline
│   │   └── test_queries.json         # Ground truth QA pairs for eval
│   │
│   ├── tests/
│   │   ├── test_ingestion.py
│   │   ├── test_retrieval.py
│   │   └── test_api.py
│   │
│   ├── .env.example                  # Environment variable template
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                         # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx     # Main chat layout
│   │   │   ├── MessageBubble.tsx     # User/assistant message renderer
│   │   │   ├── SourceCard.tsx        # Retrieved document citation card
│   │   │   ├── UploadModal.tsx       # PDF upload modal with drag-and-drop
│   │   │   └── StreamingText.tsx     # Real-time token rendering component
│   │   │
│   │   ├── hooks/
│   │   │   └── useStreamingChat.ts   # SSE streaming state management hook
│   │   │
│   │   ├── api/
│   │   │   └── client.ts             # Axios client + TypeScript interfaces
│   │   │
│   │   ├── App.tsx                   # Root component
│   │   └── main.tsx                  # Vite entry point
│   │
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── infra/
│   ├── nginx/
│   │   └── nginx.conf                # Nginx reverse proxy config
│   └── prometheus/
│       └── prometheus.yml            # Prometheus scrape config
│
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint + test + Docker build
│       └── cd.yml                    # Deploy on push to main
│
├── docker-compose.yml                # Production stack
├── LICENSE
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| Ollama | Latest | Local LLM serving |
| Docker | 24+ | Containerized deployment (optional) |

> **🪟 Windows Users — IMPORTANT:** This project runs inside **WSL 2 (Windows Subsystem for Linux)** with **Ubuntu 22.04**. You must set this up before anything else. See the WSL setup section below.

---

### 🪟 Windows Setup (WSL + Ubuntu) — Do This First

**Step 1 — Install WSL 2 with Ubuntu**

Open **PowerShell as Administrator** and run:
```powershell
wsl --install
```
This installs WSL 2 + Ubuntu 22.04 automatically. Restart your PC when prompted.

**Step 2 — Open Ubuntu terminal**

Search for **"Ubuntu"** in the Start menu and open it. Create your Linux username and password when prompted.

**Step 3 — Install required tools inside Ubuntu**

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install -y python3.12 python3.12-venv python3-pip

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install git
sudo apt install -y git

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

**Step 4 — Open VS Code from WSL (not from Windows)**

```bash
# Inside Ubuntu terminal, navigate to your project and open VS Code
cd ~/healthgpt
code .
```

> ⚠️ Always open VS Code **from the WSL terminal** using `code .` — never drag and drop files from Windows Explorer into WSL. This causes file permission errors.

---

### 1. Clone the Repository

```bash
git clone https://github.com/Aaryav1130/healthgpt.git
cd healthgpt
```

---

### 2. Pull the LLM Model

```bash
# Start Ollama service (run in a separate terminal and keep it running)
ollama serve

# Pull the model (in another terminal)
ollama pull llama3.2:3b-instruct-q4_K_M
```

> **Hardware note:** Runs fully on CPU. Tested on Intel Core i5/i7 with 8GB RAM. Inference speed is ~3–8 tokens/sec on CPU. No GPU required.

---

### 3. Backend Setup

```bash
cd ~/healthgpt/backend

# Copy environment config
cp .env.example .env

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Fix common setup issue — remove PROMETHEUS_PORT from .env:**
```bash
# The Settings class does not have a prometheus_port field
# Remove it to prevent Pydantic validation error on startup
sed -i '/PROMETHEUS_PORT/d' .env
```

**Start the backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API is now running at **http://localhost:8000**
Interactive API docs at **http://localhost:8000/api/docs**

---

### 4. Frontend Setup

Open a **new terminal tab** (keep backend running):

```bash
cd ~/healthgpt/frontend

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open **http://localhost:5173** in your browser 🚀

---

### 5. Upload a PDF and Ask Questions

1. Click **"Upload PDF"** in the top-right corner
2. Upload any **text-based** medical PDF (WHO reports, clinical guidelines, research papers)
3. Wait for the "X chunks indexed" count to update
4. Type a question in the chat box and press Enter
5. Watch the answer stream in real time with source citations

```bash
# Or test via API directly
curl -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main symptoms described?", "stream": false}'
```

> ⚠️ **PDF Note:** Only **text-based PDFs** work (e.g. downloaded research papers, WHO reports). Scanned handwritten notes or image-only PDFs will not extract text correctly.

---

## 🐳 Docker Compose (Production)

```bash
# Start full stack: backend + frontend + prometheus
docker-compose up --build

# Running services:
# Frontend:    http://localhost:3000
# Backend API: http://localhost:8000
# API Docs:    http://localhost:8000/api/docs
# Prometheus:  http://localhost:9090
```

---

## ⚙️ Configuration

All settings are controlled via `backend/.env`. Copy from `.env.example` and edit:

```env
# LLM Settings
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:3b-instruct-q4_K_M
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1024

# Embedding Settings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DEVICE=cpu

# Retrieval Settings
TOP_K_DENSE=10        # FAISS candidates
TOP_K_BM25=10         # BM25 candidates
TOP_K_RERANK=5        # Final results after reranking

# Chunking Settings
CHUNK_SIZE=512
CHUNK_OVERLAP=64
```

---

## 🔬 How the RAG Pipeline Works

### Stage 1 — Ingestion
1. PDF text extracted page-by-page via **PyMuPDF**
2. Text split into **512-token chunks** with 64-token overlap using RecursiveCharacterTextSplitter
3. Each chunk embedded using **BGE-small-en-v1.5** (L2-normalized for cosine similarity)
4. Dense vectors stored in **FAISS IndexFlatIP**; raw text indexed in **BM25Okapi**

### Stage 2 — Hybrid Retrieval + RRF
1. Query embedded → top-10 candidates from FAISS **(dense)**
2. Query tokenized → top-10 candidates from BM25 **(sparse)**
3. Both result lists merged using **Reciprocal Rank Fusion** — no score normalization needed

### Stage 3 — Cross-Encoder Reranking
1. All RRF candidates passed as `(query, passage)` pairs to **ms-marco-MiniLM-L-6-v2**
2. Cross-encoder scores each pair independently (more accurate than bi-encoder similarity)
3. **Top-5 results** selected by rerank score → passed to LLM

### Stage 4 — Generation + Streaming
1. LangGraph assembles context from top-5 chunks with page/source metadata
2. Medical system prompt + context + user query sent to **Llama 3.2 via Ollama**
3. Response tokens streamed via **Server-Sent Events (SSE)**
4. React `EventSource` renders tokens in real time as they arrive

---

## 📊 RAG Evaluation

HealthGPT includes a RAGAS-based evaluation pipeline:

```bash
cd backend
source venv/bin/activate
python evaluation/evaluate.py
```

**Metrics computed:**

| Metric | What it measures |
|---|---|
| Faithfulness | Are answers grounded in retrieved context? |
| Answer Relevancy | Does the answer address the question asked? |
| Context Recall | Is the right context being retrieved? |
| Context Precision | Is irrelevant context being filtered out? |

---

## 🔍 API Reference

Full interactive docs at **http://localhost:8000/api/docs**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns status and model info |
| `POST` | `/api/v1/chat/stream` | Stream RAG response via SSE |
| `POST` | `/api/v1/documents/upload` | Upload PDF and trigger ingestion |
| `GET` | `/api/v1/documents/status` | Get index status and total chunk count |
| `GET` | `/metrics` | Prometheus metrics endpoint |

**Example request:**
```json
POST /api/v1/chat/stream
{
  "query": "What are the symptoms of hypertension?",
  "conversation_history": [],
  "stream": true
}
```

---

## 🧪 Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --tb=short
```

---

## 📈 Monitoring

Prometheus metrics exposed at `/metrics`:

| Metric | Description |
|---|---|
| `healthgpt_requests_total` | Request count by endpoint |
| `healthgpt_request_duration_seconds` | Latency histogram |
| `healthgpt_rag_retrieval_duration_seconds` | Retrieval stage latency |
| `healthgpt_llm_tokens_generated_total` | Total tokens generated |

Connect Grafana to `http://localhost:9090` to build dashboards.

---

## 🎯 Design Decisions & Trade-offs

**Why FAISS over Pinecone/Weaviate?**
FAISS runs fully locally with zero API costs and no internet dependency. For CPU-constrained hardware this is the right trade-off. At production scale, a managed vector DB (Qdrant, Weaviate) would be more appropriate.

**Why Llama 3.2:3b quantized?**
The q4_K_M quantization fits in 2–3GB RAM and runs on CPU-only hardware. This demonstrates understanding of real deployment constraints — a key engineering skill.

**Why LangGraph over a simple function chain?**
LangGraph gives a proper DAG with named nodes, inspectable state, and the ability to add conditional routing (e.g. fallback node when no context is retrieved) without refactoring the entire pipeline.

**Why SSE over WebSockets?**
SSE is HTTP-native and perfectly suited for one-directional streaming (server → client). WebSockets add unnecessary bidirectional complexity for this use case.

**Why Hybrid Search (FAISS + BM25) over pure dense retrieval?**
Dense retrieval excels at semantic similarity but can miss exact keyword matches (drug names, medical codes). BM25 catches these exact matches. RRF combines both without requiring score normalization.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📚 References

- [Building A Generative AI Platform — Huyen Chip](https://huyenchip.com/2024/07/25/genai-platform.html)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Building Effective Agents — Anthropic](https://www.anthropic.com/research/building-effective-agents)
- [MTEB Leaderboard — Best Embedding Models](https://huggingface.co/spaces/mteb/leaderboard)
- [Nearest Neighbor Indexes for Similarity Search — Pinecone](https://www.pinecone.io/learn/series/faiss/vector-indexes/)
- [RAGAS Evaluation Framework](https://docs.ragas.io/)
- [GPT in 60 Lines of NumPy](https://jaykmody.com/blog/gpt-from-scratch/)
- [Introduction to Weight Quantization](https://towardsdatascience.com/introduction-to-weight-quantization-2494701b9c0c)

---

<div align="center">
  <strong>Built with ❤️ for the AI engineering community</strong><br/>
  <sub>⭐ Star this repo if you found it useful!</sub>
</div>
