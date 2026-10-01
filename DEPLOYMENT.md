# Local and Render deployment

## Local

```bash
cp backend/.env.example backend/.env
# Set OPENAI_API_KEY in backend/.env
docker compose up --build
```

Open http://localhost:3000. The API is at http://localhost:8000/docs.

## Deploy

The repository includes `render.yaml`. In Render, create a Blueprint from this repository, then configure `OPENAI_API_KEY`, `DATABASE_URL`, `REDIS_URL`, `CHROMA_URL`, and the frontend `NEXT_PUBLIC_API_URL` using the deployed API URL.

The chatbot requires persistent PostgreSQL, Redis, and Chroma services. Do not use ephemeral storage for uploads or the vector database in production; use managed services or persistent disks.
