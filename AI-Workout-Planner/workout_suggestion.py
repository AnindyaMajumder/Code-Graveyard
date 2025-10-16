from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
    
    
def format_exercises_data(data, indent=0):
    formatted_string = ""
    
    # Loop through each key-value pair in the data
    for key, value in data.items():
        # If the value is a list, process it (likely exercises or similar data)
        if isinstance(value, list):
            formatted_string += f"{key.capitalize()}: "
            exercises_list = []
            for item in value:
                # Check if item is a dictionary with 'code' and 'name' keys (for exercises)
                if isinstance(item, dict) and 'code' in item and 'name' in item:
                    exercises_list.append(f"{item['code']}: {item['name']}")
            # Join all exercises for this body part with a delimiter
            formatted_string += " | ".join(exercises_list) + " | "
        elif isinstance(value, dict):
            # If the value is a dictionary (nested data), recurse into it
            formatted_string += format_exercises_data(value, indent + 1)
    
    # Remove the last delimiter
    if formatted_string.endswith(" | "):
        formatted_string = formatted_string[:-3]
    
    return formatted_string

def workout_suggestion(
        height: str,
        weight: str,
        age: str,
        gender: str,
        fitness_level: str,
        event: str,
        injuries: str,
        health_conditions: str,
        doctor_cleared: str,
        days_per_week: int,
        session_duration: int,
        training_environment: str,
        equipment_access: str,
        training_style: str,
        activeness_level: str,
        motivation_factors: str,
        exercises_data: dict
    ):
    exercises_data = format_exercises_data(exercises_data)
    
    # Response from the OpenAI
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"You are a fitness expert specializing in creating personalized workout plans. You provide workout suggestions based on user preferences, fitness levels, and goals. MUST use the following exercise database to create the workout plans: {exercises_data}. STRICTLY return ONLY a valid JSON array, where each element represents a day and has the following structure: {{'day': 'Day 1', 'exercises': [{{'exercise': 'Bench Press', 'series': 4, 'reps': 10, 'rest': '90s'}}, ...]}}. Do not include any explanation, markdown, or text outside the JSON. The output must be valid JSON parsable by Python's json.loads(). Example output: [{{\"day\": \"Day 1\", \"exercises\": [{{\"exercise\": \"Bench Press\", \"series\": 4, \"reps\": 10, \"rest\": \"90s\"}}, {{\"exercise\": \"Squat\", \"series\": 4, \"reps\": 12, \"rest\": \"90s\"}}]}}, {{\"day\": \"Day 2\", \"exercises\": [{{\"exercise\": \"Deadlift\", \"series\": 4, \"reps\": 8, \"rest\": \"120s\"}}]}}]"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Here are my preferences and goals: Height: {height}; Weight: {weight}; Age: {age}; Gender: {gender}; Fitness Level: {fitness_level}; Specific Timeline or Event: {event}; Current Injuries or Physical Limitations: {injuries}; Chronic health conditions: {health_conditions}; Cleared by a doctor to exercise if you have health conditions or injuries: {doctor_cleared}; Days per week can you realistically commit to working out: {days_per_week}; Per workout session duration: {session_duration} minutes; Primary training environment: {training_environment}; Access to equipment: {equipment_access}; Preferred training style: {training_style}; Physical activeness level: {activeness_level}; Things that keep me motivated: {motivation_factors};"
                    }
                ]
            }
        ],
        reasoning={"effort": "high"}
    )
    
    return json.loads(response.output_text)

# ------------------------------------------------------------------------------------------------
with open("data/BASE_DATOS.json", "r", encoding="utf-8") as f:
    exercises_data = json.load(f)  # Load the JSON file

workout_plan = workout_suggestion(
    height="180 cm",
    weight="75 kg",
    age="28",
    gender="Male",
    fitness_level="Intermediate",
    event="Build muscle and improve cardiovascular health",
    injuries="None",
    health_conditions="Heart Issues",
    doctor_cleared="Yes",
    days_per_week=5,
    session_duration=60,
    training_environment="Gym",
    equipment_access="Barbells, Dumbbells, Treadmill, Resistance Bands",
    training_style="HIIT",
    activeness_level="active",
    motivation_factors="Progress tracking, Variety in workouts",
    exercises_data=exercises_data
    )
print(json.dumps(workout_plan, indent=2))