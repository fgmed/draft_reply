# Customer Complaint Reply Drafter

A FastAPI service that generates professional customer support replies using a two-agent system with Groq LLM.

## Architecture

**Agent 1 (Drafter)**: Creates initial empathetic reply following company guidelines

**Agent 2 (Critic)**: Reviews draft against guidelines, revises up to 3 times until PASS or rejects

## Company Guidelines

1. Acknowledge frustration FIRST, before any explanation
2. No specific refund amounts/timelines - say "our team will follow up with next steps"
3. Never blame customer or other departments
4. Keep replies under 120 words
5. End by inviting reply if more questions

## Project Structure

```
├── app.py              # FastAPI application with routes
├── agents.py           # Agent logic (draft, critique, revise, review)
├── requirements.txt    # Python dependencies
└── .env                # GROQ_API_KEY (not tracked)
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export $(cat .env | xargs)

# Run with auto-reload
uvicorn app:app --reload
```

Server runs at `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/draft-reply` | Generate reply for complaint |
| GET | `/health` | Health check |
| GET | `/guidelines` | List company guidelines |

### POST /draft-reply

**Request:**
```json
{
  "complaint": "string",
  "customer_name": "string (optional)",
  "tone": "string (optional, default: professional and empathetic)"
}
```

**Response:**
```json
{
  "draft_reply": "string",
  "critique": "string (PASS after review or VIOLATION details)",
  "revised": "boolean"
}
```

## Example

```bash
curl -X POST http://localhost:8000/draft-reply \
  -H "Content-Type: application/json" \
  -d '{
    "complaint": "My order arrived broken for the third time",
    "customer_name": "John"
  }'
```

## Deployment

Set `GROQ_API_KEY` as environment variable (not in .env):

```bash
export GROQ_API_KEY=your_key_here
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Requirements

- Python 3.10+
- Groq API key
- Dependencies in `requirements.txt`