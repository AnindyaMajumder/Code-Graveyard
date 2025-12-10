from datetime import date, datetime
import json
import time
from typing import Any, Dict

# Cache configuration
CACHE_TTL = 300  # Time to live in seconds (5 minutes)
_cache: Dict[str, Dict[str, Any]] = {}

def _load_json_cached(filepath: str) -> dict:
    """Load JSON file with TTL-based caching."""
    current_time = time.time()
    
    # Check if cached data exists and is still valid
    if filepath in _cache:
        cache_entry = _cache[filepath]
        if current_time - cache_entry['timestamp'] < CACHE_TTL:
            return cache_entry['data']
    
    # Load from file and update cache
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    _cache[filepath] = {
        'data': data,
        'timestamp': current_time
    }
    
    return data

def profile() -> str:
    profile_data = _load_json_cached("../data/profile.json") 
    # ----------------------------------------------------------------------------
    
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

def workout() -> str:
    workout_data = _load_json_cached("../data/user_workout.json")
    
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

def meal() -> str:
    meal_data = _load_json_cached("../data/user_meal.json")
    
    now_date = date.today().strftime('%Y-%m-%d')
    # Filter daily_meals for current date
    filtered_daily = [day for day in meal_data.get('daily_meals', []) if day['date'] == now_date]
    if not filtered_daily:
        return "No meal plan for today."
    day = filtered_daily[0]
    # Count remaining days
    remaining_days = sum(1 for d in meal_data.get('daily_meals', []) if d['date'] >= now_date)
    # Remove completed from meal_slots and entries
    day_filtered = {
        'id': day['id'],
        'date': day['date'],
        'meal_slots': []
    }
    for slot in day.get('meal_slots', []):
        slot_filtered = {k: v for k, v in slot.items() if k != 'completed'}
        slot_filtered['entries'] = []
        for entry in slot.get('entries', []):
            entry_filtered = {k: v for k, v in entry.items() if k != 'completed'}
            slot_filtered['entries'].append(entry_filtered)
        day_filtered['meal_slots'].append(slot_filtered)
        
    # Build string output
    day_lines = [f"id: {day_filtered['id']}", f"date: {day_filtered['date']}", f"Remaining days: {remaining_days}"]
    if day['date'] == meal_data.get('end_date'):
        day_lines.append("This is the last day of the meal plan.")
    
    for slot in day_filtered['meal_slots']:
        slot_lines = [f"slot_type: {slot['slot_type']}"]
        for entry in slot['entries']:
            entry_str = f"{entry['meal_name']}, grams: {entry['grams']}, calories: {entry['calories']}, protein_g: {entry['protein_g']}, fat_g: {entry['fat_g']}, carbs_g: {entry['carbs_g']}"
            slot_lines.append(entry_str)
        slot_str = "\n".join(slot_lines)
        day_lines.append(f"[{slot_str}],")

    return "\n".join(day_lines)