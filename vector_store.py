from src.helper import load_pdf,text_split,download_huggingface_embeddings
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")

extracted_data=load_pdf("learning_python/")

text_chunk=text_split(extracted_data)

embeddings=download_huggingface_embeddings()


pc=Pinecone(api_key=PINECONE_API_KEY)

index_name="pythonlearning"

pc.create_index(
    name=index_name,
    dimension=384,
    metric='cosine',
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

from langchain.vectorstores import Pinecone

docs_search=Pinecone.from_documents(

    documents=text_chunk,
    index_name=index_name,
    embedding=embeddings

)

docs_search=Pinecone.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)