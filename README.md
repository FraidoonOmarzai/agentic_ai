<h1 align=center>Agentic AI Projects</h1>

```bash
conda create -n agent python -y
conda activate agentic_ai

pip install -U phidata openai duckduckgo-search
setx OPENAI_API_KEY sk-***
```

### 1st Projects

1. open docker destop and run the below codes to setup pgvector
```bash
docker run -d `
  -e POSTGRES_DB=ai `
  -e POSTGRES_USER=ai `
  -e POSTGRES_PASSWORD=ai `
  -e PGDATA=/var/lib/postgresql/data/pgdata `
  -v pgvolume:/var/lib/postgresql/data `
  -p 5532:5432 `
  --name pgvector `
  phidata/pgvector:16
```
