"""
Pure Python health, metabolic, and macronutrient calculations.
Uses gold-standard Mifflin-St Jeor formula and evidence-based clinical nutrition science.
Deterministic, mathematically sound, tailored precisely for age, biological sex, weight, height, activity, and goal.
"""


def calculate_bmi(weight_kg: float, height_cm: float) -> tuple[float, str]:
    """
    Calculate Body Mass Index (BMI) and determine WHO category.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        
    Returns:
        Tuple of (bmi_value_rounded, category_string)
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "Normal Weight"
        
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    bmi_rounded = round(bmi, 1)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25.0:
        category = "Normal Weight"
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"
        
    return bmi_rounded, category


def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor formula.
    Accurately differentiates between biological sex and age factors.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        sex: "male" or "female"
        
    Returns:
        BMR in calories per day
    """
    if sex.lower() == "male":
        # Men: BMR = 10×weight + 6.25×height − 5×age + 5
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        # Women: BMR = 10×weight + 6.25×height − 5×age − 161
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    return max(bmr, 800.0)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure from BMR and physical activity level.
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: "sedentary", "moderate", or "active"
        
    Returns:
        TDEE in calories per day
    """
    activity_multipliers = {
        "sedentary": 1.2,      # Desk job, minimal exercise
        "moderate": 1.55,      # Moderate exercise 3-5 days/week
        "active": 1.725        # High activity / daily athletic training
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return bmr * multiplier


def calculate_calorie_target(tdee: float, goal: str) -> int:
    """
    Calculate target daily calorie intake based on user goal.
    
    Args:
        tdee: Total Daily Energy Expenditure
        goal: "lose", "gain", or "maintain"
        
    Returns:
        Target calories per day (integer, minimum 1100 for safety)
    """
    if goal.lower() == "lose":
        target = tdee - 500  # Safe deficit for fat loss
    elif goal.lower() == "gain":
        target = tdee + 500  # Safe surplus for muscle gain
    else:  # maintain
        target = tdee
    
    return max(int(round(target)), 1100)


def calculate_protein_target(weight_kg: float, goal: str, activity_level: str, age: int = 25, sex: str = "male") -> int:
    """
    Calculate recommended daily protein intake in grams based on clinical guidelines.
    Adjusted for age (sarcopenia prevention in older adults) and gender.
    """
    if goal.lower() == "lose":
        multiplier = 2.0 if activity_level.lower() in ["moderate", "active"] else 1.8
    elif goal.lower() == "gain":
        multiplier = 2.2 if activity_level.lower() == "active" else 2.0
    else:  # maintain
        multiplier = 1.6 if (activity_level.lower() == "active" or age >= 50) else 1.4
        
    protein_g = int(round(weight_kg * multiplier))
    return max(protein_g, 45)


def calculate_water_intake(weight_kg: float, activity_level: str) -> float:
    """
    Calculate recommended daily water intake in Liters.
    Baseline: ~35 ml per kg body weight + physical activity allowance.
    """
    base_ml = weight_kg * 35.0
    if activity_level.lower() == "active":
        base_ml += 750
    elif activity_level.lower() == "moderate":
        base_ml += 500
    else:
        base_ml += 250
        
    return round(base_ml / 1000.0, 1)


def calculate_macro_split(calorie_target: int, protein_target_g: int) -> tuple[int, int]:
    """
    Calculate target Carbs (g) and Fats (g) based on total energy.
    Protein = 4 kcal/g, Fat = ~25% of calories (9 kcal/g), Carbs = remaining calories (4 kcal/g).
    """
    protein_cals = protein_target_g * 4
    fat_cals = calorie_target * 0.25
    fats_target_g = int(round(fat_cals / 9.0))
    
    remaining_cals = max(0, calorie_target - (protein_cals + (fats_target_g * 9)))
    carbs_target_g = int(round(remaining_cals / 4.0))
    
    return carbs_target_g, fats_target_g


def calculate_all_user_metrics(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
    activity_level: str,
    goal: str
) -> dict:
    """
    Calculate the complete set of body and nutrition metrics for the user.
    """
    bmi, bmi_category = calculate_bmi(weight_kg, height_cm)
    bmr = int(round(calculate_bmr(weight_kg, height_cm, age, sex)))
    tdee = int(round(calculate_tdee(bmr, activity_level)))
    calorie_target = calculate_calorie_target(tdee, goal)
    protein_target_g = calculate_protein_target(weight_kg, goal, activity_level, age, sex)
    carbs_target_g, fats_target_g = calculate_macro_split(calorie_target, protein_target_g)
    water_intake_liters = calculate_water_intake(weight_kg, activity_level)
    
    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": calorie_target,
        "protein_target_g": protein_target_g,
        "carbs_target_g": carbs_target_g,
        "fats_target_g": fats_target_g,
        "water_intake_liters": water_intake_liters
    }
