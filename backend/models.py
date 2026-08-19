from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any


class DietRequest(BaseModel):
    age: int = Field(ge=10, le=100, description="Age in years (10 to 100)")
    weight_kg: float = Field(gt=0, le=500, description="Weight in kilograms")
    height_cm: float = Field(gt=0, le=300, description="Height in centimeters")
    sex: Literal["male", "female"] = "male"
    diet_type: Literal["veg", "non-veg"]
    activity_level: Literal["sedentary", "moderate", "active"]
    goal: Literal["lose", "gain", "maintain"]
    allergies: Optional[str] = None
    free_text: Optional[str] = None


class UserMetrics(BaseModel):
    bmi: float
    bmi_category: str
    bmr: int
    tdee: int
    calorie_target: int
    protein_target_g: int
    carbs_target_g: int
    fats_target_g: int
    water_intake_liters: float


class DietResponse(BaseModel):
    user_metrics: UserMetrics
    weekday_plan: Dict[str, Any]
    weekend_plan: Dict[str, Any]
    exercise_plan: Dict[str, Any]
    key_nutrients: List[Dict[str, Any]]
    calorie_target: int  # Maintained for backwards compatibility
    notes: str


class RejectedResponse(BaseModel):
    message: str = "I can only assist with diet-related queries."
