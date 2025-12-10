from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph_supervisor.supervisor import create_react_agent
from langchain_core.tools import tool
from models import Food, WorkoutPlan, MealResponse, WorkoutResponse, ProfileResponse

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
            response_format=MealResponse,
            tools=[get_profile, get_meal],
            prompt = (
                "You are a meal planning assistant with access to the user's profile and current meal plan.\n\n"
                "IMPORTANT INSTRUCTIONS:\n"
                "1. ALWAYS use get_profile() and get_meal() tools to retrieve current user data first.\n"
                "2. For general questions or queries about meals/nutrition:\n"
                "   - Provide conversational, friendly responses in the 'explanation' field\n"
                "   - Reference the user's current meal plan, preferences, allergies, and restrictions\n"
                "   - Set 'structured_update' to null\n\n"
                "3. For meal plan UPDATE requests (keywords: 'update', 'change', 'modify', 'create new', 'suggest new'):\n"
                "   - Provide a conversational explanation comparing current vs. suggested meals in 'explanation'\n"
                "   - Include reasoning for changes (e.g., 'Based on your goal to gain muscle, I increased protein')\n"
                "   - Populate 'structured_update' with the complete new meal plan using Food model\n"
                "   - Ensure meals align with dietary preferences, restrictions (allergies, medical conditions), and fitness goals\n\n"
                "4. Make responses personal and context-aware:\n"
                "   - 'I see you currently have...' or 'Looking at your meal plan...'\n"
                "   - Reference specific user data like allergies, goals, preferences\n"
                "   - Explain nutritional balance (calories, protein, carbs, fats)\n\n"
                "Always be helpful, supportive, and ensure meal suggestions are safe and appropriate for the user."
            ),
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
            response_format=WorkoutResponse,
            prompt = (
                "You are a workout planning assistant with access to the user's profile and current workout plan.\n\n"
                "IMPORTANT INSTRUCTIONS:\n"
                "1. ALWAYS use get_profile() and get_workout() tools to retrieve current user data first.\n"
                "2. For general questions or queries about workouts/fitness:\n"
                "   - Provide conversational, friendly responses in the 'explanation' field\n"
                "   - Reference the user's current workout plan, fitness level, goals, and preferences\n"
                "   - Set 'structured_update' to null\n\n"
                "3. For workout plan UPDATE requests (keywords: 'update', 'change', 'modify', 'create new', 'suggest new'):\n"
                "   - Provide a conversational explanation comparing current vs. suggested workouts in 'explanation'\n"
                "   - Include reasoning for changes (e.g., 'Based on your intermediate level, I added progressive overload')\n"
                "   - Populate 'structured_update' with the complete new workout plan using WorkoutPlan model\n"
                "   - Ensure workouts match fitness level, available equipment, training environment, and goals\n\n"
                "4. Make responses personal and context-aware:\n"
                "   - 'I see your current plan includes...' or 'Looking at your workout schedule...'\n"
                "   - Reference specific user data like fitness level, equipment access, training style\n"
                "   - Explain exercise selection, volume (sets/reps), and progression\n\n"
                "Always prioritize safety, proper form, and progressive overload principles."
            ),
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
            response_format=ProfileResponse,
            prompt = (
                "You are a user profile assistant with access to the user's fitness profile data.\n\n"
                "IMPORTANT INSTRUCTIONS:\n"
                "1. ALWAYS use get_profile() tool to retrieve current user data first.\n"
                "2. Provide conversational, friendly responses in the 'explanation' field.\n"
                "3. Reference specific user data like:\n"
                "   - Personal details (name, age, gender, weight, height, body measurements)\n"
                "   - Fitness goals and objectives\n"
                "   - Dietary preferences and restrictions (allergies, medical conditions)\n"
                "   - Workout preferences (training style, equipment access, fitness level)\n"
                "   - Activity level and training frequency\n\n"
                "4. Make responses personal and informative:\n"
                "   - Address the user's specific question about their profile\n"
                "   - Use friendly, supportive language\n"
                "   - Provide relevant context when appropriate\n\n"
                "Always be helpful and ensure the user understands their profile information."
            ),
            name = "ProfileAgent"
        )
        return profile_agent
    except Exception as e:
        raise RuntimeError(f"Error in Profile agent: {str(e)}")