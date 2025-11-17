# 🚀 Quick Start Guide - Streamlit Frontend

Get your AI Document Summarizer running in 5 minutes!

## 🎯 One-Command Start (Easiest)

```bash
./start_app.sh
```

This will start all Docker services and give you instructions for the next steps.

## 📋 Manual Start (Step by Step)

### Terminal 1: Start Docker Services
```bash
docker-compose up -d
```

Wait for services to start (~10 seconds)

### Terminal 2: Start FastAPI Backend
```bash
python main.py
```

You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`

### Terminal 3: Start RQ Worker
```bash
cd queues
rq worker --with-scheduler
```

You should see: `Worker started`

### Terminal 4: Start Streamlit Frontend
```bash
streamlit run streamlit_app.py
```

Your browser will automatically open to `http://localhost:8501`

## ✅ Quick Test

1. **Sign Up**: Create a new account
   - Name: Test User
   - Email: test@example.com
   - Password: test123

2. **Login**: Use the credentials you just created

3. **Upload a PDF**: 
   - Go to "📤 Upload Document" tab
   - Choose any PDF file
   - Click "📤 Upload & Process"
   - Wait for processing (usually 10-30 seconds depending on PDF size)

4. **Ask a Question**:
   - Go to "💬 Ask Questions" tab
   - Select your uploaded document
   - Type a question like: "What is this document about?"
   - Click "🔍 Ask Question"
   - Wait for AI response (5-15 seconds)

## 🎨 What You'll See

### Login Page
- Clean, modern interface with gradient header
- Tabs for Login and Sign Up
- Form validation

### Main Dashboard
- Sidebar showing:
  - User profile
  - List of uploaded documents
  - Logout button
- Main area with two tabs:
  - Upload Document
  - Ask Questions

### Upload Tab
- Drag-and-drop PDF uploader
- Progress indicator during processing
- Success message with document details

### Query Tab
- Document selector dropdown
- Text area for your question
- Real-time progress bar
- Beautiful answer display with gradient border

## 🔍 Verifying Everything Works

Check each service is running:

```bash
# Check Docker services
docker-compose ps

# Check FastAPI
curl http://localhost:8000/
# Should return: {"status":"server is running"}

# Check Streamlit (in browser)
# Open: http://localhost:8501

# Check Qdrant Dashboard (in browser)
# Open: http://localhost:6333/dashboard
```

## ⚠️ Common Issues

### "Connection refused" when logging in
→ FastAPI backend is not running. Start it with `python main.py`

### Queries stuck at "Waiting for response"
→ RQ worker is not running. Start it with `cd queues && rq worker --with-scheduler`

### "Port already in use" error
→ Another app is using the port. Either:
- Stop the other app
- Or run on a different port: `streamlit run streamlit_app.py --server.port 8502`

### Document upload fails
→ Check:
1. Qdrant is running: `curl http://localhost:6333/collections`
2. OpenAI API key is set in `.env`

## 🎥 Demo Flow

Here's a suggested flow for demonstrating this in your portfolio:

1. **Show the landing page** - Beautiful gradient design
2. **Create an account** - Show the signup process
3. **Upload a document** - Use a sample PDF, show the processing
4. **Ask several questions**:
   - "Summarize this document in 3 bullet points"
   - "What are the main topics covered?"
   - "Can you explain [specific concept from the PDF]?"
5. **Show sidebar** - Multiple documents management
6. **Switch between documents** - Query different docs

## 📸 Portfolio Screenshots to Take

1. Login/Signup page
2. Empty dashboard (no documents yet)
3. Document upload in progress
4. Successfully uploaded document
5. Sidebar with multiple documents
6. Query being processed (progress bar)
7. AI response displayed
8. Multiple Q&A examples

## 🎨 Customization Ideas

Want to make it your own?

1. **Change the color scheme**:
   - Edit the gradient in `streamlit_app.py`
   - Currently: `#667eea` (purple) to `#764ba2` (darker purple)

2. **Add your branding**:
   - Replace "AI Document Summarizer" with your name
   - Add your logo to the sidebar

3. **Extend features**:
   - Add document deletion
   - Add chat history
   - Export answers to PDF
   - Add document statistics

## 📊 System Requirements

- **Python**: 3.13+
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB for dependencies + space for PDFs
- **Docker**: Latest version
- **OS**: macOS, Linux, or Windows (with WSL2)

## 🚀 Ready to Deploy?

See `STREAMLIT_README.md` for deployment options:
- Streamlit Cloud (easiest, free tier available)
- Docker container
- VPS/Cloud server

## 🎓 Learning Resources

Built with:
- [Streamlit Docs](https://docs.streamlit.io)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [OpenAI API](https://platform.openai.com/docs)
- [LangChain](https://python.langchain.com)

---

**Need Help?** Check `STREAMLIT_README.md` for detailed troubleshooting.

**Ready to Start?** Run `./start_app.sh` and follow the steps! 🎉
