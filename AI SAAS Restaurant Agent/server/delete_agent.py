import requests
import os
from dotenv import load_dotenv

load_dotenv()

def delete_agent(agent_id,  twilio_id):
    try: 
        response1 = requests.delete(
        "https://api.vapi.ai/assistant/" + agent_id,
        headers={
            "Authorization": "Bearer " + os.getenv("VAPI_API_KEY"),
        },
        )
        
        response2 = requests.delete(
        "https://api.vapi.ai/phone-number/" + twilio_id,
        headers={
            "Authorization": "Bearer " + os.getenv("VAPI_API_KEY"),
        },
        )
        
        return response1.json(), response2.json()
    except:
        raise Exception("Failed to delete assistant")