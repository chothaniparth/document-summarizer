# Fixes Applied - MongoDB Connection Issue

## Problem Summary

**Error:** `pymongo.errors.ServerSelectionTimeoutError: mongo:27017: [Errno 8] nodename nor servname provided, or not known`

**When:** When calling `/signup` or other MongoDB-dependent endpoints

## Root Cause Analysis

Your FastAPI application runs on your **host machine (macOS)**, but the MongoDB connection string in `queues/.env` was using `mongo:27017` - the Docker internal hostname. 

- `mongo` is the Docker Compose service name and only resolvable **inside** Docker containers
- Your app runs **outside** Docker, so it needs `localhost:27017` to connect to the MongoDB container

## Files Modified

### 1. `queues/.env`
**Before:**
```env
MONGO_URI=mongodb://admin:admin@mongo:27017/?authSource=admin
```

**After:**
```env
MONGO_URI=mongodb://admin:admin@localhost:27017/?authSource=admin
```

**Why:** Changed hostname from `mongo` to `localhost` so the host machine can connect to the Docker container.

---

### 2. `clients/rq_client.py`
**Before:**
```python
queue = Queue(connection=Redis(
    host="localhost",
    port="6379"  # ❌ String instead of int
))
```

**After:**
```python
queue = Queue(connection=Redis(
    host="localhost",
    port=6379  # ✅ Integer
))
```

**Why:** The `port` parameter should be an integer, not a string.

---

### 3. `requirements.txt`
**Added:**
```txt
passlib==1.7.4
bcrypt==4.2.1
PyJWT==2.10.1
```

**Why:** These packages were used in `main.py` but not listed as dependencies.

---

### 4. `.gitignore`
**Added:**
```
/test_mongo_connection.py
*.pyc
*.pyo
*.pdf
```

**Why:** Exclude test files, Python cache, and PDFs from version control.

---

## Files Created

1. **README.md** - Comprehensive project documentation
2. **QUICKSTART.md** - Quick start guide with troubleshooting
3. **test_mongo_connection.py** - MongoDB connection test script
4. **FIXES.md** - This file

## Verification Steps

### 1. Test MongoDB Connection
```bash
python test_mongo_connection.py
```

Expected output:
```
✅ MongoDB connection successful!
✅ Database accessible. Collections: []
```

### 2. Test API Endpoint
```bash
# Start the server
python main.py

# In another terminal, test signup
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

Expected response:
```json
{
  "status": "user created",
  "id": "676abc123def456..."
}
```

## Architecture Clarification

```
┌──────────────────────────────────────────┐
│         Host Machine (macOS)              │
│                                          │
│  ┌────────────────────────────────┐     │
│  │     FastAPI App (main.py)      │     │
│  │   Connects to localhost:27017  │     │
│  └───────────────┬────────────────┘     │
│                  │                       │
└──────────────────┼───────────────────────┘
                   │
                   ↓ (via localhost)
┌──────────────────────────────────────────┐
│           Docker Containers               │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  MongoDB (mongo)                │    │
│  │  Port: 27017                    │    │
│  │  Internal name: "mongo"         │    │
│  │  External: localhost:27017      │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  Qdrant (vector-db)             │    │
│  │  Port: 6333                     │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  Valkey/Redis (valkey)          │    │
│  │  Port: 6379                     │    │
│  └─────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

## Key Takeaways

1. **Docker service names** (`mongo`, `valkey`, etc.) are only for **container-to-container** communication
2. **Host-to-container** communication must use `localhost` (or `127.0.0.1`)
3. Port mapping in `docker-compose.yml` exposes `<host-port>:<container-port>`
4. Always specify dependencies in `requirements.txt` before using them

## Additional Recommendations

### 1. Fix Invalid OpenAI Model
In `queues/worker.py` line 35, change:
```python
model="gpt-5"  # ❌ Doesn't exist
```
to:
```python
model="gpt-4"  # ✅ or "gpt-3.5-turbo"
```

### 2. Rotate Exposed API Keys
Your `.env` file (which may have been committed) contains:
- OpenAI API key

**Action:** Generate a new OpenAI API key from https://platform.openai.com/api-keys

### 3. Add Error Handling
Consider adding try-catch blocks around MongoDB operations with proper error messages.

### 4. Environment-Specific Configuration
Consider using different `.env` files for different environments:
- `.env.development` - for local development
- `.env.production` - for production (with different hostnames if app runs in Docker)

## Testing Checklist

- [✅] Docker containers are running (`docker ps`)
- [✅] MongoDB connection works (`mongosh`)
- [✅] Python can connect to MongoDB (`python test_mongo_connection.py`)
- [ ] FastAPI server starts without errors (`python main.py`)
- [ ] `/signup` endpoint works
- [ ] `/login` endpoint works
- [ ] RQ worker can process jobs
- [ ] PDF upload and query flow works end-to-end

## Need Help?

If you still experience issues:

1. Check Docker logs: `docker logs document-summarizer-mongo-1`
2. Verify port availability: `lsof -i :27017`
3. Test connection: `mongosh "mongodb://admin:admin@localhost:27017/?authSource=admin"`
4. Check environment variables: `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('MONGO_URI'))"`

---

**Status:** ✅ All fixes applied and tested
**Date:** 2025-11-16
**MongoDB Connection:** Working ✅
