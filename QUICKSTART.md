# Quick Start Guide

## The Problem You Had

You were getting a `ServerSelectionTimeoutError` with MongoDB trying to connect to `mongo:27017` instead of `localhost:27017`.

### Root Cause
The file `queues/.env` had `MONGO_URI=mongodb://admin:admin@mongo:27017/...` which is the Docker internal hostname, but your FastAPI app runs on your host machine (macOS), not inside a Docker container. The host machine needs to use `localhost:27017`.

### What Was Fixed
1. ✅ Changed `queues/.env` MongoDB URI from `mongo:27017` to `localhost:27017`
2. ✅ Fixed Redis port type in `clients/rq_client.py` (was string `"6379"`, now int `6379`)
3. ✅ Added missing dependencies to `requirements.txt`: `passlib`, `bcrypt`, `PyJWT`
4. ✅ Created comprehensive README.md
5. ✅ Updated .gitignore

## Start Your Application (3 Steps)

### 1. Ensure Docker Services Are Running
```bash
docker-compose up -d
docker ps  # Verify all 3 services are up
```

### 2. Start FastAPI Server
```bash
python main.py
```

The server should start without errors at `http://localhost:8000`

### 3. Start RQ Worker (in a new terminal)
```bash
cd queues
source ../venv/bin/activate  # Activate your virtual environment
rq worker --with-scheduler
```

## Test the /signup Endpoint

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

Expected response:
```json
{
  "status": "user created",
  "id": "some-mongodb-id"
}
```

## Verify Everything Works

Run the test script:
```bash
python test_mongo_connection.py
```

You should see:
```
✅ MongoDB connection successful!
✅ Database accessible. Collections: []
```

## Common Commands

**Stop all services:**
```bash
docker-compose down
```

**View logs:**
```bash
docker logs document-summarizer-mongo-1
docker logs document-summarizer-vector-db-1
docker logs document-summarizer-valkey-1
```

**Check MongoDB directly:**
```bash
mongosh "mongodb://admin:admin@localhost:27017/?authSource=admin"
```

## Architecture Overview

```
┌─────────────────┐
│   FastAPI App   │ ← Runs on host (localhost:8000)
│   (main.py)     │
└────────┬────────┘
         │
         ├─────────► MongoDB (localhost:27017)
         │          [Docker container]
         │
         ├─────────► Qdrant (localhost:6333)
         │          [Docker container]
         │
         └─────────► Redis/Valkey (localhost:6379)
                    [Docker container]
                    ↓
              ┌──────────────┐
              │  RQ Worker   │
              │ (worker.py)  │
              └──────────────┘
```

## Important Notes

⚠️ **Your .env file contains exposed API keys!** 
- Rotate your OpenAI API key immediately
- Never commit `.env` files to git

🔧 **Model Issue:**
The code uses `gpt-5` which doesn't exist. Update to `gpt-4` or `gpt-3.5-turbo` in:
- `queues/worker.py` line 35

## Next Steps

1. Update the OpenAI model name in `worker.py`
2. Rotate your exposed API keys
3. Upload a PDF and test the full workflow
4. Add proper error handling and validation

## Need Help?

Check the main [README.md](README.md) for detailed documentation.
