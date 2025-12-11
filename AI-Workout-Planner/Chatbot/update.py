from models import Meal, WorkoutPlan
import json

def update_meal(meal: Meal) -> str:
    # print(json.dumps(meal.dict(), indent=2))
    print("\n\n==Update meal triggered==\n\n")
    
def update_workout(workout: WorkoutPlan) -> str:
    # print(json.dumps(workout.dict(), indent=2))
    print("\n\n==Update workout triggered==\n\n")