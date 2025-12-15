# Study Buddy AI

Week 7 project for Andela GenAI Bootcamp. Quiz generator + chat with persona selection.

## Features
- Provider/model selection (Groq, OpenAI)
- 3 chat personas (Study Buddy, Socratic Tutor, Exam Coach)
- MCQ and open-ended quiz generation
- Pydantic validation for quiz JSON

## Run locally
```bash
cd week_7/study-buddy-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export GROQ_API_KEY="..."
# optional: export OPENAI_API_KEY="..."

streamlit run streamlit_app.py
```

## Docker
```bash
docker build -t study-buddy:local .
docker run --rm -p 8501:8501 -e GROQ_API_KEY="..." study-buddy:local
```

## K8s deployment

Manifests in `manifests/`. Uses ArgoCD for GitOps.
```bash
kubectl apply -f manifests/namespace.yaml

kubectl create secret generic study-buddy-secrets \
  -n study-buddy \
  --from-literal=GROQ_API_KEY="..." \
  --from-literal=OPENAI_API_KEY="..."

kubectl apply -f manifests/
```

## Stack
- LangChain + Groq/OpenAI
- Streamlit frontend
- Docker + Minikube + ArgoCD
