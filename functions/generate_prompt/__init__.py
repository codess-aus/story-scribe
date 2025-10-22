"""
Azure Function: generate_prompt (HTTP Trigger) - NO AUTH DEMO
WHAT: Returns an AI-generated autobiographical writing prompt.
WHY: Show integration with Azure OpenAI quickly.
HOW: Future: Add moderation, auth, and Cosmos persistence.
"""

import os
import json
import logging
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

SYSTEM_PROMPT = (
    "You are StoryScribe's creative writing assistant. Generate ONE vivid, reflective "
    "autobiographical writing prompt that inspires personal storytelling. Keep it under 40 words "
    "and make it emotionally engaging."
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger to generate writing prompts using Azure OpenAI.
    """
    logging.info("generate_prompt function invoked.")
    
    # Get genre parameter (default to memoir)
    genre = req.params.get("genre", "memoir").lower()
    
    try:
        # Get OpenAI client
        client, deployment = get_client()
        
        # Create the prompt request
        user_prompt = f"Generate a writing prompt for the genre: {genre}"
        
        # Call Azure OpenAI
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
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
            "error": str(e),
            "fallback": True
        }
        return func.HttpResponse(
            json.dumps(fallback_result), 
            mimetype="application/json", 
            status_code=200
        )
    