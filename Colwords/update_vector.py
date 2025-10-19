from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
import requests

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)

vector_store = Chroma(
    collection_name="colwords",
    embedding_function=embeddings,
    # host="localhost",
    # port="8000"
    persist_directory="./colwords_vector_store",
)

def database_content():
    url = "https://colwords.com/api/words/random"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            response = response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return
    
    return response

def update_vector_store():
    data = database_content()
    if data and 'data' in data and 'words' in data['data']:
        documents = []
        for word in data['data']['words']:
            content = f"Name: {word['name']}\nType: {word['type']}\nDefinition: {word['definition']}\nCategory: {word['category']['name']}\nSubcategory: {word['sub_category']['name']}"
            doc = Document(page_content=content, metadata={"name": word['name'], "category": word['category']['name'], "subcategory": word['sub_category']['name']})
            documents.append(doc)
            
        vector_store.add_documents(documents)
        print("Vector store updated successfully with", len(documents), "documents")
    else:
        print("No data to update vector store")

def retriever(query: str, k: int = 5):
    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": k})
    results = retriever.invoke(query)
    print(results)
    return results

# update_vector_store()
retriever("Your question was outstanding")