from models import MealList, WorkoutList
import json

def update_meal(meal: MealList) -> str:
    print("\n\n==Update meal triggered==\n\n", flush=True)

    try:
        with open("meal_data.json", "w") as f:
            f.write(json.dumps(meal.model_dump(mode='json'), indent=2))
    except Exception as e:
        raise e
    print("\n========================\n", flush=True)

def update_workout(workout: WorkoutList) -> str:
    print("\n\n==Update workout triggered==\n\n", flush=True)
    try:
        with open("workout_data.json", "w") as f:
            f.write(json.dumps(workout.model_dump(mode='json'), indent=2))
    except Exception as e:
        raise e       
    print("\n========================\n", flush=True)