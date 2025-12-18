---
title: SuperTech Store Customer Support
emoji: 🛍️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8501
pinned: false
---

# SuperTech Store Customer Support Chatbot

AI-powered customer support chatbot for SuperTech Store, a computer products retailer.

## Features

- 📦 Order tracking and status
- 🛒 Product catalog browsing
- 🔍 Product search
- ↩️ Return policy information
- 💬 Natural language support

## Tech Stack

- **LLM:** Groq (Llama 3.1 8B Instant)
- **UI:** Streamlit
- **Container:** Docker (Hugging Face Space)

## Local Development

### Prerequisites

- Python 3.10+
- Groq API Key (free at https://console.groq.com/keys)

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a local `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Run locally:

```bash
streamlit run app.py
```

Open http://localhost:8501

## Deployment to HuggingFace Spaces

1. Create a new Space (SDK: Docker)
2. Upload `app.py`, `requirements.txt`, `Dockerfile`, `README.md`
3. In Space Settings → Secrets, add `GROQ_API_KEY`
4. Wait for the build to complete

## Project Structure

```
.
├── app.py
├── Dockerfile
├── requirements.txt
├── README.md
└── .env
```
