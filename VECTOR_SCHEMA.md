# Vector Store Schema Configuration

## Overview

This document explains the Qdrant vector store schema configuration for multi-user, multi-document RAG filtering.

## Schema Design

### Collection Configuration

**Collection Name:** `learning_rag`

**Vector Configuration:**
- **Dimension:** 3072 (OpenAI `text-embedding-3-large`)
- **Distance Metric:** COSINE

### Payload Schema

Each vector point stores the following metadata:

```json
{
  "page_content": "The actual text chunk...",
  "metadata": {
    "UserId": "user_mongodb_id",
    "DocumentId": "document_mongodb_id",
    "source": "/path/to/file.pdf",
    "page": 1,
    "page_label": "1"
  }
}
```

### Indexed Fields

For efficient filtering, the following fields are indexed:

1. **`metadata.UserId`** (KEYWORD)
   - Filters documents by user
   - Ensures users only see their own documents

2. **`metadata.DocumentId`** (KEYWORD)
   - Filters chunks by specific document
   - Enables document-specific queries

## How It Works

### 1. Document Upload (`/save-file/`)

```python
# Step 1: Save file and create MongoDB entry
file_path = ROOT_PATH / unique_name
doc_data = {
    "userId": UserId,
    "fileName": unique_name,
    "created_at": datetime.utcnow()
}
result = await db.documents.insert_one(doc_data)
DocumentId = str(result.inserted_id)

# Step 2: Load and chunk PDF
loader = PyPDFLoader(str(file_path))
docs = loader.load()

# Step 3: Add metadata to each chunk
for d in docs:
    d.metadata["UserId"] = UserId
    d.metadata["DocumentId"] = DocumentId

# Step 4: Create embeddings and store
chunks = splitter.split_documents(docs)
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    collection_name="learning_rag"
)
```

### 2. Query Processing (`/query`)

```python
# Filter by user and document
search_result = vector_db.similarity_search(
    query=body["query"],
    filter=Filter(
        must=[
            FieldCondition(
                key="metadata.UserId",
                match=MatchValue(value=body["UserId"])
            ),
            FieldCondition(
                key="metadata.DocumentId",
                match=MatchValue(value=body["DocumentId"])
            ),
        ]
    ),
    k=5  # Return top 5 relevant chunks
)
```

## Key Points

### ✅ Metadata Path

**IMPORTANT:** When filtering, use the full path:
- ✅ `metadata.UserId`
- ✅ `metadata.DocumentId`
- ❌ ~~`UserId`~~ (won't work)
- ❌ ~~`DocumentId`~~ (won't work)

LangChain stores metadata under the `metadata` key in the payload.

### ✅ Index Creation

Indexes are created automatically on startup via `init_qdrant_collection()`:

```python
qdrant_client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="metadata.UserId",
    field_schema=PayloadSchemaType.KEYWORD
)
```

### ✅ Multi-tenancy

Each user's documents are isolated:
1. User A uploads → `UserId="user_a_id"`
2. User B uploads → `UserId="user_b_id"`
3. User A queries → Only sees documents with `UserId="user_a_id"`

## API Request Examples

### Upload Document

```bash
curl -X POST http://localhost:8000/save-file/ \
  -F "file=@document.pdf" \
  -F "UserId=676abc123def456"
```

Response:
```json
{
  "documentId": "676xyz789ghi012",
  "saved_file": "20241117123456_document.pdf",
  "pages": 10,
  "chunks": 45
}
```

### Query Document

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "UserId": "676abc123def456",
    "DocumentId": "676xyz789ghi012"
  }'
```

Response:
```json
{
  "status": "query queued",
  "job_id": "abc-def-123"
}
```

### Get Result

```bash
curl http://localhost:8000/getResult?job_id=abc-def-123
```

Response:
```json
{
  "result": "Based on the document, the main topic is..."
}
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   User Uploads PDF                       │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Save file to disk            │
        │  Create MongoDB entry         │
        │  Get DocumentId               │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  Load PDF → Split chunks      │
        │  Add metadata:                │
        │    - UserId                   │
        │    - DocumentId               │
        │    - page, source, etc.       │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  Generate embeddings (3072D)  │
        │  Store in Qdrant              │
        │    Collection: learning_rag   │
        └───────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   User Queries Document                  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │  Generate query embedding     │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  Similarity search in Qdrant  │
        │  Filter by:                   │
        │    - metadata.UserId          │
        │    - metadata.DocumentId      │
        │  Return top 5 chunks          │
        └───────────┬───────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  Build context from chunks    │
        │  Send to GPT-4o-mini          │
        │  Return answer                │
        └───────────────────────────────┘
```

## Troubleshooting

### No Results Returned

**Problem:** Query returns empty results even though documents exist.

**Solutions:**

1. **Check filter keys**
   ```python
   # ✅ Correct
   key="metadata.UserId"
   
   # ❌ Wrong
   key="UserId"
   ```

2. **Verify metadata in vectors**
   ```python
   # Check in Qdrant dashboard: http://localhost:6333/dashboard
   # Or use API:
   from qdrant_client import QdrantClient
   client = QdrantClient(url="http://localhost:6333")
   points = client.scroll(collection_name="learning_rag", limit=1)
   print(points[0][0].payload)
   ```

3. **Check index exists**
   ```python
   collection_info = client.get_collection("learning_rag")
   print(collection_info.payload_schema)
   ```

### Slow Queries

**Problem:** Queries take too long.

**Solutions:**

1. Ensure indexes are created (automatically done on startup)
2. Reduce `k` parameter (number of results)
3. Use more specific queries

### Wrong Results

**Problem:** Results don't match the document content.

**Solutions:**

1. Adjust `chunk_size` and `chunk_overlap` in `RecursiveCharacterTextSplitter`
2. Increase `k` parameter to get more context
3. Improve the system prompt in the worker

## Best Practices

1. **Always filter by UserId** - Ensures data isolation
2. **Use specific DocumentId** - For document-specific queries
3. **Monitor collection size** - Large collections may need optimization
4. **Backup regularly** - Qdrant data is stored in Docker volumes
5. **Test with sample data** - Before production use

## Collection Management

### View Collection Info
```bash
curl http://localhost:6333/collections/learning_rag
```

### Delete Collection (⚠️ Dangerous)
```python
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
client.delete_collection("learning_rag")
```

### Recreate Collection
Restart your FastAPI server - `init_qdrant_collection()` will recreate it.

## Performance Metrics

**Text Embedding 3 Large:**
- Dimension: 3072
- Cost: $0.13 / 1M tokens
- Quality: High accuracy for semantic search

**Qdrant:**
- Fast filtering with indexes
- Cosine similarity for relevance
- Scales to millions of vectors

## Security Considerations

1. **User Isolation:** UserId filtering prevents data leakage
2. **Document Access:** Only document owners can query
3. **Authentication:** Implement JWT token validation (recommended)
4. **Rate Limiting:** Add rate limits to prevent abuse

---

**Last Updated:** 2025-11-17  
**Schema Version:** 1.0
