import streamlit as st
import requests
import time
from datetime import datetime
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="AI Document QnA",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .query-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .document-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'token' not in st.session_state:
    st.session_state.token = None
if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = []

# Helper functions
def signup_user(name, email, password):
    """Sign up a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/signup",
            json={
                "name": name,
                "email": email,
                "password": password
            }
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def login_user(email, password):
    """Login user and get token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={
                "email": email,
                "password": password
            }
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def upload_document(file, user_id):
    """Upload a PDF document"""
    try:
        files = {"file": (file.name, file, "application/pdf")}
        data = {"UserId": user_id}
        response = requests.post(
            f"{API_BASE_URL}/save-file/",
            files=files,
            data=data
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def query_document(query, user_id, document_id):
    """Submit a query about a document"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={
                "query": query,
                "UserId": user_id,
                "DocumentId": document_id
            }
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_query_result(job_id):
    """Get the result of a query job"""
    try:
        response = requests.get(f"{API_BASE_URL}/getResult?job_id={job_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Authentication page
def show_auth_page():
    st.markdown('<div class="main-header">📄 AI Document QnA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about your PDF documents using AI</div>', unsafe_allow_html=True)
    
    # Create tabs for login and signup
    auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with auth_tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            login_email = st.text_input("Email", placeholder="your.email@example.com")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                if login_email and login_password:
                    with st.spinner("Logging in..."):
                        result = login_user(login_email, login_password)
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        elif "token" in result:
                            st.session_state.authenticated = True
                            st.session_state.user_id = result["user_id"]
                            st.session_state.user_email = result["email"]
                            st.session_state.user_name = result["name"]
                            st.session_state.token = result["token"]
                            st.success(f"✅ Welcome back, {result['name']}!")
                            st.rerun()
                else:
                    st.error("Please fill in all fields")
    
    with auth_tab2:
        st.subheader("Create a New Account")
        with st.form("signup_form"):
            signup_name = st.text_input("Full Name", placeholder="John Doe")
            signup_email = st.text_input("Email", placeholder="your.email@example.com")
            signup_password = st.text_input("Password", type="password", placeholder="Create a strong password")
            signup_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            submit_signup = st.form_submit_button("Sign Up")
            
            if submit_signup:
                if signup_name and signup_email and signup_password and signup_confirm_password:
                    if signup_password != signup_confirm_password:
                        st.error("❌ Passwords don't match!")
                    else:
                        with st.spinner("Creating account..."):
                            result = signup_user(signup_name, signup_email, signup_password)
                            if "error" in result:
                                st.error(f"❌ {result['error']}")
                            elif "status" in result:
                                st.success("✅ Account created successfully! Please login.")
                else:
                    st.error("Please fill in all fields")

# Main application page
def show_main_page():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {st.session_state.user_name}!")
        st.markdown(f"**Email:** {st.session_state.user_email}")
        st.markdown("---")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.token = None
            st.session_state.uploaded_documents = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Uploaded Documents")
        if st.session_state.uploaded_documents:
            for doc in st.session_state.uploaded_documents:
                with st.expander(f"📄 {doc['filename'][:30]}..."):
                    st.write(f"**Document ID:** {doc['document_id'][:8]}...")
                    st.write(f"**Pages:** {doc['pages']}")
                    st.write(f"**Chunks:** {doc['chunks']}")
                    st.write(f"**Uploaded:** {doc['timestamp']}")
        else:
            st.info("No documents uploaded yet")
    
    # Main content
    st.markdown('<div class="main-header">📄 AI Document QnA</div>', unsafe_allow_html=True)
    
    # Create tabs for upload and query
    tab1, tab2 = st.tabs(["📤 Upload Document", "💬 Ask Questions"])
    
    with tab1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("Upload Your PDF Document")
        st.write("Upload a PDF file to start asking questions about it using AI.")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload a PDF document to analyze"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File selected: {uploaded_file.name}")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("📤 Upload & Process", type="primary"):
                    with st.spinner("Uploading and processing document... This may take a minute."):
                        result = upload_document(uploaded_file, st.session_state.user_id)
                        
                        if "error" in result:
                            st.error(f"❌ Error: {result['error']}")
                        elif "documentId" in result:
                            # Add to session state
                            st.session_state.uploaded_documents.append({
                                "document_id": result["documentId"],
                                "filename": result["saved_file"],
                                "pages": result["pages"],
                                "chunks": result["chunks"],
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                            st.success("✅ Document uploaded and processed successfully!")
                            st.balloons()
                            
                            # Show processing details
                            st.info(f"""
                            **Processing Complete:**
                            - Document ID: `{result['documentId']}`
                            - Pages processed: {result['pages']}
                            - Text chunks created: {result['chunks']}
                            - File: {result['saved_file']}
                            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="query-section">', unsafe_allow_html=True)
        st.subheader("Ask Questions About Your Documents")
        
        if not st.session_state.uploaded_documents:
            st.warning("⚠️ Please upload a document first before asking questions.")
        else:
            # Document selector
            doc_names = [f"{doc['filename']} (ID: {doc['document_id'][:8]}...)" 
                        for doc in st.session_state.uploaded_documents]
            selected_doc_idx = st.selectbox(
                "Select a document to query:",
                range(len(doc_names)),
                format_func=lambda x: doc_names[x]
            )
            
            selected_doc = st.session_state.uploaded_documents[selected_doc_idx]
            
            # Query input
            query = st.text_area(
                "Your question:",
                placeholder="e.g., What are the main topics covered in this document?",
                height=100
            )
            
            col1, col2 = st.columns([1, 3])
            with col1:
                submit_query = st.button("🔍 Ask Question", type="primary")
            
            if submit_query and query:
                with st.spinner("Processing your question... This may take a few seconds."):
                    # Submit query
                    result = query_document(
                        query,
                        st.session_state.user_id,
                        selected_doc["document_id"]
                    )
                    
                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    elif "job_id" in result:
                        job_id = result["job_id"]
                        st.info(f"Query submitted. Job ID: `{job_id}`")
                        
                        # Poll for result
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        max_attempts = 30
                        for attempt in range(max_attempts):
                            time.sleep(1)
                            progress_bar.progress((attempt + 1) / max_attempts)
                            status_text.text(f"Waiting for response... ({attempt + 1}/{max_attempts}s)")
                            
                            query_result = get_query_result(job_id)
                            
                            if query_result and "result" in query_result:
                                progress_bar.empty()
                                status_text.empty()
                                
                                st.success("✅ Answer received!")
                                st.markdown("### 💡 Answer:")
                                st.markdown(f"""
                                <div style='background-color: #f0f2f6; padding: 1.5rem; 
                                border-radius: 10px; border-left: 5px solid #667eea;'>
                                {query_result['result']}
                                </div>
                                """, unsafe_allow_html=True)
                                break
                            
                            if attempt == max_attempts - 1:
                                progress_bar.empty()
                                status_text.empty()
                                st.warning("⚠️ Response is taking longer than expected. Please try again.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>Built with ❤️ using Streamlit, FastAPI, OpenAI, and Qdrant</p>
            <p style='font-size: 0.9rem;'>© 2024 AI Document QnA - Portfolio Project</p>
        </div>
    """, unsafe_allow_html=True)

# Main app logic
def main():
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_page()

if __name__ == "__main__":
    main()
