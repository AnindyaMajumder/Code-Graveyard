from models import MealList, WorkoutList
import json

def update_meal(meal: MealList) -> str:
    print("\n\n==Update meal triggered==\n\n", flush=True)

    with open("meal_data.json", "w") as f:
        f.write(json.dumps(meal.model_dump(), indent=2))
    
    print("Meal data saved to meal_data.json", flush=True)
    print("\n========================\n", flush=True)

def update_workout(workout: WorkoutList) -> str:
    print("\n\n==Update workout triggered==\n\n", flush=True)
    print(f"DEBUG: Received type: {type(workout)}", flush=True)
    try:
        if isinstance(workout, dict):
             print(f"DEBUG: It's a dict: {json.dumps(workout, indent=2)}", flush=True)
             data_to_save = workout
        else:
             print(f"DEBUG: It's a Pydantic model", flush=True)
             data_to_save = workout.model_dump()
        
        with open("workout_data.json", "w") as f:
            f.write(json.dumps(data_to_save, indent=2))

        print("Workout data saved to workout_data.json", flush=True)
    except Exception as e:
        print(f"DEBUG: Error in update_workout: {e}", flush=True)
        import traceback
        traceback.print_exc()

    print("\n========================\n", flush=True)