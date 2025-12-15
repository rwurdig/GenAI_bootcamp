# Study Buddy AI (Week 7)

A simple **RAG-based** Study Buddy built with **Streamlit + Groq**.

## Local Run

```bash
cd week_7/study-buddy-ai
cp .env.example .env
# edit .env and set GROQ_API_KEY

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

streamlit run application.py --server.address=0.0.0.0 --server.port=8501
```

Open:
- `http://localhost:8501`

## Docker

```bash
docker build -t study-buddy-ai:local .
docker run --rm -p 8501:8501 --env-file .env study-buddy-ai:local
```

## Kubernetes (Minikube)

Create the secret:

```bash
kubectl create secret generic groq-api-secret \
  --from-literal=GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

Deploy:

```bash
kubectl apply -f manifest/
```

Port-forward to match the guide:

```bash
kubectl port-forward svc/study-buddy-service 8501:80
```

## Notes

- The app supports **paste notes** or **upload PDF/TXT**, then Q&A over indexed chunks.
- `.env` is gitignored; use `.env.example` as template.
