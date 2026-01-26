# Akari Phase 3 - Product Decision Support System

A FastAPI-based system that helps users make informed product decisions through intent-based visualization and explanation.

## Features

- **Intent Detection**: Automatically detects user intent (compare/explain/clarify/choose)
- **Product Data Layer**: Structured product database with attributes
- **Cause-Effect Logic**: Rule-based mapping from intents to attributes and visual effects
- **Pre-Decision Checks**: Validates system readiness before decision support
- **Visualization Engine**: Renders visual triggers (highlight/zoom/split/label)
- **GPT-4 Explanation Layer**: Provides natural language explanations (read-only)

## Architecture

The system follows a strict separation of concerns:
1. **Product Data Layer**: Structured database with pre-defined attributes
2. **Logic Layer**: Rule-based intent → attribute mapping
3. **Visualization Layer**: Visual effects applied to products
4. **Explanation Layer**: GPT-4 provides natural language explanations (read-only)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

   **Note:** `psycopg2-binary` (PostgreSQL support) is commented out by default since SQLite is used for development. If you want to use PostgreSQL, you can:
   - Install PostgreSQL on your system first, then uncomment the line in `requirements.txt`
   - Or use: `pip install -r requirements-postgresql.txt` (may require PostgreSQL installed)

2. **Optional:** Install spaCy for enhanced NLP (not required - intent detection works with pattern matching):
```bash
pip install spacy
python -m spacy download en_core_web_sm
```
   Note: spaCy is optional. The intent detector uses pattern matching by default and works without spaCy.

3. Create `.env` file (copy from `.env.example` or create manually):
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///./akari.db

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

4. Seed the database with sample products (optional):
```bash
python scripts/seed_data.py
```

5. Run the application:
```bash
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Intent Detection
- `POST /api/v1/intent/detect` - Detect user intent from query
- `POST /api/v1/intent/process` - Process intent and return visualization
- `POST /api/v1/intent/choose` - Handle CHOOSE intent with pre-decision checks

### Explanation
- `POST /api/v1/explanation/generate` - Generate explanation using GPT-4
- `POST /api/v1/explanation/full` - Complete flow: intent → visualization → explanation

### Products
- `GET /api/v1/products` - Get all products
- `GET /api/v1/products/{product_id}` - Get product by ID
- `POST /api/v1/products` - Create a new product

## Example Usage

### Detect Intent and Get Visualization
```bash
curl -X POST "http://localhost:8000/api/v1/intent/process" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Compare AirPods Max vs AirPods Pro",
    "product_ids": ["airpods-max", "airpods-pro"]
  }'
```

### Full Flow with Explanation
```bash
curl -X POST "http://localhost:8000/api/v1/explanation/full" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "Which headphones are better for travel?",
    "product_ids": ["airpods-max", "airpods-pro", "sony-wh1000xm5"]
  }'
```

## Project Structure

```
src/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and session
├── models/                # SQLAlchemy models
├── schemas/               # Pydantic schemas
├── intents/               # Intent detection and handlers
├── checks/                # Pre-decision check modules
├── explanation/           # ChatGPT explanation layer
├── visualization/         # Visualization engine
├── data/                  # Product data layer
└── api/                   # API routes and endpoints
```

