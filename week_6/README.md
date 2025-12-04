# Week 6 - AI Serving & Deployment

AI deployment projects focusing on serving and production deployment.

## Projects

### 1. Medical RAG Chatbot (Day 5: AI Deployment)
- **Port:** 8502
- **Tech Stack:** Flask, LangChain, FAISS, Groq LLM
- **Description:** Medical Q&A assistant that provides health information using RAG (Retrieval Augmented Generation)

## Deployment URL

| Project | URL |
|---------|-----|
| Medical RAG Chatbot | http://<EXTERNAL_IP>:8502 |

## Setup Instructions

### Prerequisites
- Python 3.10+
- Groq API Key (get it from https://console.groq.com/)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/rwurdig/GenAI_bootcamp.git
cd GenAI_bootcamp/week_6/medical-rag

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Run the application
python app/application.py
```

### Using tmux for Persistent Deployment

```bash
# Start Medical RAG
tmux new-session -d -s medical "cd ~/projects/medical-rag && source venv/bin/activate && python app/application.py"

# Check running sessions
tmux ls

# Attach to session
tmux attach -t medical  # Use Ctrl+B then D to detach
```

## GCP Firewall Setup

```bash
gcloud compute firewall-rules create allow-medical-rag \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:8502 \
  --source-ranges=0.0.0.0/0
```

## Project Structure

```
week_6/
├── README.md
└── medical-rag/
    ├── requirements.txt
    ├── setup.py
    ├── Dockerfile
    ├── .env.example
    └── app/
        ├── application.py
        ├── components/
        │   ├── embeddings.py
        │   ├── llm.py
        │   ├── pdf_loader.py
        │   ├── retriever.py
        │   └── vector_store.py
        ├── config/
        │   └── config.py
        ├── common/
        │   ├── custom_exception.py
        │   └── logger.py
        └── templates/
            └── index.html
```

## Features

- **RAG-based Q&A:** Uses FAISS vector store for semantic search
- **Medical Knowledge Base:** Pre-loaded with medical information on flu, diabetes, hypertension, headaches, first aid
- **Session Management:** Maintains conversation history per session
- **Responsive UI:** Clean Flask-based web interface

## Technologies Used

- **LLM:** Groq (Llama 3.1 8B Instant)
- **Embeddings:** HuggingFace sentence-transformers/all-MiniLM-L6-v2
- **Vector Store:** FAISS
- **Framework:** Flask, LangChain
- **Deployment:** Google Cloud Platform (Compute Engine)
