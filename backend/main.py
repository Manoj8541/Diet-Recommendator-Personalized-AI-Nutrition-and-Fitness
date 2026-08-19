"""
FastAPI application for AI Diet & Nutrition Recommendation Web App.
Provides /generate-diet endpoint with smart guardrails, metabolic metrics,
rich nutritional breakdowns, and exercise recommendations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import DietRequest, DietResponse, RejectedResponse, UserMetrics
from guardrail import is_diet_related
from calculations import calculate_all_user_metrics
from nutrition_data import get_food_list, filter_candidate_foods_by_allergens
from groq_client import generate_diet_plan

app = FastAPI(
    title="AI Diet & Nutrition Recommendation API",
    description="Generate personalized diet, macro, and fitness plans using AI",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "AI Diet & Nutrition Recommendation API is running",
        "version": "2.0.0"
    }


@app.post("/generate-diet")
async def generate_diet(request: DietRequest):
    """
    Generate a personalized diet and fitness plan based on user parameters.
    
    Returns either a DietResponse with complete metrics & plan or a RejectedResponse
    if the query is off-topic.
    """
    # Step 1: Run guardrail filter if free_text is provided
    if request.free_text and request.free_text.strip():
        if not is_diet_related(request.free_text):
            return RejectedResponse(
                message="I can only assist with diet-related queries."
            )
    
    # Step 2: Calculate body metrics, calorie targets, protein, and water needs in Python
    try:
        user_metrics_dict = calculate_all_user_metrics(
            weight_kg=request.weight_kg,
            height_cm=request.height_cm,
            age=request.age,
            sex=request.sex,
            activity_level=request.activity_level,
            goal=request.goal
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating metabolic metrics: {str(e)}"
        )
    
    # Step 3: Get categorized candidate foods and filter out specified allergens
    base_foods = get_food_list(request.diet_type)
    candidate_foods = filter_candidate_foods_by_allergens(base_foods, request.allergies)
    
    # Step 4: Call Groq API to generate detailed diet, nutrient, and workout plan
    try:
        plan_data = generate_diet_plan(
            user_metrics=user_metrics_dict,
            diet_type=request.diet_type,
            activity_level=request.activity_level,
            goal=request.goal,
            candidate_foods=candidate_foods,
            allergies=request.allergies,
            free_text=request.free_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating nutrition and workout plan: {str(e)}"
        )
    
    # Step 5: Construct and return response
    return DietResponse(
        user_metrics=UserMetrics(**user_metrics_dict),
        weekday_plan=plan_data.get("weekday_plan", {}),
        weekend_plan=plan_data.get("weekend_plan", {}),
        exercise_plan=plan_data.get("exercise_plan", {}),
        key_nutrients=plan_data.get("key_nutrients", []),
        calorie_target=user_metrics_dict["calorie_target"],
        notes=plan_data.get("notes", "")
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
