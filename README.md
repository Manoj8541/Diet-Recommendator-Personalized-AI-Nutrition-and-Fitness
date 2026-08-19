# AI Diet Recommendation Web App

A full-stack web application that generates personalized diet plans using AI. Built with FastAPI (Python) backend and React (Vite) frontend.

## Features

- 🎯 Personalized calorie calculations using Mifflin-St Jeor formula
- 🥗 Separate weekday and weekend meal plans
- 🛡️ Keyword-based guardrails to reject off-topic queries
- 🤖 AI-powered meal planning using Groq's Llama 3.3 70B model
- ⚡ Lightweight and fast - runs on low-end machines
- 🔒 No local LLM required - uses Groq API (free tier)

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- Groq API (llama-3.3-70b-versatile)
- Uvicorn

### Frontend
- React 18
- Vite
- Vanilla CSS

## Project Structure

```
Diet Suggestor/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic schemas
│   ├── guardrail.py         # Keyword-based topic filter
│   ├── calculations.py      # BMR/TDEE calculations
│   ├── nutrition_data.py    # Food lists
│   ├── groq_client.py       # Groq API wrapper
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variables template
│   └── README.md            # Backend setup instructions
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Styles
│   │   ├── main.jsx         # React entry point
│   │   └── index.css        # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md                # This file
```

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 16 or higher
- Groq API key (free from https://console.groq.com)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file from the example:
```bash
copy .env.example .env
```

6. Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_actual_key_here
```

7. Run the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Usage

1. Ensure both backend and frontend servers are running
2. Open http://localhost:5173 in your browser
3. Fill out the form with your details:
   - Age, weight, height
   - Sex (male/female)
   - Diet type (vegetarian/non-vegetarian)
   - Activity level
   - Goal (lose/gain/maintain weight)
   - Allergies (optional)
   - Additional query (optional - for testing guardrails)
4. Click "Generate Diet Plan"
5. View your personalized weekday and weekend meal plans

## Testing the Guardrails

To test the off-topic rejection feature, enter text unrelated to diet/nutrition in the "Additional Query" field:

**Should be rejected:**
- "What's the weather today?"
- "Tell me a joke"
- "Write me a poem"

**Should be accepted:**
- "I want a high protein diet"
- "Suggest me low carb meals"
- Empty field (normal operation)

When rejected, you'll see the message: "I can only assist with diet-related queries."

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Design Decisions

1. **Calorie Calculation**: Pure Python math using Mifflin-St Jeor formula - no LLM involvement ensures accuracy and consistency

2. **Guardrails**: Lightweight keyword matching instead of ML models - executes in <5ms with zero memory overhead

3. **Food Grounding**: Static food lists prevent LLM hallucination and ensure only valid/sensible meals are suggested

4. **JSON Mode**: Groq's JSON mode ensures structured, parsable responses with automatic retry logic

5. **No Database**: Stateless design keeps deployment simple and resource usage minimal

## Security Notes

- Never commit `.env` files with real API keys
- The `.env` file is git-ignored by default
- Use environment variables for all sensitive configuration

## Troubleshooting

### Backend won't start
- Check if Python 3.10+ is installed: `python --version`
- Ensure virtual environment is activated
- Verify Groq API key is set in `.env`

### Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify fetch URL in `frontend/src/App.jsx`

### Groq API errors
- Check your API key is valid
- Ensure you haven't exceeded free tier limits
- Check network connectivity

## License

This project is built as a demonstration of AI-powered diet planning. Use responsibly and consult healthcare professionals for actual dietary advice.

## Notes

- This app provides general diet suggestions and should not replace professional medical or nutritional advice
- The calorie calculations use standard formulas but individual needs may vary
- Always consult with healthcare providers before making significant dietary changes
