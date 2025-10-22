"""
FastAPI backend for StoryScribe (NO AUTH DEMO).
WHAT: Provides story CRUD and a placeholder prompt endpoint.
WHY: Demonstrates end-to-end flow without identity overhead.
HOW: Replace user header extraction with JWT validation later.
"""

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

app = FastAPI(title="StoryScribe Backend (Demo No Auth)")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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

@app.get("/prompt")
def get_prompt(genre: str = "memoir"):
    """
    Placeholder prompt endpoint for demo.
    In production, this would call the Azure Function or integrate directly.
    For now, returns a simple prompt to demonstrate the flow.
    """
    prompts = {
        "memoir": "Write about a moment from your childhood that shaped who you are today. What happened, and why does it matter?",
        "adventure": "Describe a time you stepped outside your comfort zone. What did you discover about yourself?",
        "reflection": "Think about a relationship that changed your perspective. What did you learn?",
        "creative": "Imagine your life as a book. What would the opening line be, and why?",
    }
    prompt_text = prompts.get(genre.lower(), prompts["memoir"])
    return {"prompt": prompt_text, "genre": genre}