# Week 3 — Unified Streamlit App (News ▪ YouTube ▪ Voice RAG)

This repo contains a single Streamlit application with three tools:

1. **News Article Summarizer** — fetch & summarize articles via newspaper3k/Trafilatura and LangChain (map‑reduce).
2. **YouTube Summarizer + Q&A** — download/transcribe via yt‑dlp + Whisper, summarize (map‑reduce), build a vector index for Q&A.
3. **Voice RAG Assistant** — upload PDFs/TXT/MD, build a persistent Chroma vector store, ask by **voice** (Whisper STT) or text, respond with **ElevenLabs TTS**.

---

## 🧱 Project Structure

```
week_3_unified_app/
├── streamlit_app.py
├── requirements.txt
├── .env.example
├── downloads/                       # audio/video scratch
└── src/
    ├── utils/
    │   ├── llm.py                   # LLM & embeddings factory
    │   ├── text.py                  # chunking & helpers
    │   ├── news.py                  # article fetchers
    │   ├── youtube.py               # YT download/transcript/whisper
    │   └── audio.py                 # mic/file -> wav; whisper STT; elevenlabs TTS
    ├── summarizers/
    │   ├── news.py                  # NewsArticleSummarizer
    │   └── youtube.py               # YoutubeVideoSummarizer
    └── rag/
        ├── indexer.py               # ingest & persist Chroma
        └── qa.py                    # retrieval + answer
```

---

## ⚙️ Setup

1) **Python & FFmpeg**  
- Python **3.11+** recommended  
- Install FFmpeg (macOS: `brew install ffmpeg`; Ubuntu: `sudo apt install ffmpeg`; Windows: download FFmpeg and add to PATH).

2) **Create venv & install deps**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) **Environment variables**  
Copy `.env.example` to `.env` and fill values.  

- Set `OPENAI_API_KEY` (works for OpenAI *or* compatible proxies such as AIMLAPI).
- Optional: set `OPENAI_BASE_URL` if you are routing through a proxy like AIMLAPI.

---

## ▶️ Run

```bash
streamlit run streamlit_app.py
```

- **Tab 1 — News**: paste an article URL, select provider/model/summary style, click **Summarize**.
- **Tab 2 — YouTube**: paste a YouTube URL, click **Process** → gets transcript or downloads audio and transcribes via Whisper → summary + Q&A chat.
- **Tab 3 — Voice RAG**: upload PDFs/TXT/MD, click **Index**. Then record or upload a short audio question (or type), get grounded answer + optional TTS replay.

> Vector store is persisted under `.chroma/` inside the project folder so subsequent runs load instantly.

---

## 🧪 Notes & Troubleshooting

- **Whisper first run** downloads the model; be patient.
- If **SSL** issues appear behind corporate proxies, set `SSL_VERIFY=false` in `.env` (dev only).
- If **yt‑dlp** fails for a video, try another URL or ensure FFmpeg is available on PATH.
- If **mic recorder** fails, the app falls back to file upload; or install `streamlit-mic-recorder`.

---

