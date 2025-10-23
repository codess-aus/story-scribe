"""
Azure Function: generate_prompt (HTTP Trigger) - NO AUTH DEMO
WHAT: Returns an AI-generated autobiographical writing prompt.
WHY: Show integration with Azure OpenAI quickly.
HOW: Future: Add moderation, auth, and Cosmos persistence.
"""

import os
import json
import logging
import random
import azure.functions as func

def get_client():
    """Initialize Azure OpenAI client with proper authentication."""
    from azure.identity import DefaultAzureCredential
    from openai import AzureOpenAI
    
    endpoint = os.getenv("OPENAI_ENDPOINT")
    deployment = os.getenv("OPENAI_DEPLOYMENT", "gpt-4o-mini")
    api_version = os.getenv("OPENAI_API_VERSION", "2024-08-01-preview")
    
    if not endpoint:
        raise RuntimeError("OPENAI_ENDPOINT environment variable is missing.")
    
    # Get Azure credential token
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    
    # Create Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=token.token,
        api_version=api_version
    )
    
    return client, deployment

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

def resolve_mood(mood_raw: str) -> dict:
    """Normalize incoming mood text to known configuration."""
    if not mood_raw:
        return MOODS[DEFAULT_MOOD_KEY]
    normalized = mood_raw.strip().lower().replace("-", "_").replace(" ", "_")
    return MOODS.get(normalized, MOODS[DEFAULT_MOOD_KEY])


def select_system_prompt(mood_config: dict) -> str:
    """Randomly choose a system prompt template and format it for the mood."""
    template = random.choice(SYSTEM_PROMPT_TEMPLATES)
    return template.format(MOOD=mood_config["label"])

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger to generate writing prompts using Azure OpenAI.
    """
    logging.info("generate_prompt function invoked.")
    
    # Get parameters (genre, mood, preferences)
    genre = req.params.get("genre", "memoir").lower()
    mood_raw = req.params.get("mood")
    preferences = req.params.get("preferences")
    mood_config = resolve_mood(mood_raw)
    system_prompt = select_system_prompt(mood_config)
    
    # Build user instructions
    user_parts = [f"Generate a writing prompt for the genre: {genre}."]
    user_parts.append(f"Mood guidance: {mood_config['label']} — {mood_config['description']}")
    if preferences:
        user_parts.append(f"User preferences: {preferences}")
    user_parts.append("Return only the prompt.")
    user_prompt = " ".join(user_parts)
    
    try:
        # Get OpenAI client
        client, deployment = get_client()
        
        # Call Azure OpenAI
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=80,
            temperature=0.7
        )
        
        # Extract the generated prompt
        generated_prompt = completion.choices[0].message.content.strip()
        
        # Build response
        result = {
            "prompt": generated_prompt,
            "genre": genre,
            "mood": mood_config["label"],
            "tokens": {
                "prompt": completion.usage.prompt_tokens,
                "completion": completion.usage.completion_tokens,
                "total": completion.usage.total_tokens,
            },
        }
        
        logging.info(f"Successfully generated prompt for genre: {genre}")
        return func.HttpResponse(
            json.dumps(result), 
            mimetype="application/json", 
            status_code=200
        )
        
    except Exception as e:
        logging.exception("Error generating prompt")
        # Return fallback prompt on error
        fallback_result = {
            "prompt": "Write about a moment that changed your perspective on something important to you.",
            "genre": genre,
            "mood": mood_config["label"],
            "error": str(e),
            "fallback": True
        }
        return func.HttpResponse(
            json.dumps(fallback_result), 
            mimetype="application/json", 
            status_code=200
        )
    