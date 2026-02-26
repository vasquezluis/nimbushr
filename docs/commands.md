# Commands

## Setup

```bash
cd backend
uv venv
uv sync
cp .env.example .env   # add OPENAI_API_KEY
```

## Ingest documents

```bash
# Place files in backend/data/pdfs|excels|texts, then:
cd backend
uv run python -m app.ingest
```

## Run backend

```bash
cd backend
uv run uvicorn app.main:app --reload
# http://localhost:8000
# http://localhost:8000/docs
```

## Run frontend

```bash
cd frontend
pnpm install
pnpm run dev
# http://localhost:3000
```

## Key env vars (.env)

```
OPENAI_API_KEY=sk-...

# Optional overrides
USE_AI_SUMMARIZATION=false   # disable to save cost during testing
PDF_STRATEGY=fast             # fast | hi_res | ocr_only
TOP_K_CHUNKS=3
USE_RERANKING=true
```
