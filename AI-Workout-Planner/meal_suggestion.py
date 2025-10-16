from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def format_meal_data(meal_data):
    output_lines = []

    # Iterate through the dictionary and collect food names and calories
    for category, foods in meal_data.items():
        # Add category label to the output
        output_lines.append(f"{category}:")
        
        # Collect each food item and its calories in a clean format
        for food in foods:
            food_name = food.get("food")
            calories = food.get("calories")
            output_lines.append(f"{food_name} - {calories} kcal,")

        if category != list(meal_data.keys())[-1]:
            output_lines.append("|")

    return " ".join(output_lines)

def meal_suggestion(
    height: str,
    weight: str,
    age: str,
    gender: str,
    level: str,
    event: str,
    injuries: str,
    medical_conditions: str,
    doctor_cleared: str,
    environment: str,
    style: str,
    activeness: str,
    preferences: str,
    allergies: str,
    skipped: str,
    frequency: str,
    meal_data: dict
    ):
    
    formatted_meal_data = format_meal_data(meal_data)
    
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
                        "text": """You are a fitness expert specializing in creating personalized meal plans based on dietary preferences and nutritional data. You have to calculate user diet requirements strictly following these steps: 1. Calculate BMR using Mifflin-St Jeor Formula (Women: (10 * weight_kg) + (6.25 * height_cm)-(5 * age) - 161; Men: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5); 2. Calculate TDEE by multiplying BMR by activity factor (Sedentary:*1.2, Lightly active:*1.375, Moderately active:*1.55, Very active:*1.725, Extremely active:*1.9); 3. Adjust calories based on goal (Fat loss: TDEE -15-25%, Muscle gain: TDEE +10-20%, Maintenance: TDEE); 4. Distribute macros (Protein: 1.6-2.2g/kg body weight, Fat: 0.8-1.2g/kg or ≥0.2 calories, Carbs: remaining calories); generate a daily meal plan fitting the calculated requirements by adjusting grams and calories of the provided foods or suggesting similar spanish foods if needed. Always MUST output only a well-structured JSON: {"requirements": {"bmr": number, "tdee": number, "goal_calories": number, "protein_g": number, "fat_g": number, "carbs_g": number}, "meals": [{"Breakfast": [{"food": "string", "grams": "string like '290 gm'", "calories": "string like '195'"}, ...], "Lunch": [{"food": "string", "grams": "string like '150 gm'", "calories": "string like '200'"}, ...], ...}], "total_calories": number, "advice": "string based on fine-tuning steps"}.\nUse the following food database to create the meal plans:"""+f" {formatted_meal_data}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Here are my details: height: {height}; weight: {weight}; age: {age}; gender: {gender}; fitness Level: {level}; specific goals or events: {event}; injuries: {injuries}; Medical Conditions: {medical_conditions}; Doctor Cleared: {doctor_cleared}; training Environment: {environment}; training Style: {style}; activeness Level: {activeness}; Dietary Preferences: {preferences}; Food Allergies: {allergies}; Skipped Meals: {skipped}; Meal Frequency: {frequency}"
                    }
                ]
            }
        ],
        reasoning={"effort": "high"}
    )
    
    return json.loads(response.output_text)

# ------------------------------------------------------------------------------------------------
with open("data/IA4.json", "r", encoding="utf-8") as f:
    meal_data = json.load(f)  # Load the JSON file

meal_plan = meal_suggestion(
    height="180 cm",
    weight="75 kg",
    age="28",
    gender="Male",
    level="Intermediate",
    event="Build muscle and improve cardiovascular health",
    injuries="None",
    medical_conditions="None",
    doctor_cleared="Yes",
    environment="Gym and Home",
    style="Mixed",
    activeness="Moderately active",
    preferences="Balanced diet with a mix of proteins, carbs, and fats",
    allergies="None",
    skipped="Occasionally breakfast",
    frequency="3 main meals and 2 snacks",
    meal_data=meal_data
)
print(json.dumps(meal_plan, indent=2))