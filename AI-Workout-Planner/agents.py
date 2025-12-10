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
def get_profile(
    query: Annotated[str, "User's specific data required for updating the meal plan and workout plan"],
    ) -> str:
    """Get the user's profile data including fitness goals, preferences, and restrictions."""
    try:
        return profile()
    except Exception as e:
        return f"Error retrieving profile data: {str(e)}"

@tool
def get_workout(
    query: Annotated[str, "User's specific data required for updating the workout plan"],
    ) -> str:
    """Get the user's current workout plan and exercise data."""
    try:
        return workout()
    except Exception as e:
        return f"Error retrieving workout data: {str(e)}"
    
@tool
def get_meal(
    query: Annotated[str, "User's specific data required for updating the meal plan"],
    ) -> str:
    """Get the user's current meal plan and dietary information."""
    try:
        return meal()
    except Exception as e:
        return f"Error retrieving meal data: {str(e)}"
    
# Agents
def Agents(agent: str):
    llm = ChatOpenAI(model="gpt-5-nano", api_key= os.getenv("OPENAI_API_KEY"))

    if (agent == "meal"):
        meal_update_agent = create_react_agent(
            llm.with_structured_output(Food),
            tools=[get_profile, get_meal],
            prompt = (
                "You are a meal plan update agent. Based on the user's profile data and current meal plan, "
                "provide updated meal suggestions that align with the user's dietary preferences, restrictions, "
                "and fitness goals. Ensure the meal plan is balanced and nutritious."
            ) ,
            name = "MealUpdateAgent"
        )
        return meal_update_agent
    elif (agent == "workout"):
        workout_update_agent = create_react_agent(
            llm.with_structured_output(WorkoutPlan),
            tools=[get_profile, get_workout],
            prompt = (
                "You are a workout plan update agent. Based on the user's profile data and current workout plan, "
                "provide updated workout suggestions that align with the user's fitness level, goals, and preferences. "
                "Ensure the workout plan is effective and safe."
            ) ,
            name = "WorkoutUpdateAgent"
        )
        return workout_update_agent
    else:
        raise ValueError("Invalid agent type. Choose 'meal' or 'workout'.")