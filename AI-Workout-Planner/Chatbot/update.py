from models import MealList, WorkoutList
import json

def update_meal(meal: MealList) -> str:
    print("\n\n==Update meal triggered==\n\n")
    print(json.dumps(meal.dict(), indent=2))
    print("\n========================\n")

def update_workout(workout: WorkoutList) -> str:
    print("\n\n==Update workout triggered==\n\n")
    print(json.dumps(workout.dict(), indent=2))
    print("\n========================\n")