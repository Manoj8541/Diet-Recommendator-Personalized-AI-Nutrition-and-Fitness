"""
Rich food database for vegetarian and non-vegetarian diets with allergen filtering.
Categorized into breakfast, lunch, dinner, and snacks.
"""

VEG_MEALS = {
    "breakfast": [
        "Rolled oats with chia seeds, almond milk, and mixed berries",
        "Moong dal chilla with mint chutney and grated paneer",
        "Greek yogurt bowl with sliced bananas, walnuts, and honey",
        "Sprouted green gram salad with pomegranate and lemon dressing",
        "Whole grain avocado toast with hemp seeds and cherry tomatoes",
        "Tofu vegetable scramble with spinach and whole wheat sourdough",
        "Besan (gram flour) vegetable pancake with curd",
        "Quinoa porridge with flaxseeds, apple slices, and cinnamon",
        "Paneer and spinach stuffed whole wheat paratha with low-fat curd",
        "High-protein smoothie (soy milk, spinach, peanut butter, banana)"
    ],
    "lunch": [
        "Paneer tikka masala with 2 whole wheat rotis and cucumber salad",
        "Yellow dal tadka with brown basmati rice and steamed French beans",
        "Chickpea (chana) curry with quinoa and mixed vegetable kachumber",
        "Palak paneer with whole wheat roti and roasted flaxseed raita",
        "Rajma (kidney bean) curry with brown rice and beet salad",
        "Tofu and mixed vegetable stir-fry with edamame and brown rice",
        "Lentil and vegetable khichdi with roasted papad and curd",
        "Soya chunk curry with whole wheat rotis and green salad",
        "Mediterranean quinoa bowl with roasted chickpeas, olives, and feta",
        "Mixed dal (Panchmel) with multigrain roti and sautéed spinach"
    ],
    "dinner": [
        "Grilled tofu steak with sautéed broccoli, mushrooms, and bell peppers",
        "Lentil vegetable soup with a warm whole wheat dinner roll",
        "Methi paneer bhurji with 2 multigrain rotis and clear veg soup",
        "Stuffed bell peppers with spiced quinoa, black beans, and corn",
        "Cottage cheese and grilled zucchini salad with lemon-herb dressing",
        "Mushroom and green pea curry with whole wheat phulkas",
        "Steamed moong dal idlis with vegetable sambar and coconut-mint chutney",
        "Cauliflower and paneer bhurji with warm cucumber-mint raita",
        "Roasted pumpkin and lentil soup with toasted pumpkin seeds",
        "Stir-fried asparagus, baby corn, and tofu in sesame-ginger glaze"
    ],
    "snacks": [
        "Roasted spiced makhana (fox nuts)",
        "Boiled chana (chickpea) chaat with onions and lemon",
        "Mixed raw nuts (almonds, walnuts) and pumpkin seeds",
        "Cucumber and carrot crudités with roasted garlic hummus",
        "Low-fat cottage cheese cubes sprinkled with chaat masala",
        "Apple slices with 1 tbsp natural peanut butter",
        "Roasted soybeans or edamame pods with sea salt",
        "Chia seed pudding made with almond milk and raspberries"
    ]
}

NON_VEG_MEALS = {
    "breakfast": [
        "3 Egg-white and 1 whole egg vegetable omelette with whole grain toast",
        "Scrambled eggs with sautéed baby spinach, mushrooms, and avocado",
        "Smoked salmon with poached eggs on whole wheat sourdough",
        "Boiled eggs (2 whole) with steel-cut oats and blueberries",
        "Grilled chicken sausage with sautéed bell peppers and rye toast",
        "Egg bhurji (spiced scrambled eggs) with multigrain roti",
        "Greek yogurt parfait with whey isolate, sliced strawberries, and almonds",
        "Turkey breast slices with avocado and sunny-side-up egg on sourdough",
        "Shakshuka (poached eggs in spiced tomato-bell pepper sauce) with pita",
        "Egg white and cottage cheese frittata with herbs"
    ],
    "lunch": [
        "Grilled chicken breast with herb roasted sweet potato and steamed broccoli",
        "Fish curry (Rohu or Pomfret) with brown basmati rice and cucumber salad",
        "Tandoori chicken breast with 2 whole wheat rotis and mint raita",
        "Tuna and avocado whole grain wrap with mixed greens salad",
        "Grilled salmon fillet with quinoa and lemon-garlic asparagus",
        "Chicken keema (minced chicken) with multigrain phulkas and kachumber",
        "Grilled prawn salad with olive oil, baby spinach, and cherry tomatoes",
        "Chicken biryani prepared with brown rice and low-fat cucumber raita",
        "Baked cod or tilapia with sautéed zucchini, bell peppers, and wild rice",
        "Turkey and quinoa power bowl with roasted sweet potato and tahini"
    ],
    "dinner": [
        "Pan-seared salmon with garlic sautéed green beans and cauliflower mash",
        "Herb-marinated grilled chicken breast with roasted asparagus and clear soup",
        "Steamed fish with ginger, scallions, soy glaze, and bok choy",
        "Clear chicken and vegetable broth with shredded chicken breast",
        "Grilled fish tikka with bell pepper skewers and mint chutney",
        "Egg white curry with 2 whole wheat phulkas and green salad",
        "Roasted chicken thigh (skinless) with sautéed mushrooms and spinach",
        "Baked lemon-herb tilapia with sautéed bell peppers and broccoli",
        "Grilled turkey cutlets with roasted carrots and fresh garden salad",
        "Shrimp stir-fry with snow peas, broccoli, and garlic sesame sauce"
    ],
    "snacks": [
        "2 Hard-boiled egg whites with black pepper",
        "Grilled chicken strips with mustard dip",
        "Greek yogurt with walnuts and cinnamon",
        "Canned tuna salad with diced celery and lemon",
        "Mixed roasted nuts (almonds, walnuts, pistachios)",
        "Jerky (lean turkey or chicken breast strips)",
        "Sprouted moong salad with boiled egg whites",
        "Cottage cheese cubes with cherry tomatoes"
    ]
}


def get_food_list(diet_type: str) -> dict:
    """
    Get categorized meals dictionary based on diet type.
    """
    if diet_type.lower() == "non-veg":
        return NON_VEG_MEALS
    else:
        return VEG_MEALS


def get_flattened_food_list(diet_type: str) -> list[str]:
    """
    Get a flattened list of all food items for the diet type.
    """
    meals_dict = get_food_list(diet_type)
    all_foods = []
    for category in ["breakfast", "lunch", "dinner", "snacks"]:
        all_foods.extend(meals_dict.get(category, []))
    return all_foods


# Allergen mapping keywords
ALLERGEN_MAP = {
    "dairy": ["milk", "paneer", "curd", "yogurt", "cheese", "feta", "butter", "raita", "cottage cheese"],
    "milk": ["milk", "paneer", "curd", "yogurt", "cheese", "feta", "butter", "raita", "cottage cheese"],
    "lactose": ["milk", "paneer", "curd", "yogurt", "cheese", "feta", "butter", "raita", "cottage cheese"],
    "nut": ["nut", "nuts", "almond", "almonds", "walnut", "walnuts", "peanut", "peanuts", "cashew", "cashews", "pistachio"],
    "nuts": ["nut", "nuts", "almond", "almonds", "walnut", "walnuts", "peanut", "peanuts", "cashew", "cashews", "pistachio"],
    "peanut": ["peanut", "peanuts"],
    "egg": ["egg", "eggs", "omelette", "frittata", "bhurji", "shakshuka", "poached egg"],
    "eggs": ["egg", "eggs", "omelette", "frittata", "bhurji", "shakshuka", "poached egg"],
    "gluten": ["wheat", "roti", "rotis", "phulka", "phulkas", "paratha", "toast", "bread", "pita", "sourdough", "pasta"],
    "wheat": ["wheat", "roti", "rotis", "phulka", "phulkas", "paratha", "toast", "bread", "pita", "sourdough"],
    "fish": ["fish", "salmon", "tuna", "cod", "tilapia", "pomfret", "rohu", "prawn", "prawns", "shrimp"],
    "seafood": ["fish", "salmon", "tuna", "cod", "tilapia", "pomfret", "rohu", "prawn", "prawns", "shrimp"],
    "shellfish": ["prawn", "prawns", "shrimp", "crab", "lobster"],
    "soy": ["soy", "soya", "tofu", "edamame"],
    "soya": ["soy", "soya", "tofu", "edamame"],
    "tofu": ["tofu"]
}


def filter_candidate_foods_by_allergens(foods_dict: dict, allergies_text: str | None) -> dict:
    """
    Remove candidate foods containing any specified allergens.
    
    Args:
        foods_dict: Dictionary of category -> list of foods
        allergies_text: Comma or space separated user allergens string
        
    Returns:
        Filtered dictionary of category -> list of foods
    """
    if not allergies_text or not allergies_text.strip():
        return foods_dict
        
    allergies_lower = allergies_text.lower()
    trigger_words = []
    
    for allergen_key, keywords in ALLERGEN_MAP.items():
        if allergen_key in allergies_lower:
            trigger_words.extend(keywords)
            
    # Also split user text directly for custom allergen keywords
    for word in allergies_lower.replace(",", " ").split():
        if len(word) > 2:
            trigger_words.append(word)
            
    trigger_words = list(set(trigger_words))
    
    filtered = {}
    for category, items in foods_dict.items():
        clean_items = []
        for item in items:
            item_lower = item.lower()
            if not any(trigger in item_lower for trigger in trigger_words):
                clean_items.append(item)
        # Ensure at least some items remain (if overly filtered, keep safe fallback)
        filtered[category] = clean_items if clean_items else items
        
    return filtered
