from pydantic import BaseModel, Field
from datetime import date as dt
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
    rest: int = Field(..., description="Rest time between series in seconds")

class WorkoutPlan(BaseModel):
    id: str = Field(..., description="Unique identifier for the workout plan")
    date: dt = Field(..., description="Date of the workout plan")
    workouts: list[Workout] = Field(..., description="List of workouts included in the plan")