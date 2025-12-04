# Week 5 - GenAI Projects Deployment

Three AI-powered applications deployed on Google Cloud Platform.

## Projects

### 1. Flipkart Product Recommender
- **Port:** 5000
- **Tech Stack:** Flask, LangChain, ChromaDB, Groq LLM
- **Description:** E-commerce chatbot that recommends products based on user queries using RAG (Retrieval Augmented Generation)

### 2. AI Travel Planner
- **Port:** 8501
- **Tech Stack:** Streamlit, LangChain, Groq LLM
- **Description:** Interactive travel itinerary generator that creates personalized travel plans

### 3. Medical RAG Chatbot
- **Port:** 8502
- **Tech Stack:** Flask, LangChain, FAISS, Groq LLM
- **Description:** Medical Q&A assistant that provides health information using RAG

## Deployment URLs

| Project | URL |
|---------|-----|
| Flipkart Recommender | http://<EXTERNAL_IP>:5000 |
| AI Travel Planner | http://<EXTERNAL_IP>:8501 |
| Medical RAG Chatbot | http://<EXTERNAL_IP>:8502 |

## Setup Instructions

### Prerequisites
- Python 3.10+
- Groq API Key (get it from https://console.groq.com/)

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/rwurdig/GenAI_bootcamp.git
cd GenAI_bootcamp/week_5
```

2. **Set up each project:**

```bash
# Flipkart Recommender
cd flipkart-recommender
python3 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your GROQ_API_KEY
python app.py
```

```bash
# AI Travel Planner
cd ai-travel-planner
python3 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your GROQ_API_KEY
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

```bash
# Medical RAG
cd medical-rag
python3 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env with your GROQ_API_KEY
python app/application.py
```

### Using tmux for Persistent Deployment

```bash
# Start Flipkart
tmux new-session -d -s flipkart "cd ~/projects/flipkart-recommender && source venv/bin/activate && python app.py"

# Start Travel Planner
tmux new-session -d -s travel "cd ~/projects/ai-travel-planner && source venv/bin/activate && streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true"

# Start Medical RAG
tmux new-session -d -s medical "cd ~/projects/medical-rag && source venv/bin/activate && python app/application.py"

# Check running sessions
tmux ls

# Attach to a session
tmux attach -t flipkart  # Use Ctrl+B then D to detach
```

## GCP Firewall Setup

Create a firewall rule to allow traffic to the application ports:

```bash
gcloud compute firewall-rules create allow-apps \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:5000,tcp:8501,tcp:8502 \
  --source-ranges=0.0.0.0/0
```

## Project Structure

```
week_5/
├── README.md
├── flipkart-recommender/
│   ├── app.py
│   ├── requirements.txt
│   ├── setup.py
│   ├── Dockerfile
│   ├── .env.example
│   ├── flipkart/
│   │   ├── config.py
│   │   ├── data_ingestion.py
│   │   └── rag_chain.py
│   ├── templates/
│   └── static/
├── ai-travel-planner/
│   ├── app.py
│   ├── requirements.txt
│   ├── setup.py
│   ├── Dockerfile
│   ├── .env.example
│   └── src/
│       ├── chains/
│       ├── config/
│       ├── core/
│       └── utils/
└── medical-rag/
    ├── requirements.txt
    ├── setup.py
    ├── Dockerfile
    ├── .env.example
    └── app/
        ├── application.py
        ├── components/
        ├── config/
        ├── common/
        └── templates/
```

## Technologies Used

- **LLM:** Groq (Llama 3.1 8B Instant, Llama 3.3 70B Versatile)
- **Embeddings:** HuggingFace sentence-transformers/all-MiniLM-L6-v2
- **Vector Stores:** ChromaDB, FAISS
- **Frameworks:** Flask, Streamlit, LangChain
- **Deployment:** Google Cloud Platform (Compute Engine)
