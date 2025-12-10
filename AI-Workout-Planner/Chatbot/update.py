from models import MealResponse, WorkoutResponse, ProfileResponse
import json

def update_meal(meal: MealResponse) -> str:
    # print(json.dumps(meal.dict(), indent=2))
    print("==Update meal triggered==")
    
def update_workout(workout: WorkoutResponse) -> str:
    # print(json.dumps(workout.dict(), indent=2))
    print("==Update workout triggered==")