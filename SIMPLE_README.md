# 📄 Document Q&A with Hugging Face

A lightweight, single-page Streamlit application for asking questions about PDF documents using Hugging Face language models.

## 🎯 Features

- **Simple & Fast**: Single-page Streamlit application
- **No Authentication**: Session-based user identification (no database required)
- **PDF Processing**: Extract text from PDF files instantly
- **AI-Powered Q&A**: Uses Hugging Face transformers for question answering
- **Vector Search**: Sentence Transformers for semantic search with Qdrant
- **Privacy-First**: No documents or chats stored permanently
- **No External APIs**: Uses open-source models (no OpenAI or Google Gemini)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OR Python 3.11+ with pip

### Option 1: Docker (Recommended)

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8501`

### Option 2: Local Python

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Qdrant (required for vector storage):
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

4. Run the application:
```bash
streamlit run streamlit_app.py
```

The application will be available at `http://localhost:8501`

## 📖 How to Use

### 1. Upload a PDF
- Go to **"📤 Upload & Index"** tab
- Upload a PDF file
- Click **"🚀 Process & Index Document"**
- Wait for the system to extract text and create embeddings

### 2. Ask Questions
- Go to **"💬 Ask Questions"** tab
- Select your uploaded document
- Type your question (e.g., "What are the main topics?")
- Click **"🔍 Get Answer"**
- Get AI-powered answers with source context

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│        Streamlit Frontend               │
│  - PDF Upload                           │
│  - Question Input                       │
│  - Answer Display                       │
└────────────┬────────────────────────────┘
             │
             ├──────────────────────────────────┐
             │                                  │
    ┌────────▼─────────┐          ┌───────────▼──────┐
    │ Sentence         │          │  Qdrant Vector   │
    │ Transformers     │          │  Database        │
    │ (Embeddings)     │          │                  │
    └────────┬─────────┘          └──────────────────┘
             │
    ┌────────▼──────────────────┐
    │ Hugging Face Q&A          │
    │ (deepset/roberta-base)    │
    └──────────────────────────┘
```

## 📦 Dependencies

- **Streamlit**: Web framework
- **Sentence Transformers**: Embedding models
- **Transformers**: Hugging Face models
- **Qdrant**: Vector database
- **PyPDF2**: PDF parsing
- **PyTorch**: ML framework

## 🔒 Privacy & Security

- ✅ No user management database
- ✅ No document storage on server
- ✅ No chat history stored
- ✅ Session data cleared after browser close
- ✅ All processing local (no external API calls to commercial services)
- ✅ Uses open-source models only

## ⚙️ Configuration

Edit `.env` file to change Qdrant connection:
```
QDRANT_URL=http://localhost:6333
```

For Docker, set `QDRANT_URL=http://vector-db:6333`

## 🤖 Models Used

- **Embeddings**: `all-MiniLM-L6-v2` (Sentence Transformers)
  - 384-dimensional embeddings
  - Fast and efficient
  
- **Q&A**: `deepset/roberta-base-squad2` (Hugging Face Transformers)
  - Fine-tuned for reading comprehension
  - No external API required

## 📝 Example Questions

- "What is the main topic?"
- "Summarize the key points"
- "Who are the main characters?"
- "What are the conclusions?"
- "List the important dates mentioned"

## 🐛 Troubleshooting

### Qdrant Connection Error
```
Error: Failed to connect to Qdrant at http://localhost:6333
```
**Solution**: Make sure Qdrant is running. If using Docker Compose, ensure the service started:
```bash
docker-compose ps
docker-compose logs vector-db
```

### PDF Processing Error
```
Error reading PDF
```
**Solution**: Ensure the PDF file is valid and not corrupted

### Out of Memory
If processing large PDFs:
- Break into smaller PDFs
- Restart the application
- Increase Docker memory limit

## 🚀 Performance Tips

1. **Smaller PDFs**: Process faster, better results
2. **Specific Questions**: More accurate answers than vague ones
3. **Local Deployment**: Run on machine with GPU for faster embeddings
4. **Batch Processing**: Upload multiple documents and compare answers

## 📚 Project Structure

```
├── streamlit_app.py          # Main application
├── requirements.txt          # Python dependencies
├── dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── .env                      # Environment variables
└── README.md                 # This file
```

## 🔄 Workflow

1. **Extract**: PDF → Text extraction via PyPDF2
2. **Split**: Text → Chunks (300 tokens, 50 token overlap)
3. **Embed**: Chunks → Vector embeddings (384-dim)
4. **Store**: Vectors → Qdrant database
5. **Search**: Query → Find similar chunks
6. **Answer**: Context + Question → Hugging Face Q&A model

## ⚡ Session Management

- Each browser session gets a unique session ID
- Documents indexed per session
- Data cleared when browser closes
- No persistent user profiles

## 🎓 Use Cases

- 📚 Study aid for textbooks
- 📊 Data sheet analysis
- 📄 Contract review
- 🔬 Research paper Q&A
- 📋 Document summarization

## 📄 License

Open source - Feel free to use and modify

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📧 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ using Streamlit, Hugging Face, and Qdrant**
