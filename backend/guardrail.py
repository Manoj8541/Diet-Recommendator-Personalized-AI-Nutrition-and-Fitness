"""
Lightweight keyword-based guardrail filter for diet-related queries.
Fast, deterministic pure-Python filtering without ML dependencies (<5ms).

Intelligently blocks:
- Food ordering / restaurant / takeout banter (e.g. "i'm hungry order burger", "order pizza")
- Unrelated queries (weather, coding, poems, jokes, movies, games)
While allowing:
- Genuine dietary, macronutrient, health, and fitness planning requests.
"""

import re

# Blacklisted intent patterns (food delivery, restaurant ordering, conversational chit-chat, coding, general off-topic)
BLACKLIST_PATTERNS = [
    r"\border\b",
    r"\bbuy\b",
    r"\bdeliver(y)?\b",
    r"\brestaurant\b",
    r"\bmenu\b",
    r"\bburger\b",
    r"\bpizza\b",
    r"\bzomato\b",
    r"\bswiggy\b",
    r"\buber\b",
    r"\bdoordash\b",
    r"\bweather\b",
    r"\bpoem\b",
    r"\bjoke\b",
    r"\bcode\b",
    r"\bpython\b",
    r"\bjavascript\b",
    r"\bmovie\b",
    r"\bsong\b",
    r"\bsing\b",
    r"\bgame\b",
    r"\btranslate\b",
    r"\bwrite a (story|essay|email|letter)\b",
    r"\bwho is\b",
    r"\bwho was\b",
    r"\btell me a (story|joke|riddle)\b",
]

# Genuine nutrition, dietary, fitness, health planning keywords
DIET_KEYWORDS = [
    "diet", "meal", "meals", "food", "foods", "calorie", "calories", "kcal",
    "protein", "carb", "carbs", "carbohydrate", "carbohydrates", "fat", "fats",
    "lipid", "macros", "macro", "micronutrient", "micronutrients", "nutrition",
    "nutrient", "nutrients", "nutritious", "veg", "vegetarian", "vegan", "plant-based",
    "non-veg", "non-vegetarian", "breakfast", "lunch", "dinner", "snack", "snacks",
    "allergy", "allergies", "allergic", "fiber", "fibre", "vitamin", "vitamins",
    "mineral", "minerals", "hydration", "water intake", "exercise", "workout",
    "gym", "training", "cardio", "lifting", "hypertrophy", "strength", "bmi",
    "bmr", "tdee", "obesity", "health", "healthy", "portion", "serving",
    "lose weight", "weight loss", "fat loss", "gain weight", "weight gain",
    "muscle gain", "muscle building", "maintenance", "lean", "bulk", "cut",
    "sugar", "sodium", "salt", "cholesterol", "gluten", "lactose", "dairy",
    "keto", "ketogenic", "paleo", "intermittent fasting", "fasting",
    "low carb", "high protein", "low fat", "glycemic", "digest", "digestion",
    "metabolism", "appetite", "satiety"
]


def is_diet_related(text: str) -> bool:
    """
    Check if the given text is a genuine diet/nutrition-related query.
    
    Args:
        text: Input string to validate
        
    Returns:
        True if valid diet request, False if off-topic or food ordering
    """
    if not text:
        return True  # Empty/unspecified free_text is valid
        
    text_clean = text.strip().lower()
    if not text_clean:
        return True
        
    # Check blacklisted patterns (food ordering, weather, jokes, code, etc.)
    for pattern in BLACKLIST_PATTERNS:
        if re.search(pattern, text_clean):
            return False
            
    # Check if at least one dietary/fitness keyword matches
    for keyword in DIET_KEYWORDS:
        if keyword in text_clean:
            return True
            
    # If no dietary keyword was found in the text, reject
    return False
