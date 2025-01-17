from flask import Flask,render_template,jsonify,request
from src.helper import download_huggingface_embeddings
from langchain.vectorstores import Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.prompt import *
from dotenv import load_dotenv
import os

load_dotenv()


app=Flask(__name__)

PINECONE_API_KEY=os.environ.get("PINECONE_API_KEY")
HUGGINGFACE_API_KEY=os.environ.get("HUGGINGFACE_HUB_TOKEN")

os.environ["PINECONE_API_KEY"]=PINECONE_API_KEY
os.environ['HUGGINGFACE_API_KEY']=HUGGINGFACE_API_KEY


embeddings=download_huggingface_embeddings()

index_name="pythonlearning"

docs_search=Pinecone.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever=docs_search.as_retriever(search_type="similarity",search_kwargs={"k":3})


llm=ChatGoogleGenerativeAI(model="gemini-1.5-pro",temprature=0.3,max_token=100)

prompt=ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human","{input}"),
    ]
)

question_answer_chain=create_stuff_documents_chain(llm,prompt)
rag_chain=create_retrieval_chain(retriever,question_answer_chain)

@app.route("/")
def index():
    return render_template("index.html")



@app.route("/get",methods=['GET','POST'])
def chat():
    msg=request.form["msg"]
    input=msg
    print(input)
    response=rag_chain.invoke({"input":msg})
    print("Response :", response["answer"])
    return str(response["answer"])

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5001,debug=True)