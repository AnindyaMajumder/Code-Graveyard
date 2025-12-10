from pydantic import BaseModel, Field
from datetime import date

class Meal(BaseModel):
    id: str = Field(..., description="Unique identifier for the meal")
    grams: int = Field(..., description="Weight of the meal in grams")
    calories: int = Field(..., description="Caloric content of the meal")
    protein_g: int = Field(..., description="Protein content in grams")
    fat_g : int = Field(..., description="Fat content in grams")
    carbs_g: int = Field(..., description="Carbohydrate content in grams")
    
class Food(BaseModel):
    all_meals: list[Meal] = Field(..., description="List of meals suggested by the AI")


class Workout(BaseModel):
    id: str = Field(..., description="Unique identifier for the workout")
    workout_name: str = Field(..., description="Name of the workout exercise")
    series: int = Field(..., description="Number of series for the workout")
    reps: int = Field(..., description="Number of repetitions per series")

class WorkoutPlan(BaseModel):
    id: str = Field(..., description="Unique identifier for the workout plan")
    plan_date: date = Field(..., description="Date of the workout plan")
    workouts: list[Workout] = Field(..., description="List of workouts included in the plan")