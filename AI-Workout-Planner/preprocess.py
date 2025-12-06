from datetime import date, datetime
import json

def profile(profile_data: dict) -> str:
    def flatten_dict(d, prefix='', skip_keys=None):
        if skip_keys is None:
            skip_keys = []
        items = []
        for k, v in d.items():
            if k in skip_keys:
                continue
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, skip_keys))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(flatten_dict(item, f"{new_key}[{i}]", skip_keys))
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        return items
    
    all_items = {}
    # Flatten profile
    prof = profile_data.get('profile', {})
    for k, v in flatten_dict(prof):
        all_items[k] = v
    # Flatten UserMealFQA, skip profile_json
    meal_fqa = profile_data.get('UserMealFQA', {})
    for k, v in flatten_dict(meal_fqa):
        if not k.startswith('profile_json'):
            all_items[k] = v
    # Flatten UserWorkoutFQA, skip profile_json
    workout_fqa = profile_data.get('UserWorkoutFQA', {})
    for k, v in flatten_dict(workout_fqa):
        if not k.startswith('profile_json'):
            all_items[k] = v
    # Create string
    items = [f"{k}: {v}" for k, v in all_items.items()]
    return "\n".join(items)

def workout(workout_data: dict) -> str:
    now_date = date.today()
    # Filter daily_workouts for current and future dates
    filtered_daily = []
    for day in workout_data.get('daily_workouts', []):
        day_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
        if day_date >= now_date:
            # Keep only id, date, workouts
            day_filtered = {
                'id': day['id'],
                'date': day['date'],
                'workouts': []
            }
            for w in day.get('workouts', []):
                # Remove completed and keep other fields
                w_filtered = {k: v for k, v in w.items() if k != 'completed'}
                day_filtered['workouts'].append(w_filtered)
            filtered_daily.append(day_filtered)
    
    # Build string output as list of blocks
    day_blocks = []
    for day in filtered_daily:
        day_lines = [f"id: {day['id']}", f"date: {day['date']}"]
        for w in day['workouts']:
            workout_str = f"{w['workout_name']}, series: {w['series']}, reps: {w['reps']}, rest: {w['rest']}"
            day_lines.append(workout_str)
        day_str = "\n".join(day_lines)
        day_blocks.append(f"[{day_str}]")
    return ",\n".join(day_blocks)

# ----------------------------------------------------------------------------
with open("data/user_workout.json", "r", encoding="utf-8") as f:
    workout_data = json.load(f)  # Load the JSON file
    processed_data = workout(workout_data)
    print(processed_data)