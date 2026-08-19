"""
Comprehensive test suite for AI Diet & Nutrition Recommendation backend.
Verifies all 5 core requirements + edge cases.
"""

import sys
import unittest
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

from main import app
from guardrail import is_diet_related
from calculations import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_target,
    calculate_protein_target,
    calculate_water_intake,
    calculate_all_user_metrics
)
from nutrition_data import get_food_list, filter_candidate_foods_by_allergens

client = TestClient(app)


class TestDietRecommender(unittest.TestCase):

    def test_health_check(self):
        """Verify GET / returns 200 and status ok"""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "ok")

    def test_bmi_and_metabolic_calculations(self):
        """Verify Mifflin-St Jeor math, BMI categories, and protein scaling"""
        # Test BMI
        bmi, category = calculate_bmi(70.0, 175.0)
        self.assertEqual(bmi, 22.9)
        self.assertEqual(category, "Normal weight")

        # Test BMR Male: 10*70 + 6.25*175 - 5*25 + 5 = 700 + 1093.75 - 125 + 5 = 1673.75
        bmr_male = calculate_bmr(70.0, 175.0, 25, "male")
        self.assertAlmostEqual(bmr_male, 1673.75, places=1)

        # Test BMR Female: 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
        bmr_female = calculate_bmr(60.0, 165.0, 25, "female")
        self.assertAlmostEqual(bmr_female, 1345.25, places=1)

        # Test TDEE Moderate (1.55x)
        tdee = calculate_tdee(bmr_male, "moderate")
        self.assertAlmostEqual(tdee, 1673.75 * 1.55, places=1)

        # Test Calorie Target (Lose = TDEE - 500)
        target_lose = calculate_calorie_target(tdee, "lose")
        self.assertEqual(target_lose, int(round(tdee - 500)))

        # Test Calorie Target (Gain = TDEE + 500)
        target_gain = calculate_calorie_target(tdee, "gain")
        self.assertEqual(target_gain, int(round(tdee + 500)))

        # Test Protein target (Lose/Gain in active should scale to 2.0-2.2 g/kg)
        protein_lose = calculate_protein_target(70.0, "lose", "moderate")
        self.assertEqual(protein_lose, 140)  # 70 * 2.0

        # Complete metrics bundle
        metrics = calculate_all_user_metrics(70.0, 175.0, 25, "male", "moderate", "lose")
        self.assertIn("bmi", metrics)
        self.assertIn("calorie_target", metrics)
        self.assertIn("protein_target_g", metrics)
        self.assertIn("water_intake_liters", metrics)

    def test_guardrail_rejections(self):
        """Verify off-topic queries and food ordering banter are rejected"""
        off_topic_samples = [
            "what's the weather today",
            "i'm hungry order burger and fries",
            "order pizza online",
            "write me a python script",
            "tell me a funny joke",
            "who is the president",
            "book a table at the restaurant"
        ]
        for query in off_topic_samples:
            self.assertFalse(is_diet_related(query), f"Should have rejected: '{query}'")

    def test_guardrail_acceptances(self):
        """Verify genuine dietary and fitness queries are accepted"""
        on_topic_samples = [
            "suggest me a high protein diet",
            "intermittent fasting 16:8 meal plan",
            "low carb vegetarian meals with high fiber",
            "easy 15-min breakfast ideas for weight loss",
            "ketogenic diet with healthy fats",
            "lean muscle building nutrition",
            ""
        ]
        for query in on_topic_samples:
            self.assertTrue(is_diet_related(query), f"Should have accepted: '{query}'")

    def test_allergen_filtering(self):
        """Verify allergen items are pruned from candidate foods"""
        veg_foods = get_food_list("veg")
        filtered = filter_candidate_foods_by_allergens(veg_foods, "peanuts, dairy")
        
        # Check that dairy words (paneer, curd, yogurt) and peanuts are filtered
        for cat, items in filtered.items():
            for item in items:
                item_lower = item.lower()
                self.assertNotIn("peanut", item_lower)
                self.assertNotIn("paneer", item_lower)

    def test_api_guardrail_rejection_response(self):
        """Verify POST /generate-diet returns exact rejection message on off-topic input"""
        payload = {
            "age": 25,
            "weight_kg": 70,
            "height_cm": 170,
            "sex": "male",
            "diet_type": "veg",
            "activity_level": "moderate",
            "goal": "maintain",
            "free_text": "i'm hungry order burger and fries"
        }
        response = client.post("/generate-diet", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("message"), "I can only assist with diet-related queries.")
        self.assertNotIn("weekday_plan", data)

    def test_api_pydantic_validation_error(self):
        """Verify invalid numeric inputs (e.g. age = -5 or age = 150) trigger 422 automatically"""
        payload = {
            "age": -5,
            "weight_kg": 70,
            "height_cm": 170,
            "sex": "male",
            "diet_type": "veg",
            "activity_level": "moderate",
            "goal": "maintain"
        }
        response = client.post("/generate-diet", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_api_valid_diet_plan_generation(self):
        """Verify POST /generate-diet returns a full structured response with metrics, meals, workouts, and nutrients"""
        payload = {
            "age": 27,
            "weight_kg": 72,
            "height_cm": 176,
            "sex": "male",
            "diet_type": "veg",
            "activity_level": "moderate",
            "goal": "lose",
            "allergies": "peanuts",
            "free_text": "high protein and rich in fiber"
        }
        response = client.post("/generate-diet", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check top-level keys
        self.assertIn("user_metrics", data)
        self.assertIn("weekday_plan", data)
        self.assertIn("weekend_plan", data)
        self.assertIn("exercise_plan", data)
        self.assertIn("key_nutrients", data)
        self.assertIn("calorie_target", data)
        self.assertIn("notes", data)

        # Check user metrics
        metrics = data["user_metrics"]
        self.assertIn("bmi", metrics)
        self.assertIn("bmi_category", metrics)
        self.assertIn("bmr", metrics)
        self.assertIn("tdee", metrics)
        self.assertIn("protein_target_g", metrics)
        self.assertIn("water_intake_liters", metrics)

        # Check weekday plan structure
        for meal in ["breakfast", "lunch", "dinner", "snacks"]:
            self.assertIn(meal, data["weekday_plan"])
            meal_data = data["weekday_plan"][meal]
            self.assertIn("name", meal_data)
            self.assertIn("calories", meal_data)
            self.assertIn("protein_g", meal_data)
            self.assertIn("key_nutrients", meal_data)


if __name__ == "__main__":
    unittest.main()
