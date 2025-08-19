import openai
import json
import os
import numpy as np
import faiss
import pickle
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# === Configuration ===
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Recipe Data ===
def load_recipes():
    try:
        with open("recipes.json", "r", encoding="utf-8") as f:
            recipes = json.load(f)
        return recipes
    except FileNotFoundError:
        print("Error: recipes.json file not found.")
        return []

RECIPES = load_recipes()

_QUERY_EMBED_CACHE = {}  # in-memory cache for query embeddings

# === Embedding with IndexHNSW ===
def embed_recipe_descriptions(recipes):
    EMBEDDING_PATH = "index/recipe_embeddings.faiss"
    PICKLE_PATH = "index/recipe_embeddings.pkl"
    descriptions = [recipe["recipe_name"] + " " + recipe["ingredients"] for recipe in recipes]

    if os.path.exists(EMBEDDING_PATH) and os.path.exists(PICKLE_PATH):
        index = faiss.read_index(EMBEDDING_PATH)
        with open(PICKLE_PATH, "rb") as f:
            embeddings = pickle.load(f)
        return embeddings, index

    # Create embeddings (single batch for small datasets)
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=descriptions
    )
    embeddings_list = [item.embedding for item in response.data]
    embeddings = np.array(embeddings_list, dtype="float32")

    # Use IndexHNSW for faster search
    dimension = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dimension, 32)
    index.hnsw.efConstruction = 40
    index.hnsw.efSearch = 32
    index.add(embeddings)

    os.makedirs(os.path.dirname(EMBEDDING_PATH), exist_ok=True)
    faiss.write_index(index, EMBEDDING_PATH)
    with open(PICKLE_PATH, "wb") as f:
        pickle.dump(embeddings, f)

    return embeddings, index

def _batch_embed_queries(queries):
    """Embed only unseen queries in one batch (fix 2 & 3)."""
    unseen = [q for q in queries if q not in _QUERY_EMBED_CACHE]
    if unseen:
        resp = openai.embeddings.create(model="text-embedding-3-small", input=unseen)
        for q, item in zip(unseen, resp.data):
            _QUERY_EMBED_CACHE[q] = np.array(item.embedding, dtype="float32")
    return {q: _QUERY_EMBED_CACHE[q] for q in queries}

def semantic_search_from_embedding(query_embedding, recipes, index, k=5):
    index.hnsw.efSearch = 32
    D, I = index.search(np.array([query_embedding], dtype="float32"), k)
    return [recipes[i] for i in I[0]]

# === Meal Plan Generator ===
def generate_meal_plan(user_data, recipes, embeddings, index):
    """Generate a 7-day meal plan with a single retrieval pass (fix 1)."""
    plan_user = {
        "name": user_data["fullname"],
        "gender": user_data["gender"],
        "age": (datetime.today() - datetime.strptime(user_data["date_of_birth"], "%Y-%m-%d")).days // 365,
        "weight_kg": user_data["weight"],
        "height_cm": user_data["height"],
        "fitness_goal": user_data["fitness_goal"],
        "lifestyle": user_data["lifestyle_habits"][0] if user_data["lifestyle_habits"] else "Unknown"
    }


    meal_types = [
        ("Breakfast", "08:00"),
        ("Snack 1", "11:00"),
        ("Lunch", "13:30"),
        ("Snack 2", "16:00"),
        ("Dinner", "19:30")
    ]

    # Filter recipes by allergies and dietary preferences
    def recipe_ok(recipe):
        # Check allergies
        for allergen in user_data.get("allergies", []):
            if allergen.lower() in recipe.get("ingredients", "").lower():
                return False
        # Check dietary preferences
        for pref in user_data.get("dietary_preferences", []):
            if pref.lower() not in recipe.get("tags", "").lower():
                return False
        # Check nutritional info if present (example: calories)
        if "calories" in recipe and user_data.get("fitness_goal"):
            goal = user_data["fitness_goal"].lower()
            if goal == "weight loss" and recipe["calories"] > 600:
                return False
            if goal == "muscle gain" and recipe["calories"] < 300:
                return False
        return True

    # Build distinct queries (one per meal type)
    queries = [
        f"{meal_type} for {user_data['fitness_goal']} with {', '.join(user_data.get('dietary_preferences', []))} avoiding {', '.join(user_data.get('allergies', []))}" 
        for meal_type, _ in meal_types
    ]

    # Batch embed unique queries + cache results
    query_embeddings = _batch_embed_queries(queries)

    # Retrieve candidates once per meal type, filter for restrictions
    meal_type_to_candidates = {}
    top_k = 10  # get more for variety and fallback
    for (meal_type, _), q in zip(meal_types, queries):
        candidates = semantic_search_from_embedding(query_embeddings[q], recipes, index, k=top_k)
        filtered = [r for r in candidates if recipe_ok(r)]
        # fallback: if not enough, fill with any recipe that fits
        if len(filtered) < 7:
            filtered += [r for r in recipes if recipe_ok(r) and r not in filtered][:7-len(filtered)]
        meal_type_to_candidates[meal_type] = filtered if filtered else candidates[:7]

    # Build schedule selecting one candidate per day, avoid repeats
    days_schedule = []
    used_recipes = set()
    for day in range(7):
        day_meals = []
        for meal_type, time in meal_types:
            candidates = meal_type_to_candidates.get(meal_type, [])
            # Prefer unused recipes for variety
            recipe = None
            for r in candidates:
                if r["unique_id"] not in used_recipes:
                    recipe = r
                    break
            if not recipe:
                recipe = candidates[day % len(candidates)] if candidates else None
            if recipe:
                used_recipes.add(recipe["unique_id"])
                day_meals.append((meal_type, time, recipe))
        days_schedule.append(day_meals)

    today = datetime.today()
    # Collect all ingredients_en for the week
    all_ingredients_en = []
    meal_indices = []  # (day_idx, meal_idx) for mapping
    for day_idx, day_meals in enumerate(days_schedule):
        for meal_idx, (meal_type, time, recipe) in enumerate(day_meals):
            all_ingredients_en.append(recipe["ingredients"])
            meal_indices.append((day_idx, meal_idx))

    # Prepare a single prompt with all ingredient lists
    numbered_list = "\n".join([f"{i+1}. {ing}" for i, ing in enumerate(all_ingredients_en)])
    translation_prompt = (
        "Translate the following list of ingredients from English to Spanish. Ignore '\\t\\n'. "
        "Reply with only the translated ingredients, numbered as in the input, strictly.\n"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": translation_prompt},
                {"role": "user", "content": f"{numbered_list}"}
            ]
        )
        translated_text = response.choices[0].message.content.strip()
        # Parse the translated numbered list
        import re
        translated_lines = re.findall(r"^\d+\.\s*(.+)$", translated_text, re.MULTILINE)
        # Fallback if parsing fails
        if len(translated_lines) != len(all_ingredients_en):
            translated_lines = [translated_text] * len(all_ingredients_en)
    except Exception as e:
        print(f"Batch translation error: {e}")
        translated_lines = all_ingredients_en

    # Build days_output using the batch translations
    days_output = []
    translation_idx = 0
    for day_idx, day_meals in enumerate(days_schedule):
        date = (today + timedelta(days=day_idx)).strftime("%Y-%m-%d")
        meals_output = []
        for meal_type, time, recipe in day_meals:
            ingredients_en = recipe["ingredients"]
            ingredients_es = translated_lines[translation_idx]
            translation_idx += 1
            meals_output.append({
                "meal_type": meal_type,
                "recipe_uid": recipe["unique_id"],
                "eating_time": time,
                "grams": 250,
                "ingredients_en": ingredients_en,
                "ingredients_es": ingredients_es
            })
        days_output.append({"date": date, "meals": meals_output})

    return {
        "user": plan_user,
        "tags": [
            user_data["fitness_goal"],
            *user_data.get("dietary_preferences", []),
            *user_data.get("allergies", [])
        ],
        "days": days_output
    }

# === Run Function ===
def run_meal_plan(user_data, recipes, flag=False):
    if flag:
        index_dir = "index"
        if os.path.exists(index_dir):
            for filename in os.listdir(index_dir):
                file_path = os.path.join(index_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(index_dir)
            print(f"Index folder '{index_dir}' deleted successfully.")
            flag = False

    if not recipes:
        return {"error": "No recipes found."}

    embeddings, index = embed_recipe_descriptions(recipes)
    meal_plan = generate_meal_plan(user_data, recipes, embeddings, index)
    return meal_plan

# === Example Usage ===
if __name__ == "__main__":
    user_profile = {
        "fullname": "John Doe",
        "gender": "Male",
        "date_of_birth": "1990-05-15",
        "weight": 75,
        "height": 178,
        "dietary_preferences": ["Vegetarian"],
        "medical_conditions": ["None"],
        "allergies": ["Gluten"],
        "fitness_goal": "Muscle Gain",
        "lifestyle_habits": ["Active"]
    }

    plan = run_meal_plan(user_profile, RECIPES, flag=False) # If flag true, delete index folder
    print(json.dumps(plan, indent=2))