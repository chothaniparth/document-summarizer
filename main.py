from fastapi import FastAPI, UploadFile, File, Query, Form
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from typing import Annotated
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
from clients.rq_client import queue
from queues.worker import process_query
from passlib.context import CryptContext
import jwt
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
JWT_SECRET = os.getenv('JWT_SECRET') 

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

ROOT_PATH = Path.cwd()

openai_client = OpenAI()

# correct way
app.mount("/files", StaticFiles(directory=ROOT_PATH), name="files")

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# Initialize Qdrant client
qdrant_client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "learning_rag"

# Ensure collection exists with proper schema
def init_qdrant_collection():
    """Initialize Qdrant collection with proper schema for filtering"""
    collections = qdrant_client.get_collections().collections
    collection_names = [c.name for c in collections]
    
    if COLLECTION_NAME not in collection_names:
        # Create collection with vector configuration
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=3072,  # text-embedding-3-large dimension
                distance=Distance.COSINE
            )
        )
        print(f"✅ Created collection: {COLLECTION_NAME}")
    
    # Create payload indexes for filtering
    try:
        qdrant_client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="metadata.UserId",
            field_schema=PayloadSchemaType.KEYWORD
        )
        qdrant_client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="metadata.DocumentId",
            field_schema=PayloadSchemaType.KEYWORD
        )
        print(f"✅ Created payload indexes for UserId and DocumentId")
    except Exception as e:
        # Indexes might already exist
        print(f"ℹ️  Payload indexes may already exist: {e}")

# Initialize on startup
init_qdrant_collection()

def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")

@app.get('/')
def startServer():
    return {"status" : "server is running"}
 

@app.post("/save-file/")
async def save_file(
    file: UploadFile = File(...),
    UserId: str = Form(...)
):
    # save file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_name = f"{timestamp}_{file.filename}"

    file_path = ROOT_PATH / unique_name
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ---- 2. Create DB entry ----
    doc_data = {
        "userId": UserId,
        "fileName": unique_name,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = await db.documents.insert_one(doc_data)
    DocumentId = str(result.inserted_id)

    # ---- 3. Load PDF ----
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
    
    # Store vectors with metadata for filtering
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        url="http://localhost:6333",
        collection_name=COLLECTION_NAME
    )
    
    return {
        "documentId": DocumentId,
        "saved_file": unique_name,
        "pages": len(docs),
        "chunks": len(chunks)
    }
    
class QueryBody(BaseModel):
    query: str
    UserId: str
    DocumentId: str
    
class UserSignup(BaseModel):
    name: str
    email: str
    password: str
    
class UserLogin(BaseModel):
    email: str
    password: str

@app.get("/getResult")
async def getResult(job_id: str = Query(..., description="job_id")):
    job = queue.fetch_job(job_id)
    return job.return_value()

@app.post("/query")
async def userQnA(body: QueryBody):
    job = queue.enqueue(process_query, body.dict())   # send dict
    return {"status": "query queued", "job_id": job.id}

@app.post("/signup")
async def signup(body: UserSignup):
    
    user = await db.users.find_one({"email": body.email})
    if user:
        return {"error": "Email already exists"}

    hashed = pwd.hash(body.password)

    res = await db.users.insert_one({
        "name": body.name,
        "email": body.email,
        "password": hashed
    })

    return {"status": "user created", "id": str(res.inserted_id)}

@app.post("/login")
async def login(body: UserLogin):
    user = await db.users.find_one({"email": body.email})
    if not user:
        return {"error": "Invalid credentials"}

    if not pwd.verify(body.password, user["password"]):
        return {"error": "Invalid credentials"}

    token = jwt.encode({
        "user_id": str(user["_id"]),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, JWT_SECRET)

    return {"token": token, "user_id": str(user["_id"]), "email" : str(user["email"]), "name" : str(user["name"])}

main()
