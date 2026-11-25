# Falcons Club Q&A

A Flask chatbot that answers club questions using the documents in `data/`, a FAISS similarity index, and the OpenAI API.

## Run locally

Requires Python 3.10+ and an OpenAI API key for generated answers. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"  # PowerShell: $env:OPENAI_API_KEY="your-key"
python scripts/build_index.py  # optional; the app builds a missing index on startup
python app.py
```

Open <http://127.0.0.1:5000>. The index is created from `.txt` files in `data/`; generated `data/index.faiss` and `data/chunks.json` are not committed. Without an API key the app can still return a retrieved source passage, but does not generate an LLM response.

## Deployment and live demo

The Render Blueprint is in [`render.yaml`](render.yaml). To deploy, create a Render account, connect this GitHub repository, and create a new Blueprint from it. Render installs `requirements.txt`, builds the FAISS index during the build, then starts the Flask app with Gunicorn. The app loads the index before serving requests and exposes `/healthz` for health checks. Set `OPENAI_API_KEY` as a secret in the Render service environment; never commit the key. `OPENAI_MODEL` defaults to `gpt-4o-mini`.

**Live demo:** Not deployed or verified yet. After the first successful Render deployment, add the service's public `https://…onrender.com` URL here. This repository configuration alone does not create a Render account, connect the service, or publish a live URL.

## Costs and club usage

The Render Blueprint requests the free web-service plan where available, but free-tier availability, quotas, and behavior can change. Free hosting is not a guarantee of zero cost or continuous availability. OpenAI API usage is billed separately according to the account's current model pricing; monitor its usage and set provider-side spending limits. Club usage is for reasonable, occasional questions about club information. Questions are limited to 1,000 characters, but there is currently no per-member authentication or query quota—do not treat this public demo as a private or access-controlled service.

## Limitations & Safety

Answers can be incorrect or hallucinated; check important details against official club documents or ask a club administrator. Do not use this assistant for medical or legal advice, emergencies, or sensitive personal information. The demo only knows the documents supplied in `data/`, which may be incomplete or out of date.
