import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="gpt-5-nano", api_key=api_key, reasoning={"effort": "minimal"})
# minimal=7, low=15, medium=35, high=100

def format_meal_data(meal_data):
    categories = {}
    for meal in meal_data:
        cat = meal["category"].strip().upper()
        name = meal["food_name"].strip()
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(name)
    
    # Format into the desired string
    result_parts = []
    for cat, foods in categories.items():
        # Sort foods for consistency (optional)
        foods_sorted = sorted(foods)
        food_str = ", ".join(foods_sorted)
        result_parts.append(f"{cat}: {food_str}")
    
    # Sort categories for consistent output (optional)
    result_parts.sort()
    return "; ".join(result_parts)

def format_workout_data(data):
    daily_workouts = data["Active_Workout_Plan"]["daily_workouts"]
    result = []
    
    for day in daily_workouts:
        for w in day["workouts"]:
            name = w["workout"]["workout_name"].strip()
            series = w["series"]
            reps = w["reps"]
            result.append(f"{name}: {series} series, {reps} reps")
    
    return "; ".join(result)    

def meal_suggestion(
    height,
    weight,
    dob,
    gender,
    event,
    injuries,
    medical_conditions,
    doctor_cleared,
    environment,
    activeness,
    preferences,
    allergies,
    skipped,
    meal_data,
    workout_data
    ):
    response = [
        SystemMessage(content=f"""You are a fitness expert specializing in creating personalized meal plans based on dietary preferences and nutritional data. You have to calculate user diet requirements strictly following these steps: 1. Calculate BMR using the Mifflin-St Jeor Formula: Women: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161, Men: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5; 2. Calculate TDEE by multiplying BMR by the activity factor: Sedentary: 1.2, Lightly active: 1.375, Moderately active: 1.55, Very active: 1.725, Extremely active: 1.9; 3. Adjust calories based on goal: Fat loss: TDEE - 15-25%, Muscle gain: TDEE + 10-20%, Maintenance: TDEE; 4. Distribute macros: Protein: 1.6-2.2g/kg body weight, Fat: 0.8-1.2g/kg or ≥0.2 calories, Carbs: remaining calories. Generate a daily meal plan fitting the calculated requirements by adjusting grams and calories of the provided foods or suggesting similar Spanish foods if needed. Always output only a well-structured JSON. Here is the format: [{{"meal_plan":"Pre-Entreno","meals":[{{"meal":1,"grams":250.0,"calories":350.0,"protein_g":25.0,"fat_g":10.0,"carbs_g":40.0}},{{"meal":2,"grams":200.0,"calories":300.0,"protein_g":20.0,"fat_g":8.0,"carbs_g":35.0}}]}},{{"meal_plan":"Post-Entreno","meals":[{{"meal":3,"grams":180.0,"calories":250.0,"protein_g":18.0,"fat_g":5.0,"carbs_g":30.0}},{{"meal":4,"grams":300.0,"calories":400.0,"protein_g":30.0,"fat_g":12.0,"carbs_g":45.0}}]}},{{"meal_plan":"1","meals":[{{"meal":5,"grams":150.0,"calories":220.0,"protein_g":15.0,"fat_g":6.0,"carbs_g":25.0}}]}},{{"meal_plan":"2","meals":[{{"meal":6,"grams":300.0,"calories":350.0,"protein_g":22.0,"fat_g":10.0,"carbs_g":40.0}}]}},{{"meal_plan":"3","meals":[{{"meal":1,"grams":250.0,"calories":330.0,"protein_g":26.0,"fat_g":9.0,"carbs_g":38.0}},{{"meal":2,"grams":220.0,"calories":290.0,"protein_g":19.0,"fat_g":7.0,"carbs_g":33.0}}]}},{{"meal_plan":"4","meals":[{{"meal":3,"grams":180.0,"calories":260.0,"protein_g":17.0,"fat_g":6.0,"carbs_g":32.0}},{{"meal":4,"grams":320.0,"calories":430.0,"protein_g":33.0,"fat_g":14.0,"carbs_g":48.0}}]}}] No extra meal plan field should exist other than Pre-Entreno, Post-Entreno, 1, 2, 3, and 4. For each meal plan, one or more meals can be present.\n From the meal database suggest the meals, if not possible then go for outside meals. Here is the meal database:"""+ meal_data),
        HumanMessage(content=f"""Here are my preferences and goals: Height: {height} cm; Weight: {weight} kg; Date of Birth: {dob}; Gender: {gender}; Specific Timeline or Event: {event}; Current Injuries or Physical Limitations: {injuries}; Chronic medical conditions: {medical_conditions}; Cleared by a doctor to exercise if you have health conditions or injuries: {doctor_cleared}; Primary training environment: {environment}; Physical activeness level: {activeness}; Dietary preferences: {preferences}; Food allergies or intolerances: {allergies}; Foods I want to skip: {skipped};\n Here is my workout plan you MUST consider when creating the meal plans: {workout_data}.""")
    ]
    
    response = model.invoke(response)
    return response.content[1]["text"]

def init_mealplan(db_data):
    formatted_meals = format_meal_data(db_data["Meal_data"])
    formatted_workouts = format_workout_data(db_data)
    
    meals = meal_suggestion(
        height = db_data["fqa"]["profile_json"]["height"],
        weight = db_data["fqa"]["profile_json"]["weight"],
        dob = db_data["fqa"]["profile_json"]["date_of_birth"],
        gender = db_data["fqa"]["profile_json"]["gender"],
        event = db_data["fqa"]["event"],
        injuries = db_data["fqa"]["profile_json"]["injuries_discomfort"],
        medical_conditions = db_data["fqa"]["profile_json"]["medical_conditions"],
        doctor_cleared = db_data["fqa"]["doctor_clearance"],
        environment = db_data["fqa"]["training_environment"],
        activeness = db_data["fqa"]["activeness_level"],
        preferences = db_data["fqa"]["preferences"],
        allergies = db_data["fqa"]["profile_json"]["allergies"],
        skipped = db_data["fqa"]["skipped"],
        meal_data = formatted_meals,
        workout_data = formatted_workouts
    )
    
    return json.loads(meals)

# --------------------------------------------------------
with open("data/db_mealplan.json", "r", encoding="utf-8") as f:
    db_data = json.load(f)  # Load the JSON file
print(json.dumps(init_mealplan(db_data), indent=2))