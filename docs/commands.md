# Comands

## Run commands

### ingest setup

```bash
(backend)
uv run python -m app.ingest
```

### query setup

```bash
(backend)
uv run python -m app.rag.query.query_pipeline
```

### fastapi

```bash
uv run uvicorn app.main:app --reload
```

```
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```
