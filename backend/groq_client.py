"""
Groq API client for dynamic, personalized diet, macronutrient, and fitness plan generation.
High-reliability architecture with dynamic environment key loading and clinical fallback synthesis.
"""

import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# Built-in clinical recipes bank for fallback synthesis
FALLBACK_RECIPES = {
    "veg": {
        "breakfast": [
            {"name": "Moong Dal Chilla with Mint Chutney & Grated Paneer", "portion": "2 medium chillas (150g) + 30g paneer", "benefit": "High bioavailability plant protein, low glycemic index, rich in fiber", "alt": "Rolled Oats Bowl with Chia Seeds, Almond Milk & Berries"},
            {"name": "Greek Yogurt Parfait with Walnuts & Sliced Banana", "portion": "200g Greek yogurt + 25g nuts", "benefit": "Probiotic gut support, healthy omega fats, steady morning energy", "alt": "Whole Grain Avocado Toast with Hemp Seeds & Cherry Tomatoes"},
            {"name": "Tofu & Spinach Scramble with Sourdough Toast", "portion": "160g firm tofu + 1 slice sourdough", "benefit": "Complete soy amino acids, iron and antioxidant support", "alt": "Sprouted Moong Salad with Pomegranate & Lemon Dressing"}
        ],
        "lunch": [
            {"name": "Paneer Tikka Masala with 2 Whole Wheat Rotis & Salad", "portion": "150g paneer + 2 rotis + cucumber bowl", "benefit": "Sustained casein protein delivery, complex whole grain carbohydrates", "alt": "Yellow Dal Tadka with Brown Basmati Rice & Steamed Beans"},
            {"name": "Chickpea (Chana) Curry with Quinoa & Vegetable Salad", "portion": "1.5 cups chana + 1 cup cooked quinoa", "benefit": "High soluble fiber for lipid regulation and satiety", "alt": "Palak Paneer with Multigrain Phulkas & Roasted Flaxseed Raita"},
            {"name": "Rajma (Kidney Bean) Curry with Brown Rice & Kachumber", "portion": "1.5 cups rajma + 1 cup brown rice", "benefit": "Rich in potassium, magnesium, and resistant starch", "alt": "Tofu & Mixed Vegetable Stir-Fry with Edamame & Quinoa"}
        ],
        "dinner": [
            {"name": "Grilled Tofu Steak with Sautéed Broccoli & Mushrooms", "portion": "160g tofu + 1.5 cups vegetables", "benefit": "Low carb, high protein evening meal promoting muscle repair during sleep", "alt": "Lentil Vegetable Soup with a Warm Whole Grain Roll"},
            {"name": "Methi Paneer Bhurji with 2 Multigrain Rotis & Soup", "portion": "150g paneer bhurji + 2 rotis", "benefit": "Fenugreek supports glucose metabolism; rich in calcium and magnesium", "alt": "Stuffed Bell Peppers with Spiced Quinoa & Black Beans"},
            {"name": "Cottage Cheese & Grilled Zucchini Salad with Herbs", "portion": "180g low-fat cottage cheese + veggies", "benefit": "Slow-digesting protein preventing overnight muscle catabolism", "alt": "Mushroom & Green Pea Curry with Whole Wheat Phulkas"}
        ],
        "snacks": [
            {"name": "Roasted Spiced Makhana (Fox Nuts) & Mixed Raw Almonds", "portion": "30g makhana + 15g almonds", "benefit": "Rich in magnesium and antioxidants, crunch without refined oils", "alt": "Boiled Chana Chaat with Diced Onions & Tomatoes"},
            {"name": "Low-Fat Cottage Cheese Cubes with Chaat Masala", "portion": "150g paneer cubes", "benefit": "Fast protein boost keeping blood sugar and appetite balanced", "alt": "Apple Slices with 1 tbsp Natural Peanut Butter"}
        ]
    },
    "non-veg": {
        "breakfast": [
            {"name": "3 Egg-White & 1 Whole Egg Vegetable Omelette with Sourdough", "portion": "4 eggs total + 1 slice toast + spinach", "benefit": "High leucine concentration for muscle protein synthesis and choline", "alt": "Scrambled Eggs with Sautéed Spinach, Mushrooms & Avocado"},
            {"name": "Smoked Salmon & Poached Eggs on Whole Wheat Toast", "portion": "60g salmon + 2 eggs + 1 toast", "benefit": "Rich in anti-inflammatory Omega-3 EPA/DHA fatty acids and Vitamin D", "alt": "Turkey Breast Slices with Avocado & Sunny-Side-Up Egg"},
            {"name": "Spiced Egg Bhurji with Multigrain Roti", "portion": "3 eggs + 1 multigrain roti", "benefit": "Balanced morning thermogenesis with healthy lipids and complex carbs", "alt": "Greek Yogurt Parfait with Whey Protein & Berries"}
        ],
        "lunch": [
            {"name": "Herb Grilled Chicken Breast with Sweet Potato & Broccoli", "portion": "180g chicken breast + 120g sweet potato", "benefit": "Ultra-lean high biological value protein with potassium and beta-carotene", "alt": "Fish Curry with Brown Basmati Rice & Cucumber Salad"},
            {"name": "Tandoori Chicken Breast with 2 Whole Wheat Rotis & Raita", "portion": "180g tandoori chicken + 2 rotis", "benefit": "Lean protein with anti-inflammatory spices and probiotic raita", "alt": "Tuna & Avocado Whole Grain Wrap with Mixed Greens Salad"},
            {"name": "Pan-Seared Salmon Fillet with Quinoa & Garlic Asparagus", "portion": "160g salmon + 1 cup quinoa", "benefit": "Cardiovascular health, joint recovery, and cellular membrane support", "alt": "Chicken Keema with Multigrain Phulkas & Kachumber Salad"}
        ],
        "dinner": [
            {"name": "Pan-Seared White Fish Fillet with Sautéed Green Beans", "portion": "200g fish fillet + 1.5 cups green beans", "benefit": "Ultra-lean, easily digestible evening protein ensuring restorative sleep", "alt": "Herb Marinated Grilled Chicken Breast with Clear Vegetable Broth"},
            {"name": "Steamed Fish with Ginger, Scallions & Bok Choy", "portion": "200g fish + 1.5 cups steamed greens", "benefit": "Low sodium, light on digestion, optimal overnight recovery", "alt": "Egg White Curry (4 whites) with 2 Whole Wheat Phulkas"},
            {"name": "Grilled Turkey Cutlets with Roasted Carrots & Fresh Salad", "portion": "180g turkey + roasted vegetables", "benefit": "Rich in tryptophan for serotonin and deep sleep regulation", "alt": "Shrimp Stir-Fry with Snow Peas, Broccoli & Sesame Glaze"}
        ],
        "snacks": [
            {"name": "2 Hard-Boiled Eggs with Black Pepper & Pink Salt", "portion": "2 whole eggs", "benefit": "Quick bioavailable protein, lutein, zeaxanthin, and healthy lipids", "alt": "Grilled Chicken Breast Strips with Mustard Dip (100g)"},
            {"name": "Canned Tuna Salad with Diced Celery & Olive Oil", "portion": "100g tuna + celery", "benefit": "Pure lean protein snack with zero refined sugars or starch", "alt": "Greek Yogurt Bowl with Crushed Walnuts"}
        ]
    }
}


def get_groq_client() -> Groq | None:
    """
    Dynamically retrieve and validate Groq API client from environment.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


def extract_and_clean_json(raw_text: str) -> dict:
    """
    Robust JSON extraction and sanitization from LLM output text.
    """
    if not raw_text:
        raise ValueError("Empty response received from LLM.")
        
    text = raw_text.strip()
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    
    try:
        return json.loads(text)
    except Exception:
        pass
        
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if code_block_match:
        extracted = code_block_match.group(1).strip()
        try:
            return json.loads(extracted)
        except Exception:
            text = extracted
            
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace:last_brace + 1].strip()
        clean_candidate = re.sub(r",\s*([\]\}])", r"\1", candidate)
        try:
            return json.loads(clean_candidate)
        except Exception:
            pass
            
    raise ValueError("Could not extract valid JSON structure from LLM output.")


def _normalize_meal_item(meal_data, default_name="Nutritious Meal") -> dict:
    if isinstance(meal_data, dict):
        return {
            "name": str(meal_data.get("name") or meal_data.get("dish") or default_name),
            "portion": str(meal_data.get("portion") or "1 standard serving"),
            "calories": int(meal_data.get("calories") or 400),
            "protein_g": int(meal_data.get("protein_g") or meal_data.get("protein") or 25),
            "key_nutrients": str(meal_data.get("key_nutrients") or meal_data.get("nutrients") or "High protein, essential vitamins"),
            "alternative": str(meal_data.get("alternative") or "Alternative healthy option")
        }
    elif isinstance(meal_data, str):
        parts = meal_data.split(" OR ")
        main_dish = parts[0].strip() if parts else default_name
        alt_dish = parts[1].strip() if len(parts) > 1 else "Healthy fruit or yogurt bowl"
        return {
            "name": main_dish,
            "portion": "1 balanced serving",
            "calories": 400,
            "protein_g": 25,
            "key_nutrients": "High fiber and balanced macronutrients",
            "alternative": alt_dish
        }
    else:
        return {
            "name": default_name,
            "portion": "1 serving",
            "calories": 400,
            "protein_g": 25,
            "key_nutrients": "Balanced macronutrients and energy",
            "alternative": "Healthy fruit and seed bowl"
        }


def _validate_and_sanitize_result(result: dict, user_metrics: dict) -> dict:
    meal_slots = ["breakfast", "lunch", "dinner", "snacks"]
    
    if "weekday_plan" not in result or not isinstance(result["weekday_plan"], dict):
        result["weekday_plan"] = {}
    for slot in meal_slots:
        result["weekday_plan"][slot] = _normalize_meal_item(result["weekday_plan"].get(slot), f"Weekday {slot.capitalize()}")
        
    if "weekend_plan" not in result or not isinstance(result["weekend_plan"], dict):
        result["weekend_plan"] = {}
    for slot in meal_slots:
        result["weekend_plan"][slot] = _normalize_meal_item(result["weekend_plan"].get(slot), f"Weekend {slot.capitalize()}")
        
    if "exercise_plan" not in result or not isinstance(result["exercise_plan"], dict):
        result["exercise_plan"] = {
            "workout_type": "Functional Resistance & Mobility Routine",
            "weekly_frequency": "4 sessions / week",
            "strength_focus": [
                "Compound Movements: Squats & Push-ups (3x10-12)",
                "Pull & Core: Dumbbell Rows & Planks (3x45s)"
            ],
            "cardio_focus": [
                "Zone 2 Incline Walking or Cycling (30 mins, 3x/week)",
                "Daily 8,000-10,000 Step Goal"
            ],
            "recovery_tips": "Ensure 7-8 hours quality sleep, daily hydration, and post-workout stretching."
        }
        
    if "key_nutrients" not in result or not isinstance(result["key_nutrients"], list) or len(result["key_nutrients"]) == 0:
        result["key_nutrients"] = [
            {
                "nutrient": "Complete Protein & Amino Acids",
                "benefit": "Crucial for muscle repair, maintaining metabolic rate, and satiety.",
                "recommended_foods": ["Tofu / Paneer", "Greek Yogurt / Eggs", "Lentils / Chicken Breast"]
            },
            {
                "nutrient": "Dietary Fiber & Complex Carbohydrates",
                "benefit": "Optimizes gut microbiome health and stabilizes postprandial glucose.",
                "recommended_foods": ["Oats", "Chia seeds", "Quinoa", "Vegetables"]
            },
            {
                "nutrient": "Hydration & Essential Electrolytes (Magnesium, Potassium)",
                "benefit": "Supports cellular energy, neuromuscular recovery, and metabolic rate.",
                "recommended_foods": ["Water", "Spinach", "Pumpkin seeds", "Almonds"]
            }
        ]
        
    if "notes" not in result or not result["notes"]:
        result["notes"] = f"Maintain consistent meal timing and aim for at least {user_metrics.get('water_intake_liters', 2.5)}L of water daily. Consistency is the key to achieving your health goal."
        
    return result


def _synthesize_clinical_plan(
    user_metrics: dict,
    diet_type: str,
    activity_level: str,
    goal: str,
    candidate_foods: dict,
    allergies: str = None,
    free_text: str = None
) -> dict:
    """
    Robust fallback synthesis engine producing custom personalized plans.
    """
    dt = "non-veg" if diet_type.lower() == "non-veg" else "veg"
    bank = FALLBACK_RECIPES[dt]
    cal = user_metrics.get("calorie_target", 2000)
    pro = user_metrics.get("protein_target_g", 120)

    # Filter out allergens
    allergens_list = [a.strip().lower() for a in (allergies or "").split(",") if a.strip()]
    
    def filter_and_pick(meal_list, index=0):
        safe = [m for m in meal_list if not any(al in m["name"].lower() for al in allergens_list)]
        items = safe if safe else meal_list
        return items[index % len(items)]

    b1, l1, d1, s1 = filter_and_pick(bank["breakfast"], 0), filter_and_pick(bank["lunch"], 0), filter_and_pick(bank["dinner"], 0), filter_and_pick(bank["snacks"], 0)
    b2, l2, d2, s2 = filter_and_pick(bank["breakfast"], 1), filter_and_pick(bank["lunch"], 1), filter_and_pick(bank["dinner"], 1), filter_and_pick(bank["snacks"], 1)

    weekday = {
        "breakfast": {"name": b1["name"], "portion": b1["portion"], "calories": int(round(cal * 0.25)), "protein_g": int(round(pro * 0.25)), "key_nutrients": b1["benefit"], "alternative": b1["alt"]},
        "lunch": {"name": l1["name"], "portion": l1["portion"], "calories": int(round(cal * 0.35)), "protein_g": int(round(pro * 0.35)), "key_nutrients": l1["benefit"], "alternative": l1["alt"]},
        "dinner": {"name": d1["name"], "portion": d1["portion"], "calories": int(round(cal * 0.25)), "protein_g": int(round(pro * 0.25)), "key_nutrients": d1["benefit"], "alternative": d1["alt"]},
        "snacks": {"name": s1["name"], "portion": s1["portion"], "calories": int(round(cal * 0.15)), "protein_g": int(round(pro * 0.15)), "key_nutrients": s1["benefit"], "alternative": s1["alt"]}
    }

    weekend = {
        "breakfast": {"name": b2["name"], "portion": b2["portion"], "calories": int(round(cal * 0.25)), "protein_g": int(round(pro * 0.25)), "key_nutrients": b2["benefit"], "alternative": b2["alt"]},
        "lunch": {"name": l2["name"], "portion": l2["portion"], "calories": int(round(cal * 0.35)), "protein_g": int(round(pro * 0.35)), "key_nutrients": l2["benefit"], "alternative": l2["alt"]},
        "dinner": {"name": d2["name"], "portion": d2["portion"], "calories": int(round(cal * 0.25)), "protein_g": int(round(pro * 0.25)), "key_nutrients": d2["benefit"], "alternative": d2["alt"]},
        "snacks": {"name": s2["name"], "portion": s2["portion"], "calories": int(round(cal * 0.15)), "protein_g": int(round(pro * 0.15)), "key_nutrients": s2["benefit"], "alternative": s2["alt"]}
    }

    workout_name = "Progressive Resistance & Lean Hypertrophy" if goal == "gain" else "Metabolic Conditioning & Fat Loss" if goal == "lose" else "Functional Health & Strength"
    freq = "5-6 days/week" if activity_level == "active" else "4 days/week" if activity_level == "moderate" else "3 days/week"

    exercise = {
        "workout_type": workout_name,
        "weekly_frequency": freq,
        "strength_focus": [
            "Compound Movements: Squats, Push-ups & Dumbbell Rows (3-4 sets of 8-12 reps)",
            "Core Stabilization: Planks & Romanian Deadlifts (3 sets of 45s / 10 reps)"
        ],
        "cardio_focus": [
            "Zone 2 Incline Walking or Stationary Cycling (25-30 mins, 3x/week)",
            "Daily Movement: Aim for 8,000-10,000 daily steps"
        ],
        "recovery_tips": "Ensure 7.5-8 hours of sleep, hydrate upon waking, and maintain active stretching."
    }

    nutrients = [
        {"nutrient": "Complete High Biological Value Protein", "benefit": "Preserves lean mass, optimizes recovery and increases satiety.", "recommended_foods": ["Paneer / Tofu" if dt == "veg" else "Chicken Breast / Eggs", "Greek Yogurt", "Lentils"]},
        {"nutrient": "Dietary Soluble & Insoluble Fiber", "benefit": "Stabilizes postprandial blood glucose and supports microbiome diversity.", "recommended_foods": ["Rolled Oats", "Chia seeds", "Broccoli", "Quinoa"]},
        {"nutrient": "Essential Electrolytes (Magnesium & Potassium)", "benefit": "Prevents muscular fatigue, aids cellular hydration and promotes restorative sleep.", "recommended_foods": ["Pumpkin seeds", "Spinach", "Almonds", "Avocado"]}
    ]

    custom_text = f" User note: {free_text}." if free_text else ""
    notes = f"Eat balanced meals spaced 3.5-4 hours apart. Drink at least {user_metrics.get('water_intake_liters', 2.5)}L of water daily.{custom_text} Consistency in caloric balance will deliver sustainable results."

    return {
        "weekday_plan": weekday,
        "weekend_plan": weekend,
        "exercise_plan": exercise,
        "key_nutrients": nutrients,
        "notes": notes
    }


def generate_diet_plan(
    user_metrics: dict,
    diet_type: str,
    activity_level: str,
    goal: str,
    candidate_foods: dict,
    allergies: str = None,
    free_text: str = None
) -> dict:
    """
    Generate a personalized diet and workout plan using Groq API with robust fallback synthesis.
    """
    client = get_groq_client()
    
    if client is not None:
        food_summary = []
        for cat, items in candidate_foods.items():
            food_summary.append(f"{cat}: {', '.join(items[:4])}")
        foods_formatted = " | ".join(food_summary)
        
        prompt = f"""You are a professional clinical dietitian. Generate a personalized nutrition and workout JSON for this user:
User Profile:
- Daily Calorie Target: {user_metrics['calorie_target']} kcal (BMR: {user_metrics['bmr']} kcal, TDEE: {user_metrics['tdee']} kcal)
- Daily Protein Target: {user_metrics['protein_target_g']}g
- Body Profile: BMI {user_metrics['bmi']} ({user_metrics['bmi_category']}), Daily Water: {user_metrics['water_intake_liters']}L
- Diet Type: {diet_type.upper()}, Activity: {activity_level.upper()}, Goal: {goal.upper()}
"""

        if allergies and allergies.strip():
            prompt += f"- Strict Food Exclusions: {allergies}\n"
            
        if free_text and free_text.strip():
            prompt += f"- User Specific Custom Request: \"{free_text}\" (Incorporate this request directly into meals, exercise, and advice!)\n"
            
        prompt += f"""Allowed Candidate Foods: {foods_formatted}

Return ONLY valid JSON matching this schema:
{{
  "weekday_plan": {{
    "breakfast": {{"name": "dish name", "portion": "specific portion", "calories": 400, "protein_g": 25, "key_nutrients": "benefit", "alternative": "option B"}},
    "lunch": {{"name": "dish name", "portion": "specific portion", "calories": 600, "protein_g": 35, "key_nutrients": "benefit", "alternative": "option B"}},
    "dinner": {{"name": "dish name", "portion": "specific portion", "calories": 500, "protein_g": 30, "key_nutrients": "benefit", "alternative": "option B"}},
    "snacks": {{"name": "dish name", "portion": "specific portion", "calories": 250, "protein_g": 12, "key_nutrients": "benefit", "alternative": "option B"}}
  }},
  "weekend_plan": {{
    "breakfast": {{"name": "dish name", "portion": "specific portion", "calories": 400, "protein_g": 25, "key_nutrients": "benefit", "alternative": "option B"}},
    "lunch": {{"name": "dish name", "portion": "specific portion", "calories": 600, "protein_g": 35, "key_nutrients": "benefit", "alternative": "option B"}},
    "dinner": {{"name": "dish name", "portion": "specific portion", "calories": 500, "protein_g": 30, "key_nutrients": "benefit", "alternative": "option B"}},
    "snacks": {{"name": "dish name", "portion": "specific portion", "calories": 250, "protein_g": 12, "key_nutrients": "benefit", "alternative": "option B"}}
  }},
  "exercise_plan": {{
    "workout_type": "Specific training routine tailored to goal, activity, and profile",
    "weekly_frequency": "e.g. 4 days/week",
    "strength_focus": ["Exercise 1 (sets x reps)", "Exercise 2 (sets x reps)", "Core/Mobility movement"],
    "cardio_focus": ["Cardio activity (duration)", "Daily step goal"],
    "recovery_tips": "Sleep & hydration guidance"
  }},
  "key_nutrients": [
    {{"nutrient": "Nutrient Name", "benefit": "Key health advantage for this user profile", "recommended_foods": ["Food 1", "Food 2"]}}
  ],
  "notes": "Actionable meal timing, hydration, and adherence guidance tailored for this user."
}}"""

        model_candidates = ["openai/gpt-oss-20b", "qwen/qwen3.6-27b", "openai/gpt-oss-120b"]

        for model_name in model_candidates:
            try:
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a clinical dietitian assistant. Output ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=2500
                )
                content = resp.choices[0].message.content
                result = extract_and_clean_json(content)
                return _validate_and_sanitize_result(result, user_metrics)
            except Exception:
                continue

    # Graceful fallback synthesis if API key is invalid or rate limited
    fallback_result = _synthesize_clinical_plan(
        user_metrics=user_metrics,
        diet_type=diet_type,
        activity_level=activity_level,
        goal=goal,
        candidate_foods=candidate_foods,
        allergies=allergies,
        free_text=free_text
    )
    return _validate_and_sanitize_result(fallback_result, user_metrics)
