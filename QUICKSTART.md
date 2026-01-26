# Quick Start Guide

## Prerequisites
- Python 3.9 or higher
- pip package manager

## Installation Steps

1. **Clone/Navigate to the project directory**

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

   **Note:** PostgreSQL support (`psycopg2-binary`) is optional and commented out by default. The project uses SQLite by default, which doesn't require any additional setup.

4. **Optional:** Install spaCy for enhanced NLP (not required):
```bash
pip install spacy
python -m spacy download en_core_web_sm
```
   Note: spaCy is optional - the intent detector works with pattern matching by default.

5. **Set up environment variables:**
   - Copy `.env.example` to `.env` (or create `.env` manually)
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-4
   DATABASE_URL=sqlite:///./akari.db
   ```

6. **Seed sample data (optional but recommended):**
```bash
python scripts/seed_data.py
```

7. **Start the server:**
```bash
uvicorn src.main:app --reload
```

8. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Testing the API

### Example 1: Detect Intent
```bash
curl -X POST "http://localhost:8000/api/v1/intent/detect" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Compare AirPods Max and AirPods Pro"}'
```

### Example 2: Full Flow with Explanation
```bash
curl -X POST "http://localhost:8000/api/v1/explanation/full" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Which one is better for travel?",
    "product_ids": ["airpods-max", "airpods-pro"]
  }'
```

### Example 3: Get All Products
```bash
curl http://localhost:8000/api/v1/products
```

## Project Structure Overview

```
.
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── intents/             # Intent detection & handling
│   ├── checks/              # Pre-decision checks
│   ├── explanation/         # GPT-4 explanation layer
│   ├── visualization/       # Visualization engine
│   ├── data/                # Product data service
│   └── api/                 # API routes
├── scripts/
│   └── seed_data.py         # Database seeding script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
└── README.md                # Full documentation
```

## Key Features

1. **Intent Detection**: Automatically detects user intent (compare/explain/clarify/choose)
2. **Product Data**: Structured product database with attributes
3. **Pre-Decision Checks**: Validates readiness before decision support
4. **Visualization**: Generates visual effect instructions
5. **GPT-4 Explanations**: Natural language explanations (read-only)

## Troubleshooting

### Issue: spaCy model not found
**Solution:** Run `python -m spacy download en_core_web_sm`

### Issue: OpenAI API errors
**Solution:** Check your `.env` file has the correct `OPENAI_API_KEY`

### Issue: Database errors
**Solution:** Make sure the database file is writable, or change `DATABASE_URL` in `.env`

### Issue: Import errors
**Solution:** Make sure you're in the project root directory and virtual environment is activated

