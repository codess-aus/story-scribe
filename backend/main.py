"""
FastAPI backend for StoryScribe (NO AUTH DEMO).
WHAT: Provides story CRUD and AI-powered prompt generation.
WHY: Demonstrates end-to-end flow without identity overhead.
HOW: Replace user header extraction with JWT validation later.
"""

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="StoryScribe Backend (Demo No Auth)")

# Enable CORS for local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ambitious-cliff-0afea2203.3.azurestaticapps.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORIES = {}  # In-memory; swap with Cosmos repository

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def get_user(x_user_id: Optional[str]) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id (demo)")
    return x_user_id

class StoryCreate(BaseModel):
    title: str
    content: str

class StoryOut(BaseModel):
    id: str
    title: str
    content: str
    userId: str
    createdAt: str
    updatedAt: str

@app.post("/stories", response_model=StoryOut)
def create_story(payload: StoryCreate, x_user_id: Optional[str] = Header(default=None)):
    user = get_user(x_user_id)
    story_id = "story_" + uuid.uuid4().hex[:8]
    doc = {
        "id": story_id,
        "title": payload.title,
        "content": payload.content,
        "userId": user,
        "createdAt": now_iso(),
        "updatedAt": now_iso(),
    }
    STORIES.setdefault(user, []).append(doc)
    return doc

@app.get("/stories", response_model=List[StoryOut])
def list_stories(x_user_id: Optional[str] = Header(default=None)):
    user = get_user(x_user_id)
    return STORIES.get(user, [])

@app.get("/health")
def health():
    return {"status": "ok", "mode": "no-auth"}

def get_openai_client():
    """
    Initialize Azure OpenAI client if credentials are available.
    Returns (client, deployment_name) or (None, None) if not configured.
    """
    try:
        from openai import AzureOpenAI
        
        endpoint = os.getenv("OPENAI_ENDPOINT")
        deployment = os.getenv("OPENAI_DEPLOYMENT", "gpt-4o-mini")
        api_version = os.getenv("OPENAI_API_VERSION", "2024-08-01-preview")
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not endpoint:
            return None, None
        
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment")
            return None, None
        
        # Create Azure OpenAI client with API key
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        return client, deployment
    except Exception as e:
        print(f"Warning: Could not initialize Azure OpenAI: {e}")
        return None, None

# Static fallback prompts
FALLBACK_PROMPTS = {
    "memoir": "Write about a moment from your childhood that shaped who you are today. What happened, and why does it matter?",
    "adventure": "Describe a time you stepped outside your comfort zone. What did you discover about yourself?",
    "reflection": "Think about a relationship that changed your perspective. What did you learn?",
    "creative": "Imagine your life as a book. What would the opening line be, and why?",
}

SYSTEM_PROMPT = (
    "You are StoryScribe's creative writing assistant. Generate ONE vivid, reflective "
    "autobiographical writing prompt that inspires personal storytelling. Keep it under 40 words "
    "and make it emotionally engaging."
)

@app.get("/prompt")
def get_prompt(genre: str = "memoir"):
    """
    Generate a writing prompt, using Azure OpenAI if available, otherwise fallback to static prompts.
    
    This endpoint supports:
    - AI-powered prompts via Azure OpenAI (if OPENAI_ENDPOINT is configured)
    - Static fallback prompts (if Azure OpenAI is not configured)
    """
    genre_lower = genre.lower()
    
    # Try to use Azure OpenAI
    client, deployment = get_openai_client()
    
    if client and deployment:
        try:
            # Generate AI-powered prompt
            user_prompt = f"Generate a writing prompt for the genre: {genre}"
            
            completion = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=80,
                temperature=0.7
            )
            
            ai_prompt = completion.choices[0].message.content.strip()
            
            return {
                "prompt": ai_prompt,
                "genre": genre,
                "source": "azure_openai",
                "model": deployment
            }
        except Exception as e:
            print(f"Error calling Azure OpenAI: {e}")
            # Fall through to static prompts
    
    # Fallback to static prompts
    prompt_text = FALLBACK_PROMPTS.get(genre_lower, FALLBACK_PROMPTS["memoir"])
    return {
        "prompt": prompt_text,
        "genre": genre,
        "source": "static_fallback"
    }