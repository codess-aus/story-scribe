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
    """Generate ONE short personal reflection question.

Current topic: {MOOD}

PERFECT EXAMPLES:
- "What belief has shaped your life the most?"
- "What was your favorite childhood snack?"
- "Which person taught you the most about kindness?"
- "What habit do you want to break?"
- "Who makes you laugh the hardest?"

STRICT FORMAT:
1. Use ONLY: What/When/Who/Where/Which/How
2. Max 7-8 words before optional "and why?"
3. Focus on ONE specific thing
4. NO phrases like "tell me" or "write about"
5. NO complex clauses or scenarios

Output the question only."""
]

MOODS = {
    "deep_reflection": {
        "label": "Deep Reflection",
        "description": "beliefs, values, life lessons"
    },
    "fun_nostalgia": {
        "label": "Fun Nostalgia",
        "description": "childhood memories, games, favorite things"
    },
    "creative_storytelling": {
        "label": "Creative Storytelling",
        "description": "memorable moments, surprises, achievements"
    },
    "action_growth": {
        "label": "Action & Growth",
        "description": "goals, habits, personal changes"
    },
    "connection_relationships": {
        "label": "Connection & Relationships",
        "description": "people, friendships, family"
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
            "prompt": "What moment changed your perspective, and why?",
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
    