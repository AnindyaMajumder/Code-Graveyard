from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph_supervisor.supervisor import create_react_agent
from langchain_core.tools import tool
from models import Meal, WorkoutPlan
from update import update_meal, update_workout

import os
from dotenv import load_dotenv
load_dotenv()

from preprocess import profile, workout, meal

@tool
def get_profile() -> str:
    """Get the user's profile data including fitness goals, preferences, and restrictions."""
    try:
        return profile()
    except Exception as e:
        return f"Error retrieving profile data: {str(e)}"

@tool
def get_workout() -> str:
    """Get the user's current workout plan and exercise data."""
    try:
        return workout()
    except Exception as e:
        return f"Error retrieving workout data: {str(e)}"
    
@tool
def get_meal() -> str:
    """Get the user's current meal plan and dietary information."""
    try:
        return meal()
    except Exception as e:
        return f"Error retrieving meal data: {str(e)}"
    
@tool
def update_workoutplan(new_workout_plan: WorkoutPlan) -> str:
    """Update the user's workout plan with the provided new workout plan."""
    try:
        update_workout(new_workout_plan)
        return "Workout plan updated successfully."
    except Exception as e:
        return f"Error updating workout plan: {str(e)}"
    
@tool
def update_mealplan(new_meal_plan: Meal) -> str:
    """Update the user's meal plan with the provided new meal plan."""
    try:
        update_meal(new_meal_plan)
        return "Meal plan updated successfully."
    except Exception as e:
        return f"Error updating meal plan: {str(e)}"
    
# Agents
llm = ChatOpenAI(model="gpt-4.1-nano", api_key= os.getenv("OPENAI_API_KEY"))


try:
    meal_update_agent = create_react_agent(
        llm,
        tools=[get_profile, get_meal, update_mealplan],
        prompt = (
        "You are a meal planning assistant with access to the user's profile and current meal plan. You provide dietary recommendations and meal plan updates.\n\n"
        "Use `get_meal` to get current meal plan before responding.\n"
        "Always use `get_profile` to understand user dietary preferences, restrictions and user specifics.\n\n"
        "If user requests meal plan UPDATE (keywords: 'update', 'change', 'modify', 'create new', 'suggest new', etc):\n"
        "- Provide precise justification in 'explanation' field comparing current vs. suggested meals\n"
        "Always include reasoning for changes (e.g., 'Based on your protein needs, I increased...')\n"
        "Conversational responses should be friendly, precise and context-aware referencing user data.\n"
        ),
        name = "MealUpdateAgent"
    )
except Exception as e:
        raise RuntimeError(f"Error in Meal agent: {str(e)}")


try:
    workout_update_agent = create_react_agent(
        llm,
        tools=[get_profile, get_workout, update_workoutplan],
        prompt = (
            "You are a workout planning assistant with access to the user's profile and current workout plan.\n\n"
            "Use `get_workout` to get current workout plan before responding.\n"
            "Always use `get_profile` to understand user fitness goals, preferences, restrictions and specifics.\n\n"
            "If user requests workout plan UPDATE (keywords: 'update', 'change', 'modify', 'create new', 'suggest new', etc):\n"
            "- Provide precise justification in 'explanation' field comparing current vs. suggested workouts\n"
            "Always prioritize safety, proper form, and progressive overload principles."
        ),
        name = "WorkoutUpdateAgent"
    )
except Exception as e:
        raise RuntimeError(f"Error in Workout agent: {str(e)}")