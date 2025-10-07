from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Load the JSON data
with open("data/BASE_DATOS.json", "r", encoding="utf-8") as f:
    data = json.load(f)
exercises_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# Response from the OpenAI
client = OpenAI(api_key=api_key)
response = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "system",
            "content": f"You are a fitness expert specializing in creating personalized workout plans. You provide workout suggestions based on user preferences, fitness levels, and goals. MUST use the following exercise database to create the workout plans: {exercises_data}. STRICTLY return ONLY a valid JSON array, where each element represents a day and has the following structure: {{'day': 'Day 1', 'exercises': [{{'exercise': 'Bench Press', 'series': 4, 'reps': 10, 'rest': '90s'}}, ...]}}. Do not include any explanation, markdown, or text outside the JSON. The output must be valid JSON parsable by Python's json.loads(). Example output:\n[\n  {{\n    \"day\": \"Day 1\",\n    \"exercises\": [\n      {{\n        \"exercise\": \"Bench Press\",\n        \"series\": 4,\n        \"reps\": 10,\n        \"rest\": \"90s\"\n      }},\n      {{\n        \"exercise\": \"Squat\",\n        \"series\": 4,\n        \"reps\": 12,\n        \"rest\": \"90s\"\n      }}\n    ]\n  }},\n  {{\n    \"day\": \"Day 2\",\n    \"exercises\": [\n      {{\n        \"exercise\": \"Deadlift\",\n        \"series\": 4,\n        \"reps\": 8,\n        \"rest\": \"120s\"\n      }}\n    ]\n  }}\n]"
        },
        {
            "role": "user",
            "content": f"""
            Here are my preferences and goals:\n
            - Fitness Level: Intermediate\n
            - Specific Timeline or Event: Build muscle and improve cardiovascular health\n
            - Current Injuries or Physical Limitations: None\n
            - Chronic health conditions: Heart Issues\n
            - Cleared by a doctor to exercise if you have health conditions or injuries: Yes\n
            - Days per week can you realistically commit to working out: 5\n
            - Per workout session duration: 60 minutes\n
            - Primary training environment: Gym\n
            - Access to equipment: Barbells, Dumbbells, Treadmill, Resistance Bands\n
            - Preferred training style: HIIT\n
            - Physical activeness level: active\n
            - Things that keep me motivated: Progress tracking, Variety in workouts\n
            """
        },
        {
            "role": "user",
            "content": "Based on the above information, please suggest a 6-day workout plan. The output MUST be a valid JSON array, where each element is an object with the following keys: 'day', 'exercise', 'series', 'reps', and 'rest'. Do not include any explanation, markdown, or text outside the JSON. The output must be valid JSON parsable by Python's json.loads()."
        }
    ],
)

print(response.output_text)