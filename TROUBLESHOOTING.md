# Troubleshooting Guide

## Port Already in Use

If you get "port already in use" errors:

```bash
# Find process using port 3000 (frontend)
lsof -i :3000
# Kill it
kill -9 <PID>

# Or use docker directly
docker-compose down
```

## Database Connection Issues

**Error:** `could not connect to server: Connection refused`

- Wait 30 seconds for PostgreSQL to start
- Check PostgreSQL logs: `docker-compose logs db`
- Restart: `docker-compose restart db`

## OPENAI_API_KEY Not Set

1. Get key from https://platform.openai.com/api-keys
2. Add to `backend/.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
3. Restart: `docker-compose restart backend`

## Frontend Not Loading

**Problem:** Blank page or 502 error

1. Check backend is running: `curl http://localhost:8000/health`
2. Check logs: `docker-compose logs frontend`
3. Rebuild frontend: `docker-compose up --build frontend`

## Transcription Taking Too Long

- First run downloads Whisper model (~3GB)
- Subsequent transcriptions are faster
- Check logs: `docker-compose logs celery_worker`
- Use smaller model in `.env`: `WHISPER_MODEL=tiny` (faster, less accurate)

## Chroma Connection Error

```
chromadb.errors.InvalidDimensionException
```

- Restart Chroma: `docker-compose restart chroma`
- Clear Chroma data: `docker-compose down -v && docker-compose up`

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend
```

## Reset Everything

```bash
# Stop and clean up
bash clean.sh

# Start fresh
bash start.sh
```

## Memory Issues

If containers keep crashing:

1. Increase Docker memory: Docker Desktop → Settings → Resources
2. Use smaller Whisper model: `WHISPER_MODEL=tiny`

## Database Schema Migration

If you modify models in `backend/app/models/database.py`:

```bash
# Connect to container
docker-compose exec backend bash

# Create migration
alembic revision --autogenerate -m "your migration message"

# Apply migration
alembic upgrade head
```

## Test Upload

```bash
# Create a test file
echo "test audio content" > test.mp3

# Upload
curl -F "file=@test.mp3" http://localhost:8000/api/documents/upload
```
