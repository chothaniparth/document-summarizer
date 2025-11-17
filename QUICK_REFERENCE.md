# Quick Reference - Vector Schema Implementation

## ✅ What Changed

### Critical Fix: Metadata Filtering
```python
# ❌ BEFORE (Wrong - wouldn't filter)
key="UserId"

# ✅ AFTER (Correct)
key="metadata.UserId"
```

### Other Fixes
- ✅ Added Qdrant schema initialization
- ✅ Created payload indexes for fast filtering  
- ✅ Fixed GPT model from `gpt-5` to `gpt-4o-mini`
- ✅ Added `k=5` for top-5 retrieval

---

## 📝 Schema Structure

```json
{
  "vector": [3072 dimensions],
  "payload": {
    "page_content": "text...",
    "metadata": {
      "UserId": "user_id",
      "DocumentId": "doc_id",
      "source": "/path/to/file.pdf",
      "page": 1,
      "page_label": "1"
    }
  }
}
```

**Indexed Fields:**
- `metadata.UserId` (KEYWORD)
- `metadata.DocumentId` (KEYWORD)

---

## 🚀 Quick Start

### 1. Start Server
```bash
python main.py
```

Look for:
```
✅ Created collection: learning_rag
✅ Created payload indexes for UserId and DocumentId
```

### 2. Test Schema
```bash
python test_qdrant_schema.py
```

### 3. Upload Document
```bash
curl -X POST http://localhost:8000/save-file/ \
  -F "file=@document.pdf" \
  -F "UserId=USER_ID"
```

Response:
```json
{
  "documentId": "DOC_ID",
  "saved_file": "...",
  "pages": 10,
  "chunks": 45
}
```

### 4. Query Document
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your question?",
    "UserId": "USER_ID",
    "DocumentId": "DOC_ID"
  }'
```

### 5. Get Result
```bash
curl http://localhost:8000/getResult?job_id=JOB_ID
```

---

## 🔍 Key Points

1. **Always use `metadata.` prefix** in filters
2. **Collection auto-creates** on server startup
3. **Indexes enable fast** multi-user filtering
4. **Each user isolated** by UserId
5. **Top-5 chunks** retrieved per query

---

## 📚 Documentation Files

- **VECTOR_SCHEMA.md** - Full schema documentation
- **SCHEMA_CHANGES.md** - Detailed change log
- **QUICK_REFERENCE.md** - This file (you are here)
- **test_qdrant_schema.py** - Schema verification script

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No results | Check filter uses `metadata.UserId` |
| Slow queries | Indexes created? Check logs |
| GPT errors | Model is `gpt-4o-mini`, API key set? |
| Collection missing | Start server to auto-create |

---

## 📊 Qdrant Dashboard

View your data: **http://localhost:6333/dashboard**

---

**Status:** ✅ Production Ready  
**Last Updated:** 2025-11-17
