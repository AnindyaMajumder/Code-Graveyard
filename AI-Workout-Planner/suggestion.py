from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from datetime import date

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(model="gpt-5.1", api_key=api_key, max_retries=5)

class UserProfile(BaseModel):
    water_intake: float = Field(..., description="Daily water intake in liters")
    sleep_hours: float = Field(..., description="Average sleep hours per night")
    calorie_goal: int = Field(..., description="Daily calorie intake goal")

def suggest_workout(
    date_of_birth: date,
    weight: float,
    height: float,
    gender: str,
    trainer: str = None,
    fitness_goals: str = None,
    injuries_discomfort: str = None,
    dietary_preferences: str = None,
    allergies: str = None,
    medical_conditions: str = None
    ) -> str:
    
    prompt = f"""
    You are an expert fitness trainer. Based on the following user profile and preferences, suggest required water intake, sleep hours, calorie goals.\n Here is the user information:
    Date of Birth: {date_of_birth}
    Weight: {weight} kg
    Height: {height} cm
    Gender: {gender}
    Training environment: {trainer}
    Fitness Goals: {fitness_goals}
    Injuries or Discomfort: {injuries_discomfort}
    Dietary Preferences: {dietary_preferences}
    Allergies: {allergies}
    Medical Conditions: {medical_conditions}
    """
    
    response = model.with_structured_output(UserProfile).invoke(prompt)
    return response # type: UserProfile

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    user_profile = suggest_workout(
        date_of_birth=date(1990, 5, 15),
        weight=70,
        height=175,
        gender="male",
        trainer="Gym",
        fitness_goals="Build muscle and improve endurance",
        injuries_discomfort="None",
        dietary_preferences="Non-Vegetarian",
        allergies="Peanuts",
        medical_conditions="None"
    )
    print(type(user_profile))