import streamlit as st
import os
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="Document Q&A with OpenAI",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Document Q&A with OpenAI")
st.markdown("Upload a PDF document and ask questions using AI")

# Initialize session state
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "document_name" not in st.session_state:
    st.session_state.document_name = ""

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text_content = ""
    try:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text_content += page.extract_text()
        return text_content
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# Function to get answer from OpenAI
def get_answer_from_openai(question, context):
    """Get answer from OpenAI using the document context"""
    try:
        if not context or len(context.strip()) < 50:
            return "The document doesn't contain enough text to answer this question."

        # Create prompt for OpenAI
        prompt = f"""
You are a helpful assistant that answers questions based on the provided document content.

Document Content:
{context[:8000]}  # Limit context to avoid token limits

Question: {question}

Please provide a clear, concise answer based only on the information in the document above. If the answer cannot be found in the document, say so.
"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on document content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error getting answer from OpenAI: {str(e)}"

# Main interface
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📤 Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to analyze"
    )

    if uploaded_file is not None:
        if st.button("📄 Process Document", type="primary"):
            with st.spinner("Extracting text from PDF..."):
                text_content = extract_text_from_pdf(uploaded_file)

                if text_content:
                    st.session_state.document_text = text_content
                    st.session_state.document_name = uploaded_file.name

                    # Show document info
                    st.success(f"✅ Document processed: {uploaded_file.name}")
                    st.info(f"📊 Text length: {len(text_content)} characters")
                    st.info(f"📄 Pages: {len(PdfReader(uploaded_file).pages)}")

                    # Show preview
                    with st.expander("📖 Document Preview"):
                        st.text_area(
                            "First 1000 characters:",
                            text_content[:1000],
                            height=200,
                            disabled=True
                        )
                else:
                    st.error("Failed to extract text from the PDF")

with col2:
    st.subheader("💬 Ask Questions")

    if not st.session_state.document_text:
        st.info("👆 Please upload and process a document first")
    else:
        st.info(f"📄 Current document: **{st.session_state.document_name}**")

        # Question input
        question = st.text_area(
            "Your question:",
            placeholder="e.g., What are the main topics covered in this document?",
            height=100
        )

        if st.button("🔍 Get Answer", type="primary", disabled=not question):
            if question:
                with st.spinner("Getting answer from OpenAI..."):
                    answer = get_answer_from_openai(question, st.session_state.document_text)

                    # Display answer
                    st.markdown("### 🤖 AI Answer:")
                    st.markdown("---")

                    # Answer box
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #667eea;">
                    {answer}
                    </div>
                    """, unsafe_allow_html=True)

                    # Add to chat history (optional)
                    if "chat_history" not in st.session_state:
                        st.session_state.chat_history = []

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "timestamp": st.session_state.get("timestamp", "now")
                    })

        # Show chat history
        if "chat_history" in st.session_state and st.session_state.chat_history:
            with st.expander("📚 Previous Questions"):
                for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):  # Show last 5
                    st.markdown(f"**Q{i}:** {chat['question']}")
                    st.markdown(f"**A{i}:** {chat['answer'][:200]}...")
                    st.divider()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🚀 Powered by <strong>OpenAI GPT</strong> • <strong>Streamlit</strong></p>
    <p>📌 Documents are processed in memory and not stored</p>
</div>
""", unsafe_allow_html=True)
