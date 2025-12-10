from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class Meal(BaseModel):
    id: str = Field(..., description="Unique identifier for the meal")
    grams: int = Field(..., description="Weight of the meal in grams")
    calories: int = Field(..., description="Caloric content of the meal")
    protein_g: int = Field(..., description="Protein content in grams")
    fat_g : int = Field(..., description="Fat content in grams")
    carbs_g: int = Field(..., description="Carbohydrate content in grams")

class Workout(BaseModel):
    id: str = Field(..., description="Unique identifier for the workout")
    workout_name: str = Field(..., description="Name of the workout exercise")
    series: int = Field(..., description="Number of series for the workout")
    reps: int = Field(..., description="Number of repetitions per series")

class WorkoutPlan(BaseModel):
    id: str = Field(..., description="Unique identifier for the workout plan")
    plan_date: date = Field(..., description="Date of the workout plan")
    workouts: list[Workout] = Field(..., description="List of workouts included in the plan")


# Hybrid response models for conversational + structured output
class MealResponse(BaseModel):
    """Response model for meal-related queries with optional structured update data."""
    explanation: str = Field(..., description="Conversational explanation of the response, including current meal data awareness and reasoning for any suggestions")
    structured_update: Optional[list[Meal]] = Field(None, description="Structured meal plan update data, only provided when user explicitly requests meal plan updates")

class WorkoutResponse(BaseModel):
    """Response model for workout-related queries with optional structured update data."""
    explanation: str = Field(..., description="Conversational explanation of the response, including current workout data awareness and reasoning for any suggestions")
    structured_update: Optional[WorkoutPlan] = Field(None, description="Structured workout plan update data, only provided when user explicitly requests workout plan updates")

class ProfileResponse(BaseModel):
    """Response model for profile-related queries."""
    explanation: str = Field(..., description="Conversational response about the user's fitness profile, goals, preferences, and restrictions")