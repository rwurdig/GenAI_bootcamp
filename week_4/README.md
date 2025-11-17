# Week 4 · Agentic AI Blog Generator

Streamlit interface + LangGraph workflow that creates SEO-ready blog posts using a single LLM provider (Groq or OpenAI).

## ✨ Features

- Graph-based workflow: title node → content node
- Markdown output with download button
- Multi-language support (English, Spanish, French, Portuguese)
- Provider switcher (Groq or OpenAI) with extended model list
- Auto-load API keys from `.env` (no typing necessary) with optional override field

## 🧱 Project Structure

```text
week_4/
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── src/
    ├── states/blogstate.py
    ├── llms/groq_llm.py
    ├── nodes/blog_node.py
    └── graphs/graph_builder.py
```

## ⚙️ Setup

```bash
cd week_4
uv venv  # or python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt  # or pip install -r requirements.txt
cp .env.example .env

## ▶️ Run

```bash
streamlit run streamlit_app.py
```

1. Pick provider + model in the sidebar
2. Confirm the app detected your API key from `.env` (or override it manually if needed)
3. Enter the topic and language
4. Click **Generate Blog**
5. Read or download the Markdown output

## 📦 Submission Notes

- Single Streamlit app + LangGraph backend per week 4 requirements
- Uses one model provider per run (select in sidebar)

