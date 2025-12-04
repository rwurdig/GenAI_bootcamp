# Week 5 - Cloud AI Engineering

Three AI-powered applications for Cloud AI Engineering week.

## Projects

### 1. AI Anime Recommender (Day 2)
- **Tech Stack:** Streamlit, LangChain, ChromaDB, Groq LLM
- **Description:** Anime recommendation system using RAG with synopsis-based similarity search

### 2. Flipkart Product Recommender (Day 4)
- **Port:** 5000
- **Tech Stack:** Flask, LangChain, ChromaDB, Groq LLM
- **Description:** E-commerce chatbot that recommends products based on user queries using RAG

### 3. AI Travel Planner (Day 5)
- **Port:** 8501
- **Tech Stack:** Streamlit, LangChain, Groq LLM
- **Description:** Interactive travel itinerary generator that creates personalized travel plans

## Deployment URLs

| Project | URL |
|---------|-----|
| Flipkart Recommender | http://<EXTERNAL_IP>:5000 |
| AI Travel Planner | http://<EXTERNAL_IP>:8501 |

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

## Project Structure

```
week_5/
├── README.md
├── anime-recommender/          # Day 2: AI Anime Recommender
│   ├── app/
│   ├── config/
│   ├── data/
│   ├── pipeline/
│   ├── src/
│   └── utils/
├── flipkart-recommender/       # Day 4: Flipkart Product Recommender
│   ├── app.py
│   ├── flipkart/
│   ├── templates/
│   └── static/
└── ai-travel-planner/          # Day 5: AI Travel Planner
    ├── app.py
    └── src/
```

## Technologies Used

- **LLM:** Groq (Llama 3.1 8B Instant, Llama 3.3 70B Versatile)
- **Embeddings:** HuggingFace sentence-transformers/all-MiniLM-L6-v2
- **Vector Stores:** ChromaDB
- **Frameworks:** Flask, Streamlit, LangChain
- **Deployment:** Google Cloud Platform (Compute Engine)
