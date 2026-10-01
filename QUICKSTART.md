# Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- OpenAI API key (https://platform.openai.com/api-keys)
- 10GB free disk space (for models)
- 8GB RAM

## Setup (2 minutes)

```bash
# 1. Clone
git clone https://github.com/Ashifdecoder/video-document-rag-chatbot
cd video-document-rag-chatbot

# 2. Create backend config
cp backend/.env.example backend/.env

# 3. Add your OpenAI key to backend/.env
# Edit backend/.env and set: OPENAI_API_KEY=sk-your-key-here

# 4. Start everything
bash start.sh
# Or manually: docker-compose up --build
```

## Access

Wait 1-2 minutes for startup (models download on first run).

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Task Monitor:** http://localhost:5555 (Flower)

## Usage

1. **Upload media:** Click the upload box, select MP4/MP3/etc, give it a title
2. **Wait for transcription:** Status updates in real-time
3. **Chat:** Ask questions about the media content
4. **See sources:** Each answer includes timestamped excerpts

## Stop

```bash
bash stop.sh
```

## Troubleshooting

See `TROUBLESHOOTING.md`

## Reset Everything

```bash
bash clean.sh
bash start.sh
```
