import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="gpt-5-nano", api_key=api_key, reasoning={"effort": "low"})

def format_exercises_data(data, indent=0):
    exercises_data = ""

    for item in data['data']['workouts_data']:
        exercises_data += f"id: {item['id']}, type: {item['exercise_type']}, name: {item['workout_name']};\n"

    return exercises_data
    
def workout_suggestion(
        height,
        weight,
        dob,
        gender,
        fitness_level,
        event,
        injuries,
        health_conditions,
        doctor_cleared,
        days_per_week,
        session_duration,
        training_environment,
        equipment_access,
        training_style,
        activeness_level,
        motivation_factors,
        start_date,
        exercises_data: dict
    ):
    exercises_data = format_exercises_data(exercises_data)
    response = [
        SystemMessage(content=f"You are a fitness expert specializing in creating personalized workout plans. You provide workout suggestions based on user preferences, fitness levels, and goals. MUST use the following exercise database to create the workout plans: {exercises_data}. STRICTLY return ONLY a valid JSON object with the structure: {{\"daily_workouts\": [{{'date': 'YYYY-MM-DD', 'completed': false, 'workouts': [{{'workout': id, 'series': 3, 'reps': 15, 'rest': 60}}, ...]}}, ...]}}. Generate dates starting from {start_date}, for 7 days. Use workout IDs from the database. Do not include any explanation, markdown, or text outside the JSON. The output must be valid JSON parsable by Python's json.loads(). Example output: {{\"daily_workouts\": [{{\"date\": \"2025-10-24\", \"workouts\": [{{\"workout\": 1, \"series\": 3, \"reps\": 15, \"rest\": 60}}, {{\"workout\": 2, \"series\": 3, \"reps\": 20, \"rest\": 60}}, {{\"workout\": 3, \"series\": 3, \"reps\": 45, \"rest\": 30}}]}}, {{\"date\": \"2025-10-25\", \"completed\": false, \"workouts\": [{{\"workout\": 4, \"series\": 3, \"reps\": 30, \"rest\": 45}}, {{\"workout\": 5, \"series\": 3, \"reps\": 12, \"rest\": 60}}, {{\"workout\": 6, \"series\": 3, \"reps\": 15, \"rest\": 45}}]}}, {{\"date\": \"2025-10-26\", \"completed\": false, \"workouts\": [{{\"workout\": 7, \"series\": 3, \"reps\": 20, \"rest\": 45}}, {{\"workout\": 1, \"series\": 3, \"reps\": 15, \"rest\": 60}}]}}, {{\"date\": \"2025-10-27\", \"completed\": false, \"workouts\": [{{\"workout\": 2, \"series\": 3, \"reps\": 18, \"rest\": 60}}, {{\"workout\": 5, \"series\": 3, \"reps\": 12, \"rest\": 60}}]}}, {{\"date\": \"2025-10-28\", \"completed\": false, \"workouts\": [{{\"workout\": 3, \"series\": 3, \"reps\": 45, \"rest\": 30}}, {{\"workout\": 6, \"series\": 3, \"reps\": 20, \"rest\": 45}}]}}, {{\"date\": \"2025-10-29\", \"completed\": false, \"workouts\": [{{\"workout\": 1, \"series\": 3, \"reps\": 20, \"rest\": 60}}, {{\"workout\": 7, \"series\": 3, \"reps\": 25, \"rest\": 45}}]}}, {{\"date\": \"2025-10-30\", \"completed\": false, \"workouts\": [{{\"workout\": 4, \"series\": 3, \"reps\": 30, \"rest\": 45}}, {{\"workout\": 2, \"series\": 3, \"reps\": 20, \"rest\": 60}}]}}]}}"),
        HumanMessage(content=f"Here are my preferences and goals: Height: {height}; Weight: {weight}; Date of Birth: {dob}; Gender: {gender}; Fitness Level: {fitness_level}; Specific Timeline or Event: {event}; Current Injuries or Physical Limitations: {injuries}; Chronic health conditions: {health_conditions}; Cleared by a doctor to exercise if you have health conditions or injuries: {doctor_cleared}; Days per week can you realistically commit to working out: {days_per_week}; Per workout session duration: {session_duration} minutes; Primary training environment: {training_environment}; Access to equipment: {equipment_access}; Preferred training style: {training_style}; Physical activeness level: {activeness_level}; Start date: {start_date}; Things that keep me motivated: {motivation_factors};")
    ]
    response = model.invoke(response)
    return response.content

def init_exercise(exercises_data):
    data = exercises_data

    workout_plan = workout_suggestion(
        height = data["data"]["fqa"]["profile_json"]["height"],
        weight = data["data"]["fqa"]["profile_json"]["weight"],
        dob = data["data"]["fqa"]["profile_json"]["date_of_birth"],
        gender = data["data"]["fqa"]["profile_json"]["gender"],
        fitness_level= data["data"]["fqa"]["fitness_level"],
        event = data["data"]["fqa"]["event"],
        injuries= data["data"]["fqa"]["profile_json"]["injuries_discomfort"],
        health_conditions= data["data"]["fqa"]["profile_json"]["medical_conditions"],
        doctor_cleared= data["data"]["fqa"]["doctor_clearance"],
        days_per_week= data["data"]["fqa"]["days_per_week"],
        session_duration= data["data"]["fqa"]["session_duration"],
        training_environment= data["data"]["fqa"]["training_environment"],
        equipment_access= data["data"]["fqa"]["equipments_access"],
        training_style= data["data"]["fqa"]["training_style"],
        activeness_level= data["data"]["fqa"]["activeness_level"],
        motivation_factors= data["data"]["fqa"]["motivation_factor"],
        start_date= data["data"]["workoutplan"]["start_date"],
        exercises_data=exercises_data
        )
    
    return json.loads(workout_plan[1]["text"])

# --------------------------------------------------------
with open("data/db_workout.json", "r", encoding="utf-8") as f:
    db_data = json.load(f)  # Load the JSON file

print(json.dumps(init_exercise(db_data), indent=2))