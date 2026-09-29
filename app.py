from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # data validation
from groq import Groq  # LLM client
from dotenv import load_dotenv  # load .env file
import os

from agents import generate_draft, review_with_retry, GUIDELINES

load_dotenv()  # load GROQ_API_KEY from .env

app = FastAPI(title="Customer Complaint Reply Drafter with Critique Agent")

class ComplaintRequest(BaseModel):  # input schema
    complaint: str
    customer_name: str = "Customer"
    tone: str = "professional and empathetic"

class ReplyResponse(BaseModel):  # output schema
    draft_reply: str
    critique: str = ""
    revised: bool = False

@app.post("/draft-reply", response_model=ReplyResponse)  # POST endpoint
async def draft_reply(request: ComplaintRequest):
    if not request.complaint.strip():  # validate input
        raise HTTPException(status_code=400, detail="Complaint cannot be empty")
    
    try:
        draft = generate_draft(request.complaint, request.customer_name, request.tone)  # Agent 1
        draft, critique, passed = review_with_retry(draft, request.complaint)  # Agent 2: review up to 3 times
        
        return ReplyResponse(
            draft_reply=draft,
            critique=critique if not passed else "PASS after review",
            revised=not passed  # True if revisions were needed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating reply: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/guidelines")
async def get_guidelines():
    return {"guidelines": GUIDELINES.strip().split('\n')}