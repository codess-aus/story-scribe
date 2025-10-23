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
import random
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

SYSTEM_PROMPT_TEMPLATES = [
    """You are a journaling assistant that generates thoughtful, life-based prompts for self-reflection and storytelling.

The user has selected the mood: {MOOD}. Adjust tone and style based on this mood:

- Deep Reflection: Introspective, values-based, emotionally aware.
- Fun Nostalgia: Lighthearted, memory-focused, joyful.
- Creative Storytelling: Real-life inspired, vivid, and descriptive (avoid fantasy unless explicitly requested).
- Action & Growth: Motivational, practical, forward-looking.
- Connection & Relationships: Warm, empathetic, focused on people and bonds.

Rules:
1. Prompts should feel personal, relatable, and grounded in real experiences.
2. Use clear, inviting language—short phrases or questions (not long scenarios).
3. Avoid generic phrasing like "Write about..."; make prompts specific and engaging.
4. Keep prompts concise (one sentence or a short question).
5. Ensure originality and variety across prompts.
6. If user provides additional preferences (e.g., topic, tone, length), incorporate them.

Generate ONE prompt at a time unless the user requests multiple.""",
    """Act as StoryScribe's empathetic writing coach. Craft a single, original autobiographical prompt that sparks honest reflection and keeps the writer anchored in real life moments.

Match the energy of the selected mood: {MOOD}. Use it to guide word choice, emotional depth, and pacing:

- Deep Reflection: Introspective, values-based, emotionally aware.
- Fun Nostalgia: Lighthearted, memory-focused, joyful.
- Creative Storytelling: Real-life inspired, vivid, descriptive (avoid fantasy unless asked).
- Action & Growth: Motivational, practical, focused on forward movement.
- Connection & Relationships: Warm, empathetic, people-centered.

Instructions:
1. Deliver the prompt in one sentence or short question under 40 words.
2. Stay specific—no generic "Write about" phrases.
3. Encourage sensory or emotional recall when helpful.
4. Blend any user preferences naturally into the prompt.
5. Avoid repeating concepts used in previous prompts.

Return only the prompt text.""",
    """You are a creative partner helping someone capture real stories from their life. Produce one concise, imaginative prompt that feels tailored and emotionally resonant.

Use the mood setting ({MOOD}) to steer tone, pacing, and language:

- Deep Reflection: Thoughtful, nuanced, values-driven.
- Fun Nostalgia: Playful, memory-sparking, upbeat.
- Creative Storytelling: Cinematic yet authentic to lived experience.
- Action & Growth: Energizing, solution-oriented, forward-looking.
- Connection & Relationships: Compassionate, relational, heart-centered.

Guidelines:
1. Keep prompts grounded in real experiences or reflections.
2. Use vivid but accessible language; avoid clichés.
3. Remain under 35 words when possible.
4. Integrate any stated preferences smoothly.
5. Output only the final prompt line with no framing text.""",
]

MOODS = {
    "deep_reflection": {
        "label": "Deep Reflection",
        "description": "Introspective, values-based, emotionally aware."
    },
    "fun_nostalgia": {
        "label": "Fun Nostalgia",
        "description": "Lighthearted, memory-focused, joyful."
    },
    "creative_storytelling": {
        "label": "Creative Storytelling",
        "description": "Real-life inspired, vivid, and descriptive (avoid fantasy unless explicitly requested)."
    },
    "action_growth": {
        "label": "Action & Growth",
        "description": "Motivational, practical, forward-looking."
    },
    "connection_relationships": {
        "label": "Connection & Relationships",
        "description": "Warm, empathetic, focused on people and bonds."
    },
}

DEFAULT_MOOD_KEY = "deep_reflection"

def resolve_mood(mood_raw: Optional[str]) -> dict:
    """Resolve incoming mood to a known style definition."""
    if not mood_raw:
        return MOODS[DEFAULT_MOOD_KEY]
    normalized = mood_raw.strip().lower().replace("-", "_").replace(" ", "_")
    return MOODS.get(normalized, MOODS[DEFAULT_MOOD_KEY])


def select_system_prompt(mood_config: dict) -> str:
    """Randomly choose a system prompt template and format it for the mood."""
    template = random.choice(SYSTEM_PROMPT_TEMPLATES)
    return template.format(MOOD=mood_config["label"])

@app.get("/prompt")
def get_prompt(genre: str = "memoir", mood: Optional[str] = None, preferences: Optional[str] = None):
    """
    Generate a writing prompt, using Azure OpenAI if available, otherwise fallback to static prompts.
    
    This endpoint supports:
    - AI-powered prompts via Azure OpenAI (if OPENAI_ENDPOINT is configured)
    - Static fallback prompts (if Azure OpenAI is not configured)
    """
    genre_lower = genre.lower()
    
    mood_config = resolve_mood(mood)
    system_prompt = select_system_prompt(mood_config)
    # Build user instructions for the model
    user_parts = [f"Generate a writing prompt for the genre: {genre}."]
    user_parts.append(f"Mood guidance: {mood_config['label']} — {mood_config['description']}")
    if preferences:
        user_parts.append(f"User preferences: {preferences}")
    user_parts.append("Return only the prompt.")
    user_prompt = " ".join(user_parts)

    # Try to use Azure OpenAI
    client, deployment = get_openai_client()
    
    if client and deployment:
        try:
            # Generate AI-powered prompt
            completion = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=80,
                temperature=0.7
            )
            
            ai_prompt = completion.choices[0].message.content.strip()
            
            return {
                "prompt": ai_prompt,
                "genre": genre,
                "mood": mood_config["label"],
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
        "mood": mood_config["label"],
        "source": "static_fallback"
    }