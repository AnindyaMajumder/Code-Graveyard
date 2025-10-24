import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from update_vector import retriever
import json
from google import genai
from google.genai import types

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
gemini_key = os.getenv("GOOGLE_API_KEY")

model = ChatOpenAI(model="gpt-4.1-nano", temperature=0.7, api_key=openai_key)
generator = ChatOpenAI(model="gpt-5", temperature=0.2, api_key=openai_key)

def image_generator(sentence: str):
    client = genai.Client(api_key=gemini_key)

    prompt = (f"Generate an well explanatory image for this sentence to teach English: \n"+ sentence)

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
        response_modalities=['Image'])
    )
    
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            continue
        elif part.inline_data is not None:
            return part.inline_data.data
            
# Define the function that calls the model
def flashcard(query: str):
    retriever_query = generator.invoke([
        SystemMessage(content="You are an expert in generating concise flashcards. Given the last 5 messages from a conversation, craft a precise one-line query to retrieve relevant words from the vectordb. The vectordb contains words along with their definitions, types, categories, and subcategories. Ensure the query retrieves words that are contextually relevant to the conversation for effective flashcard creation."),
        AIMessage(content="Here is the last 5 messages from the conversation: \n" + query)
    ])

    retriever_response = retriever(retriever_query.content, k=10) 
    relevant_docs = "\n".join([doc.page_content for doc in retriever_response])
    
    flashcard_prompt = f"""
    You are an expert at creating concise flashcards. Based on the following retrieval and relevant words from the database, generate a set of flashcards. Each flashcard should contain a term and its definition. Ensure the flashcards are clear and informative.
    {relevant_docs}"""
    flashcard_response = model.invoke([
        SystemMessage(content=flashcard_prompt),
        HumanMessage(content="Generate 5 flashcards containing terms, pos, definition, category and subcategory and example sentence."),
        HumanMessage(content="Don't keep any texts other than json format. Example JSON format: [{ 'term': 'example', 'pos': 'noun', 'definition': 'a representative form or pattern', 'category': 'general', 'subcategory': 'usage', 'example_sentence': 'This is an example sentence.' }]"),
        ])
        
    flashcard_response = json.loads(flashcard_response.content)
        
    # Add image for each flashcard
    for card in flashcard_response:
        card['image'] = image_generator(card['example_sentence'])
                
    return flashcard_response

print(flashcard(f"""
          User: I would like to learn about outstanding words.
          AI: Sure! Do you have any specific categories or types of words in mind?
          User: No, just the most outstanding ones.
          """))

# print(image_generator("Her performance in the competition was outstanding."))