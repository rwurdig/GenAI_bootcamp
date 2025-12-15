# Study Buddy AI (Week 7)

Streamlit app with:
- Provider/model selection (Groq or OpenAI)
- Persona-based chat
- Quiz generator (MCQ or open-ended) with JSON + Pydantic validation

## Local Run

```bash
cd week_7/study-buddy-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# set at least one of these
export GROQ_API_KEY="..."
export OPENAI_API_KEY="..."

streamlit run streamlit_app.py
```

## Docker

```bash
docker build -t study-buddy-ai:local week_7/study-buddy-ai
docker run --rm -p 8501:8501 -e GROQ_API_KEY="..." study-buddy-ai:local
```

## Kubernetes + ArgoCD

Manifests live in `week_7/study-buddy-ai/manifests/`.

```bash
kubectl apply -f week_7/study-buddy-ai/manifests/namespace.yaml

kubectl create secret generic study-buddy-secrets \
  -n study-buddy \
  --from-literal=GROQ_API_KEY="YOUR_GROQ_KEY" \
  --from-literal=OPENAI_API_KEY="YOUR_OPENAI_KEY"

kubectl apply -f week_7/study-buddy-ai/manifests/deployment.yaml
kubectl apply -f week_7/study-buddy-ai/manifests/service.yaml
```
