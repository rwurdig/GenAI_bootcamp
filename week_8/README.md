---
title: SuperTech Store Customer Support
emoji: 🛍️
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
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
- **Backend Tools:** MCP (Model Context Protocol)
- **UI:** Streamlit

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
GROQ_API_KEY=gsk_your_groq_api_key_here
ENABLE_DUMMY_DATA=1
```

## Demo Test Customers (Optional)

If you set `ENABLE_DUMMY_DATA=1`, the app will accept the following **demo** email/PIN pairs for the **👤 My Orders** flow:

- donaldgarcia@example.net / 7912
- michellejames@example.com / 1520
- laurahenderson@example.org / 1488
- spenceamanda@example.org / 2535
- glee@example.net / 4582
- williamsthomas@example.net / 4811
- justin78@example.net / 9279
- jason31@example.com / 1434
- samuel81@example.com / 4257
- williamleon@example.net / 9928

When demo data is enabled, the PIN is validated locally (so it is not required to be verified by the MCP server).

Run locally:

```bash
streamlit run app.py
```

Open http://localhost:8501

## Deployment to HuggingFace Spaces

1. Create a new Space (SDK: Streamlit)
2. Upload `app.py`, `requirements.txt`, `README.md`
3. In Space Settings → Secrets, add `GROQ_API_KEY`
4. Wait for the build to complete

## Project Structure

```
.
├── app.py
├── requirements.txt
├── README.md
└── .env
```
