from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
# from ..main import QueryBody

load_dotenv()

openai_client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

class QueryBody(BaseModel):
    query: str
    UserId: str
    DocumentId: str

def process_query(body):
    vector_db = QdrantVectorStore.from_existing_collection(
        embedding=embedding_model,
        url="http://localhost:6333",
        collection_name="learning_rag"
    )

    # Filter by metadata fields
    search_result = vector_db.similarity_search(
        query=body["query"],
        filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.UserId",  # Use metadata.UserId for proper filtering
                    match=MatchValue(value=body["UserId"])
                ),
                FieldCondition(
                    key="metadata.DocumentId",  # Use metadata.DocumentId for proper filtering
                    match=MatchValue(value=body["DocumentId"])
                ),
            ]
        ),
        k=5  # Return top 5 relevant chunks
    )

    context = "\n\n\n".join([
        f"Page Content: {r.page_content}\nPage Number: {r.metadata['page_label']}\nfile location: {r.metadata['source']}"
        for r in search_result
    ])


    SYSTEM_PROMPT = f"""You are a help full assistant who answers user query based on the available context retrieved from a PDF file along with the page contents and page number.
    
    you should only answer based on the user based on the followingcontext and nevigate the user to open the right page number to know more. 

    Context: 
    {context}
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",  # Fixed: gpt-5 doesn't exist
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": body["query"]},
        ]
    )

    return {"result": response.choices[0].message.content}