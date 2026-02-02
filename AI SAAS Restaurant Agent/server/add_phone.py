import requests
import os
from dotenv import load_dotenv

load_dotenv()

def create_phone_number(name="Restaurant", twillo_num="+1765487", ssid="ghhjghjgjhgjgj", restaurant_fallback="+88791025", auth_token="jhjjhhmjhvhjvhjv", assistant="jhbhvhvhjvhjv"):
    try:
        # Create Phone Number (POST /phone-number)
        response = requests.post(
        "https://api.vapi.ai/phone-number",
        headers={
            "Authorization": f"Bearer {os.getenv('VAPI_API_KEY')}"
        },
        json={
            "provider": "twilio",
            "number": twillo_num,
            "twilioAccountSid": ssid,
            "name": name,
            "assistantId": assistant,
            "twilioAuthToken": auth_token,
            "smsEnabled": True,
            "fallbackDestination": {
            "type": "number",
            "number": restaurant_fallback
            }
        },
        )

        # print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to create phone number: {e}")