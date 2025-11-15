from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from typing import Annotated
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

app = FastAPI()

ROOT_PATH = Path.cwd()

openai_client = OpenAI()

# correct way
app.mount("/files", StaticFiles(directory=ROOT_PATH), name="files")

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

@app.post("/save-file/")
async def save_file(file: UploadFile = File(...), UserId: str = 'default', DocumentId: str = 'default'):
    # save file
    file_path = ROOT_PATH / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # load pdf
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    
    
    # add metadata (user + document)
    for d in docs:
        d.metadata["UserId"] = UserId
        d.metadata["DocumentId"] = DocumentId

    # split chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    
    vector_store = QdrantVectorStore.from_documents(
        documents = chunks,
        embedding = embedding_model,
        url = "http://localhost:6333",
        collection_name = "learning_rag"
    )

    print("indexing of documents done.")
    
    return {
        "saved_to": str(file_path),
        "total_pages": len(docs),
        "total_chunks": len(chunks),
        "sample_chunk": chunks[0].page_content[:300]  # short preview
    }
    
class QueryBody(BaseModel):
    query: str

@app.post("/query")
async def userQnA(body : QueryBody):
    
    vector_db = QdrantVectorStore.from_existing_collection(
        embedding = embedding_model,
        url = "http://localhost:6333",
        collection_name = "learning_rag"
    )

    search_result = vector_db.similarity_search(query=body.query)
    
    context = "\n\n\n".join({f"Page Content: {result.page_content}\nPage Number:{result.metadata["page_label"]}\nfile location: {result.metadata["source"]}" for result in search_result})
    
    SYSTEM_PROMPT = f"""You are a help full assistant who answers user query based on the available context retrieved from a PDF file along with the page contents and page number.
    
    you should only answer based on the user based on the followingcontext and nevigate the user to open the right page number to know more. 

    Context: 
    {context}
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role" : "system", "content" : SYSTEM_PROMPT},
            {"role" : "user", "content" : body.query}
        ]
    )

    return {"result" : response.choices[0].message.content}

# @app.get("/read-file/")
# async def read_file(filename: str):
#     file_path = os.path.join(ROOT_PATH, filename)

#     if not os.path.exists(file_path):
#         return {"error": "File not found"}

#     with open(file_path, "rb") as f:
#         content = f.read()

#     return {"filename": filename, "content": content.decode(errors="ignore")}
