from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph_supervisor.supervisor import create_react_agent
from langchain_core.tools import tool
from models import MealList, WorkoutList
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
def update_workoutplan(new_workout_plan: WorkoutList) -> str:
    """Update the user's workout plan with the provided new workout plan."""
    try:
        update_workout(new_workout_plan)
        return "Workout plan updated successfully."
    except Exception as e:
        return f"Error updating workout plan: {str(e)}"
    
@tool
def update_mealplan(new_meal_plan: MealList) -> str:
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
        "- CRITICAL: When calling `update_mealplan`, you MUST include ALL dates returned by `get_meal`.\n"
        "- Even if the user only wants to modify one or two days, include every date in the update.\n"
        "- For dates that are not being updated (if requested), keep their original meal data exactly as returned by `get_meal`.\n\n"
        "- IMPORTANT: Use the EXACT `id` and `date` values from `get_meal` - do NOT generate or modify these values.\n"
        "- For each Slot and Meal, also preserve the original `id` from `get_meal` unless adding new items.\n"
        "- Use the MealList structure with all_data containing a list of DailyMeal entries.\n"
        "- Each DailyMeal must have: id (from get_meal), date (from get_meal), and meal_slots (list of Slot objects).\n"
        "- Each Slot must have: id (from get_meal), slot_type ('pre-entreno', 'post-entreno', '1', '2', '3', or '4'), and entries (list of Meal objects).\n"
        "- Each Meal must have: id (from get_meal), meal_name, grams, calories, protein_g, fat_g, carbs_g.\n"
        "- Provide precise justification comparing current vs. suggested meals.\n"
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
            "MANDATORY WORKFLOW - Follow these steps IN ORDER:\n"
            "1. FIRST: Call `get_profile` to understand user fitness goals, preferences, restrictions\n"
            "2. SECOND: Call `get_workout` to get current workout plan\n"
            "3. THIRD: Call `update_workoutplan` with the modified plan - DO NOT skip this step!\n"
            "4. FOURTH: Respond to user confirming what was updated\n\n"
            "CRITICAL RULES:\n"
            "- You MUST ALWAYS call `update_workoutplan` - never just describe changes without calling the tool\n"
            "- Do NOT ask clarifying questions - make reasonable assumptions based on profile and update immediately\n"
            "- When calling `update_workoutplan`, include ALL dates from `get_workout`\n"
            "- Use EXACT `id` and `date` values from `get_workout` - do NOT generate or modify these\n"
            "- For dates not being changed, keep their original workout data exactly as returned\n"
            "- Preserve original `id` for each Workout unless adding new exercises\n\n"
            "STRUCTURE:\n"
            "- WorkoutList: all_data containing list of WorkoutPlan entries\n"
            "- WorkoutPlan: id, date, workouts (list of Workout objects)\n"
            "- Workout: id, workout_name, series, reps, rest\n\n"
            "Always prioritize safety, proper form, and progressive overload principles."
        ),
        name = "WorkoutUpdateAgent"
    )
except Exception as e:
        raise RuntimeError(f"Error in Workout agent: {str(e)}")