# Document Summarizer

A FastAPI-based document processing and question-answering system that uses RAG (Retrieval Augmented Generation) to answer queries about uploaded PDF documents.

## Features

- 📄 PDF document upload and processing
- 🔍 Semantic search using Qdrant vector database
- 🤖 AI-powered question answering using OpenAI's GPT
- 👤 User authentication (signup/login) with JWT
- 📝 Document chunking and embedding
- 🚀 Background job processing with RQ (Redis Queue)
- 🔐 Password hashing with bcrypt

## Tech Stack

- **FastAPI** - Web framework
- **MongoDB** - User and document metadata storage
- **Qdrant** - Vector database for embeddings
- **Redis/Valkey** - Job queue management
- **OpenAI** - Embeddings and chat completions
- **LangChain** - Document processing and RAG pipeline
- **Motor** - Async MongoDB driver
- **RQ** - Background job processing

## Prerequisites

- Python 3.13+
- Docker and Docker Compose
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd document-summarizer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MONGO_URI=mongodb://admin:admin@localhost:27017/?authSource=admin
   MONGO_DB_NAME=document_summarizer
   JWT_SECRET=your_secret_key_here
   ```

5. **Start Docker services**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - MongoDB (port 27017)
   - Qdrant vector database (port 6333)
   - Valkey/Redis (port 6379)

6. **Verify Docker containers are running**
   ```bash
   docker ps
   ```

## Usage

### Starting the Application

1. **Start the FastAPI server**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the RQ worker** (in a separate terminal)
   ```bash
   cd queues
   rq worker --with-scheduler
   ```

### API Endpoints

#### Health Check
```bash
GET /
```

#### User Authentication

**Signup**
```bash
POST /signup
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Login**
```bash
POST /login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### Document Processing

**Upload PDF**
```bash
POST /save-file/
Content-Type: multipart/form-data

file: <pdf-file>
UserId: <user-id>
DocumentId: <document-id>
```

This endpoint:
- Saves the PDF file
- Extracts text and splits into chunks
- Generates embeddings
- Stores vectors in Qdrant

#### Query Documents

**Submit Query** (async - returns job ID)
```bash
POST /query
Content-Type: application/json

{
  "query": "What is the main topic of the document?"
}
```

**Get Query Result**
```bash
GET /getResult?job_id=<job-id>
```

### Example Workflow

```bash
# 1. Sign up
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"pass123"}'

# 2. Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# 3. Upload a PDF
curl -X POST http://localhost:8000/save-file/ \
  -F "file=@document.pdf" \
  -F "UserId=user123" \
  -F "DocumentId=doc456"

# 4. Query the document
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Summarize the key points"}'

# 5. Get the result (use the job_id from step 4)
curl http://localhost:8000/getResult?job_id=<job-id>
```

## Project Structure

```
document-summarizer/
├── main.py                 # FastAPI application and routes
├── docker-compose.yml      # Docker services configuration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── clients/
│   ├── __init__.py
│   └── rq_client.py       # Redis Queue client setup
└── queues/
    ├── __init__.py
    ├── .env               # Worker-specific env vars
    └── worker.py          # Background job processing
```

## Troubleshooting

### MongoDB Connection Issues

If you see `ServerSelectionTimeoutError` or connection timeout errors:

1. **Verify Docker containers are running**
   ```bash
   docker ps
   ```

2. **Check MongoDB logs**
   ```bash
   docker logs <mongodb-container-id>
   ```

3. **Ensure MongoDB URI is correct**
   - For running on host machine: `mongodb://admin:admin@localhost:27017/?authSource=admin`
   - For running inside Docker: `mongodb://admin:admin@mongo:27017/?authSource=admin`

4. **Test MongoDB connection**
   ```bash
   mongosh "mongodb://admin:admin@localhost:27017/?authSource=admin"
   ```

### Common Issues

**Port conflicts**
- Make sure ports 6333, 6379, and 27017 are not in use
- Check with: `lsof -i :6333` (and 6379, 27017)

**OpenAI API errors**
- Verify your API key is valid
- Check OpenAI rate limits and quotas
- Note: The code uses `gpt-5` which should be updated to a valid model like `gpt-4` or `gpt-3.5-turbo`

**RQ Worker not processing jobs**
- Make sure the worker is running: `rq worker --with-scheduler`
- Check Redis/Valkey is running: `docker ps | grep valkey`

## Development

### Running Tests
```bash
# Add your test command here
pytest
```

### Code Style
```bash
# Add linting commands here
ruff check .
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings and chat | Required |
| `MONGO_URI` | MongoDB connection string | `mongodb://admin:admin@localhost:27017/?authSource=admin` |
| `MONGO_DB_NAME` | MongoDB database name | `document_summarizer` |
| `JWT_SECRET` | Secret key for JWT token generation | Required |

## Docker Services

### MongoDB
- **Port**: 27017
- **Username**: admin
- **Password**: admin
- **Volume**: `mongo_data`

### Qdrant
- **Port**: 6333
- **Web UI**: http://localhost:6333/dashboard
- **Volume**: `qdrant_storage`

### Valkey (Redis)
- **Port**: 6379

## Security Notes

⚠️ **Important**: 
- Change default MongoDB credentials in production
- Use strong JWT secrets
- Never commit `.env` files to version control
- The current `.env` file contains exposed API keys - regenerate them immediately

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]
