# 🚀 Streamlit Frontend for AI Document Summarizer

A beautiful, user-friendly web interface for the Document Summarizer application built with Streamlit.

## ✨ Features

- 🔐 **User Authentication**: Secure signup and login system
- 📤 **PDF Upload**: Easy drag-and-drop PDF upload interface
- 💬 **Interactive Q&A**: Ask questions about your uploaded documents
- 📊 **Document Management**: Track all your uploaded documents in the sidebar
- 🎨 **Modern UI**: Beautiful gradient design with responsive layout
- ⚡ **Real-time Processing**: Live progress tracking for document processing and queries

## 📸 Screenshots

The app includes:
- Login/Signup page with tabs
- Document upload interface with progress tracking
- Query interface with document selection
- Sidebar showing user info and uploaded documents
- Beautiful response formatting with gradient styling

## 🛠️ Prerequisites

Make sure you have the following running:

1. **FastAPI Backend** (`main.py`) on `http://localhost:8000`
2. **Docker Services** (MongoDB, Qdrant, Redis/Valkey)
3. **RQ Worker** for background job processing

## 📦 Installation

Streamlit is already included in your `requirements.txt`. If you need to install it separately:

```bash
pip install streamlit
```

## 🚀 Running the Application

### Step 1: Start Docker Services
```bash
docker-compose up -d
```

### Step 2: Start the FastAPI Backend
In one terminal:
```bash
python main.py
```

The API should be running at `http://localhost:8000`

### Step 3: Start the RQ Worker
In another terminal:
```bash
cd queues
rq worker --with-scheduler
```

### Step 4: Start the Streamlit App
In a third terminal:
```bash
streamlit run streamlit_app.py
```

The Streamlit app will open automatically in your browser at `http://localhost:8501`

## 📖 How to Use

### 1. Create an Account
- Navigate to the **Sign Up** tab
- Enter your name, email, and password
- Click "Sign Up"

### 2. Login
- Go to the **Login** tab
- Enter your credentials
- Click "Login"

### 3. Upload a PDF Document
- Click on the "📤 Upload Document" tab
- Choose a PDF file from your computer
- Click "📤 Upload & Process"
- Wait for the document to be processed (you'll see a progress indicator)

### 4. Ask Questions
- Click on the "💬 Ask Questions" tab
- Select a document from the dropdown (if you have multiple)
- Type your question in the text area
- Click "🔍 Ask Question"
- Wait for the AI to process your query and provide an answer

### 5. View Your Documents
- Check the sidebar to see all your uploaded documents
- Each document shows its ID, number of pages, chunks, and upload time

## 🎨 Customization

### Change API URL
If your FastAPI backend is running on a different host/port, update the `API_BASE_URL` in `streamlit_app.py`:

```python
# Configuration
API_BASE_URL = "http://your-host:your-port"
```

### Customize Styling
The app uses custom CSS for styling. You can modify the colors and design in the `st.markdown()` section at the top of `streamlit_app.py`:

```python
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        /* Your custom styles here */
    }
    </style>
""", unsafe_allow_html=True)
```

### Adjust Polling Settings
For query results, you can adjust the polling timeout and interval in the `show_main_page()` function:

```python
max_attempts = 30  # Maximum wait time in seconds
time.sleep(1)      # Poll every 1 second
```

## 🐛 Troubleshooting

### Issue: "Connection refused" error
**Solution**: Make sure your FastAPI backend is running on `http://localhost:8000`

```bash
# Check if the API is running
curl http://localhost:8000/
# Should return: {"status":"server is running"}
```

### Issue: Queries timeout
**Solution**: 
1. Verify the RQ worker is running:
```bash
ps aux | grep "rq worker"
```
2. Check Redis/Valkey is running:
```bash
docker ps | grep valkey
```

### Issue: Authentication fails
**Solution**: Verify MongoDB is running and accessible:
```bash
docker ps | grep mongo
mongosh "mongodb://admin:admin@localhost:27017/?authSource=admin"
```

### Issue: Document upload fails
**Solution**: 
1. Check that Qdrant is running:
```bash
curl http://localhost:6333/collections
```
2. Verify your OpenAI API key is set in `.env`

### Issue: Streamlit app doesn't start
**Solution**: 
1. Check if port 8501 is already in use:
```bash
lsof -i :8501
```
2. Run on a different port:
```bash
streamlit run streamlit_app.py --server.port 8502
```

## 📝 Configuration Options

You can configure Streamlit settings by creating a `.streamlit/config.toml` file:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = false
```

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Update the `API_BASE_URL` to point to your deployed FastAPI backend
5. Add your secrets in the Streamlit Cloud dashboard

### Deploy Locally with Docker

Create a `Dockerfile` for the Streamlit app:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t document-summarizer-frontend .
docker run -p 8501:8501 document-summarizer-frontend
```

## 🔒 Security Notes

- Session state is used for authentication (client-side)
- For production, implement proper token-based authentication
- Always use HTTPS in production
- Store sensitive configuration in environment variables
- Never commit API keys or secrets to version control

## 🎯 Portfolio Tips

When showcasing this project in your portfolio:

1. **Take Screenshots**: Capture the login page, upload interface, and query results
2. **Create a Demo Video**: Show the full workflow from signup to asking questions
3. **Highlight Features**: 
   - Real-time document processing
   - AI-powered Q&A
   - User authentication
   - Modern, responsive UI
4. **Explain the Tech Stack**:
   - Frontend: Streamlit
   - Backend: FastAPI
   - Database: MongoDB + Qdrant (vector DB)
   - Queue: Redis/Valkey + RQ
   - AI: OpenAI GPT + Embeddings

## 📄 License

This project is part of your portfolio. Feel free to customize and use it as needed.

## 🤝 Contributing

This is a portfolio project, but you can extend it with:
- Document deletion functionality
- Chat history
- Multi-document querying
- File format support (Word, Excel, etc.)
- Share documents with other users
- Export answers to PDF/Markdown

## 📧 Contact

Add your contact information here for your portfolio.

---

**Happy Coding! 🎉**
