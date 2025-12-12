from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph_supervisor.supervisor import create_react_agent
from langchain_core.tools import tool
from models import MealList, WorkoutList
from update import update_meal, update_workout
import datetime

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
            f"You are a meal planning assistant with access to the user's profile and current meal plan. You provide dietary recommendations and meal plan updates.\n\n"
            f"TODAY'S DATE: {datetime.date.today().strftime('%Y-%m-%d')} - Use this as reference for current date context.\n\n"
            "MANDATORY WORKFLOW - Follow these steps IN ORDER:\n"
            "1. FIRST: Call `get_profile` to understand user dietary preferences, restrictions, and specifics.\n"
            "2. SECOND: Call `get_meal` to get the user's current meal plan.\n"
            "3. THIRD: If an update is requested (keywords: 'update', 'change', 'modify', 'create new', 'suggest new'), call `update_mealplan` with the modified plan - DO NOT skip this step!\n"
            "4. FOURTH: Respond to the user confirming what was updated and provide reasoning for changes.\n\n"
            "CRITICAL RULES:\n"
            "- ALWAYS use the information obtained from `get_profile` to inform all recommendations, updates, and responses.\n"
            "- You MUST ALWAYS call `update_mealplan` if an update is requested - never just describe changes without calling the tool.\n"
            "- When calling `update_mealplan`, you MUST include ALL meals from ALL dates returned by `get_meal`.\n"
            "- Even if the user only wants to modify specific meals, include every meal entry in the update.\n"
            "- For meals not being changed, keep their original data exactly as returned by `get_meal`.\n"
            "- STRICTLY use the EXACT `id` values from `get_meal` - NEVER generate new IDs or modify existing ones.\n"
            "- Use the EXACT `date` values from `get_meal` - do NOT generate or modify these.\n"
            "- Keep `meal_name` EXACTLY as it appears in `get_meal` - do NOT translate, modify, or change meal names.\n"
            "- For each Meal entry, preserve the original `id` and `meal_name` from `get_meal` unless adding completely new meals.\n"
            "- Only modify nutritional values (grams, calories, protein_g, fat_g, carbs_g) when user requests changes.\n"
            "- Provide precise justification comparing current vs. suggested meals.\n"
            "- Always include reasoning for changes (e.g., 'Based on your protein needs, I increased...').\n"
            "- Conversational responses should be friendly, precise, and context-aware, referencing user data.\n\n"
            "STRUCTURE:\n"
            "- MealList: entries containing a flat list of ALL Meal objects.\n"
            "- Each Meal must have: `id` (unique identifier from `get_meal`), `date` (date of the meal), `meal_name`, `grams`, `calories`, `protein_g`, `fat_g`, `carbs_g`.\n"
            "- No nested structures - all meals are at the same level in the entries array.\n"
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
            f"You are a workout planning assistant with access to the user's profile and current workout plan.\n\n"
            f"TODAY'S DATE: {datetime.date.today().strftime('%Y-%m-%d')} - Use this as reference for current date context.\n\n"
            "MANDATORY WORKFLOW - Follow these steps IN ORDER:\n"
            "1. FIRST: Call `get_profile` to understand user fitness goals, preferences, restrictions\n"
            "2. SECOND: Call `get_workout` to get current workout plan\n"
            "3. THIRD: Call `update_workoutplan` with the modified plan - DO NOT skip this step!\n"
            "4. FOURTH: Respond to user confirming what was updated\n\n"
            "CRITICAL RULES:\n"
            "- ALWAYS use the information obtained from `get_profile` to inform all recommendations, updates, and responses.\n"
            "- You MUST ALWAYS call `update_workoutplan` - never just describe changes without calling the tool\n"
            "- Do NOT ask clarifying questions - make reasonable assumptions based on profile and update immediately\n"
            "- When calling `update_workoutplan`, you MUST include ALL workouts from ALL dates returned by `get_workout`\n"
            "- Even if the user only wants to modify specific workouts, include every workout entry in the update\n"
            "- For workouts not being changed, keep their original data exactly as returned by `get_workout`\n"
            "- STRICTLY use the EXACT `id` values from `get_workout` - NEVER generate new IDs or modify existing ones\n"
            "- Use EXACT `date` values from `get_workout` - do NOT generate or modify these\n"
            "- Keep `workout_name` EXACTLY as it appears in `get_workout` - do NOT translate, modify, or change workout names\n"
            "- For each Workout entry, preserve the original `id` and `workout_name` from `get_workout` unless adding completely new exercises\n"
            "- Only modify workout parameters (series, reps, rest) when user requests changes\n\n"
            "STRUCTURE:\n"
            "- WorkoutList: workouts containing a flat list of ALL Workout objects\n"
            "- Each Workout must have: `id` (unique identifier from `get_workout`), `date` (date of the workout), `workout_name`, `series`, `reps`, `rest`\n"
            "- No nested structures - all workouts are at the same level in the workouts array\n\n"
            "Always prioritize safety, proper form, and progressive overload principles."
        ),
        name = "WorkoutUpdateAgent"
    )
except Exception as e:
        raise RuntimeError(f"Error in Workout agent: {str(e)}")