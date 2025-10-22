import os
from dotenv import load_dotenv
from update_vector import retriever
import json
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="gpt-4.1-nano", temperature=0.7, api_key=api_key)

# Define the function that calls the model
def quiz(query: str):
    retriever_query = model.invoke([
        SystemMessage(content="You are an expert in summarizing chats for quiz question generation. Given the last 5 messages from a conversation, craft a precise one-line query to retrieve relevant words from the vectordb. The vectordb contains words along with their definitions, types, categories, and subcategories. Ensure the query retrieves words that are contextually relevant to the conversation for effective quiz question creation."),
        HumanMessage(content="Here is the last 5 messages from the conversation: \n" + query)
    ])
    
    retriever_response = retriever(retriever_query.content, k=10) 
    relevant_docs = "\n".join([doc.page_content for doc in retriever_response])
    
    flashcard_prompt = f"""
    You are an expert at creating concise quiz of 5 questions. Based on the following retrieval and relevant words from the database, generate a quiz. Each question should be clear and informative. Your main goal is to help users learn new words effectively.\n\n{relevant_docs}"""
    flashcard_response = model.invoke([
        SystemMessage(content=flashcard_prompt),
        HumanMessage(content="Generate 5 quiz questions with 4 options and indicate the correct answer."),
        HumanMessage(content="Don't keep any texts other than json format. Example JSON format: [{ 'question': 'What is ...?', 'options': ['A. ...', 'B. ...', 'C. ...', 'D. ...'], 'correct_answer': 'A' }]"),
        ])
        
    flashcard_response = json.loads(flashcard_response.content)
    return flashcard_response

print(quiz(f"""
          User: I would like to learn about outstanding words.
          AI: Sure! Do you have any specific categories or types of words in mind?
          User: No, just the most outstanding ones.
          """
))