from fastapi import FastAPI, UploadFile, File, Query
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
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
from clients.rq_client import queue
from queues.worker import process_query
from passlib.context import CryptContext
import jwt
import datetime

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

def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")

@app.get('/')
def startServer():
    return {"status" : "server is running"}
 
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
    print(f"\n\n {job.id} \n\n")
    return job.return_value()

@app.post("/query")
async def userQnA(body : QueryBody):
    job = queue.enqueue(process_query, body.query)
    return {"status" : "query queued", "job_id" : job.id}
    # vector_db = QdrantVectorStore.from_existing_collection(
    #     embedding = embedding_model,
    #     url = "http://localhost:6333",
    #     collection_name = "learning_rag"
    # )

    # search_result = vector_db.similarity_search(query=body.query)
    
    # context = "\n\n\n".join({f"Page Content: {result.page_content}\nPage Number:{result.metadata["page_label"]}\nfile location: {result.metadata["source"]}" for result in search_result})
    
    # SYSTEM_PROMPT = f"""You are a help full assistant who answers user query based on the available context retrieved from a PDF file along with the page contents and page number.
    
    # you should only answer based on the user based on the followingcontext and nevigate the user to open the right page number to know more. 

    # Context: 
    # {context}
    # """
    
    # response = openai_client.chat.completions.create(
    #     model="gpt-5",
    #     messages=[
    #         {"role" : "system", "content" : SYSTEM_PROMPT},
    #         {"role" : "user", "content" : body.query}
    #     ]
    # )
    

# @app.get("/read-file/")
# async def read_file(filename: str):
#     file_path = os.path.join(ROOT_PATH, filename)

#     if not os.path.exists(file_path):
#         return {"error": "File not found"}

#     with open(file_path, "rb") as f:
#         content = f.read()

#     return {"filename": filename, "content": content.decode(errors="ignore")}

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

    return {"token": token}

main()
