from groq import Groq  # LLM client
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])  # init Groq client

GUIDELINES = """
1. Acknowledge frustration FIRST, before any explanation
2. No specific refund amounts/timelines - say "our team will follow up with next steps"
3. Never blame customer or other departments
4. Under 120 words
5. End by inviting reply if more questions"""

def generate_draft(complaint: str, customer_name: str, tone: str) -> str:
    """Agent 1: Draft initial reply using guidelines"""
    prompt = f"""Write a {tone} reply to {customer_name} about: "{complaint}"

Rules:
{GUIDELINES}

Reply:"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,  # creative
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def critique_draft(draft: str, complaint: str) -> str:
    """Agent 2: Review draft against guidelines"""
    prompt = f"""Review this draft against rules:
{GUIDELINES}

Draft: {draft}
Complaint: {complaint}

If any rule violated, reply: VIOLATION: [rule numbers] FIX: [how to fix]
If all pass, reply: PASS"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # precise
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def revise_draft(draft: str, complaint: str, critique: str) -> str:
    """Agent 2: Fix draft based on critique"""
    prompt = f"""Fix this draft. Rules:
{GUIDELINES}

Complaint: {complaint}
Draft: {draft}
Issues: {critique}

Corrected reply:"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,  # balanced
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

def review_with_retry(draft: str, complaint: str, max_attempts: int = 3) -> tuple[str, str, bool]:
    """Agent 2: Review and revise up to max_attempts times until PASS or reject"""
    current_draft = draft
    last_critique = ""
    
    for attempt in range(max_attempts):
        critique = critique_draft(current_draft, complaint)
        last_critique = critique
        
        if critique == "PASS":
            return current_draft, critique, True
        
        if critique.startswith("VIOLATION:"):
            current_draft = revise_draft(current_draft, complaint, critique)
    
    return current_draft, last_critique, False