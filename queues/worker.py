from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI()

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

def process_query(query : str):
    vector_db = QdrantVectorStore.from_existing_collection(
        embedding = embedding_model,
        url = "http://localhost:6333",
        collection_name = "learning_rag"
    )
    
    search_result = vector_db.similarity_search(query= query)
    
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
            {"role" : "user", "content" : query}
        ]
    )

    return {"result" : response.choices[0].message.content}
