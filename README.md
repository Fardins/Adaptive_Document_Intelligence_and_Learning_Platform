<div align="center">

# Adaptive Document Intelligence & Learning Platform

### Transform PDF books into an AI-powered adaptive learning ecosystem

<p align="center">
Semantic Retrieval • Adaptive MCQs • Multi-Book Learning • Vector Search • Learning Analytics
</p>

<br/>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Database-6A5ACD?style=for-the-badge)
![Plotly](https://img.shields.io/badge/Plotly-Analytics-3F4FBD?style=for-the-badge&logo=plotly&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM_Powered-FF6600?style=for-the-badge)

<br/>

</div>

---
## Table of Contents

1. [Overview](#overview)
2. [Live Demo](#live-demo)
3. [Why This Project Matters](#why-this-project-matters)
3. [Core Features](#core-features)
5. [System Architecture](#system-architecture)
6. [Project Structure](#project-structure)
7. [Tech Stack](#tech-stack)
8. [Installation](#installation)
9. [Environment Variables](#environment-variables)
10. [Running the Application](#running-the-application)
11. [Usage Workflow](#usage-workflow)
12. [Analytics Dashboard](#analytics-dashboard)
13. [Persistence & Storage](#persistence--storage)
14. [Engineering Highlights](#engineering-highlights)
15. [Roadmap](#roadmap)
16. [Contributing](#contributing)
17. [Acknowledgements](#acknowledgements)
18. [Author](#author)

---

## Overview

The **Adaptive Document Intelligence & Learning Platform** is an AI-powered system that converts static PDF books into an intelligent, interactive, and adaptive learning environment.\
It combines semantic retrieval, adaptive assessment, vector databases, and **LLM-powered quiz generation** to create a **personalized AI-assisted learning experience**.

The platform combines:

- PDF document understanding
- Semantic chunking
- Vector retrieval with ChromaDB
- LLM-driven adaptive quiz generation
- Learning analytics and mastery tracking
- Interactive Streamlit dashboards

This project demonstrates a production-style AI workflow that integrates:

- document parsing
- semantic retrieval
- adaptive assessment
- vector search
- learning analytics

into a unified educational intelligence platform.

---
## Live Demo

<div align="center">

### Try it live — no installation needed

**[Adaptive-Document-Intelligence-and-Learning-Platform](https://adaptive-document-intelligence-and-learning-platform.streamlit.app/)**
> See [Running the App](#running-the-application) → *Deploy to Streamlit Cloud* for step-by-step instructions.

</div>

---
## Why This Project Matters

Traditional PDF books are passive and difficult to learn from efficiently.

This platform transforms books into structured knowledge systems by:

- extracting semantic sections
- enabling intelligent retrieval
- generating adaptive quizzes dynamically
- tracking learner performance over time
- building personalized mastery profiles

The system enables:

- AI-assisted self-learning
- adaptive educational workflows
- intelligent tutoring systems
- semantic document understanding
- retrieval-augmented learning experiences

It bridges the gap between static educational material and intelligent AI-powered learning systems.

---

## Core Features

###  Document Intelligence

- Upload PDF books directly through Streamlit
- Automatic section extraction
- Hierarchical metadata preservation
- Intelligent semantic chunking
- Multi-book management and switching

---

### Semantic Retrieval Engine

- Embedding generation using Sentence Transformers
- Persistent ChromaDB vector storage
- Section-aware retrieval pipeline
- Fast semantic search
- Chunk-level inspection and exploration

---

### Adaptive Learning System

- LLM-powered MCQ generation using Groq API
- Adaptive quiz workflow
- Weakness-aware question generation
- Personalized learning sessions
- Session-based mastery tracking

---

### Learning Analytics

- Interactive Plotly dashboards
- Accuracy tracking by section
- Correct vs wrong analytics
- Knowledge progression monitoring
- Personalized learning insights

---

### Developer Experience

- Modular architecture
- Persistent storage pipeline
- Multi-page Streamlit dashboard
- Production-oriented structure
- Scalable ingestion workflow

---

## System Architecture

```text
                ┌────────────────────┐
                │    PDF Upload      │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │  Section Extraction │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Semantic Chunking  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Embedding Generation│
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ ChromaDB Vector DB │
                └─────────┬──────────┘
                          │
        ┌─────────────────┴─────────────────┐
        ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│ Section Explorer │              │ Adaptive Quizzes │
└──────────────────┘              └──────────────────┘
                                              │
                                              ▼
                                   ┌──────────────────┐
                                   │ Learning Analytics│
                                   └──────────────────┘
```

---

## Project Structure

```text
Adaptive_Document_Preparation_System/
│
├── app.py
├── main.py
├── config.py
├── requirements.txt
├── .env
├── book_meta.json
├── books_registry.json
├── section_map_full.json
│
├── books/
├── chroma_store/
├── section_maps/
├── history/
│   ├── mastery.json
│   └── quiz_history.json
│
├── input_processing/
│   ├── parser.py
│   ├── chunker.py
│   ├── storage.py
│   ├── ingest.py
│   ├── check.py
│   └── main.py
│
├── adaptivity_processing/
│   ├── adaptive_engine.py
│   ├── adaptive_quiz.py
│   ├── knowledge_base.py
│   └── session_manager.py
│
└── mcq_processing/
    ├── mcq_generator.py
    ├── quiz_engine.py
    └── quiz_engine.py
```

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.10+ |
| Frontend UI | Streamlit |
| Vector Database | ChromaDB |
| Embedding Model | Sentence Transformers |
| LLM Provider | Groq API |
| Visualization | Plotly |
| Data Processing | Pandas |

---

## Installation

### 1. Clone Repository

```bash
git clone <https://github.com/Fardins/Adaptive_Document_Intelligence_and_Learning_Platform.git>
cd Adaptive_Document_Preparation_System
```

---

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

---

### 3. Activate Environment

### Windows

```powershell
.\.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
HF_TOKEN=your_huggingface_token
GROQ_API_KEY=your_groq_api_key
```

---

### Required Keys

| Variable | Purpose |
|---|---|
| `HF_TOKEN` | HuggingFace model access |
| `GROQ_API_KEY` | Groq LLM API access |

> Never commit your `.env` file to GitHub.

---

## Running the Application

### Launch Streamlit Dashboard

```bash
streamlit run app.py
```

Open the local URL shown in the terminal.

---

### Run CLI Pipeline

```bash
python main.py
```

The pipeline automatically:

- checks ChromaDB persistence
- skips re-ingestion if embeddings already exist
- launches adaptive quiz workflow

---

## Usage Workflow

### Step 1 — Upload PDF

Upload a PDF document using the Streamlit dashboard.

---

### Step 2 — Intelligent Processing

The system automatically:

- extracts sections
- chunks content semantically
- generates embeddings
- stores vectors in ChromaDB

---

### Step 3 — Explore Content

Browse:

- document sections
- metadata
- chunked text
- vectorized content

---

### Step 4 — Generate Adaptive Quiz

Create personalized MCQs dynamically using Groq-powered LLM generation.

---

### Step 5 — Track Learning Progress

Monitor:

- mastery score
- weaknesses
- section accuracy
- analytics dashboard

---

## Analytics Dashboard

The analytics system provides:

- section-level performance tracking
- quiz accuracy visualization
- correct vs wrong answer analysis
- mastery progression monitoring
- personalized learning insights

Powered by interactive Plotly visualizations inside Streamlit.

---

## Persistence & Storage

| Storage | Purpose |
|---|---|
| `chroma_store/` | Vector embeddings |
| `section_maps/` | Section metadata |
| `history/` | Quiz sessions & mastery |
| `books_registry.json` | Multi-book registry |
| `book_meta.json` | Active book tracking |

---

## Engineering Highlights

- Modular AI pipeline architecture
- Persistent semantic vector storage
- Adaptive assessment workflow
- Multi-book learning support
- Retrieval-aware chunking strategy
- Session-based knowledge tracking
- Streamlit production dashboard
- Scalable ingestion pipeline


---

## Roadmap

- OCR support for scanned PDFs
- RAG-based conversational chatbot
- Difficulty-aware adaptive quizzes
- User authentication and learner profiles
- Cloud vector database integration
- Real-time collaborative learning
- Docker deployment support
- Automated testing pipeline

---

## Contributing

Contributions are welcome.

### Development Setup

```bash
git clone <repo-url>

cd Adaptive_Document_Preparation_System

python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

### Contribution Guidelines

- Keep modules focused on a single responsibility
- Update documentation when adding new features
- Maintain modular project structure
- Test both Streamlit and CLI workflows

---

## Acknowledgements

This project combines concepts from:

- Semantic Retrieval Systems
- Adaptive Learning Platforms
- Retrieval-Augmented Generation (RAG)
- Vector Databases
- Educational AI Systems
- LLM-powered Knowledge Assessment

Built as AI/ML portfolio project focused on intelligent document understanding and adaptive learning systems.

---
## Author
**MD. ATICKUR RAHMAN**\
Gmail: atickft13129@gmail.com\
Contact: **01849647396**