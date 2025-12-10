from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph_supervisor.supervisor import create_react_agent
from langchain_core.tools import tool
from models import Food, WorkoutPlan

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
    
# Agents
llm = ChatOpenAI(model="gpt-4.1-nano", api_key= os.getenv("OPENAI_API_KEY"))

def Meal():
    try:
        meal_update_agent = create_react_agent(
            llm,
            response_format=Food,
            tools=[get_profile, get_meal],
            prompt = (
                "You are a meal plan update agent. Based on the user's profile data and current meal plan, "
                "provide updated meal suggestions that align with the user's dietary preferences, restrictions, "
                "and fitness goals. Ensure the meal plan is balanced and nutritious."
            ) ,
            name = "MealUpdateAgent"
        )
        return meal_update_agent
    except Exception as e:
        raise RuntimeError(f"Error in Meal agent: {str(e)}")

def Workout():
    try:
        workout_update_agent = create_react_agent(
            llm,
            tools=[get_profile, get_workout],
            response_format=WorkoutPlan,
            prompt = (
                "You are a workout plan update agent. Based on the user's profile data and current workout plan, "
                "provide updated workout suggestions that align with the user's fitness level, goals, and preferences. "
                "Ensure the workout plan is effective and safe."
            ) ,
            name = "WorkoutUpdateAgent"
        )
        return workout_update_agent
    except Exception as e:
        raise RuntimeError(f"Error in Workout agent: {str(e)}")
    
def Profile():
    try:
        profile_agent = create_react_agent(
            llm,
            tools=[get_profile],
            response_format=str,
            prompt = (
                "You are a user profile retrieval agent. Provide a summary of the user's fitness profile, "
                "including goals, preferences, and restrictions."
            ) ,
            name = "ProfileAgent"
        )
        return profile_agent
    except Exception as e:
        raise RuntimeError(f"Error in Profile agent: {str(e)}")