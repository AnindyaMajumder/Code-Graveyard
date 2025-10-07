import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def extract_from_pdf():
    try:
        completion = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {
                "role": "system",
                "content": "You are a experienced meal planner and recipe suggester. You provide meal suggestions based on user preferences and dietary restrictions."
            },
            {
                "role": "user",
                "content": ""
            }
        ]
        )

        print(completion, end="\n\n")
        return completion.choices[0].message.content
    
    except Exception as e:
        raise RuntimeError(f"Failed to extract from PDF: {e}")
        
print(extract_from_pdf())