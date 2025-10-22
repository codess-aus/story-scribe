"""
StoryScribe Backend API
-----------------------
This is the main entry point for the StoryScribe backend service, implementing
a FastAPI application that handles user authentication, story management,
and AI integration.
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ai.content_safety import ContentModerationPipeline
from ai.progressive_prompting import ProgressivePromptingSystem
from db.models import Story, User

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="StoryScribe API",
    description="Backend API for StoryScribe, an AI-assisted diary-to-book application",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize AI services
content_safety = ContentModerationPipeline(
    os.getenv("CONTENT_SAFETY_ENDPOINT"),
    os.getenv("CONTENT_SAFETY_KEY")
)

# Pydantic models for request/response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str
    display_name: str

class StoryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    tags: Optional[List[str]] = []

class PromptRequest(BaseModel):
    user_id: str
    prompt_type: Optional[str] = "continuation"  # continuation, new_topic, genre_suggestion, title

class PromptResponse(BaseModel):
    prompt_text: str
    prompt_type: str
    related_topics: Optional[List[str]] = []

# User authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Here you would fetch the user from your database
    user = get_user_by_email(token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_user_by_email(email: str):
    """Placeholder for database lookup function"""
    # In a real implementation, this would query your database
    # For now, just return a mock user
    return User(
        user_id="1",
        email=email,
        display_name="Test User",
        password_hash=get_password_hash("password")
    )

# API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # In a real implementation, you would validate against your database
    # Mock implementation for demonstration
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user account
    """
    # Mock implementation - in a real app, you would check for existing users
    # and save to the database
    hashed_password = get_password_hash(user.password)
    
    # Content moderation check on display name
    safety_result = await content_safety.moderate_user_content(user.display_name)
    if not safety_result["is_safe"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Display name contains inappropriate content"
        )
    
    # Here you would save the user to your database
    return {"message": "User created successfully"}

@app.post("/stories", status_code=status.HTTP_201_CREATED)
async def create_story(story: StoryCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new story entry
    """
    # Content moderation
    safety_result = await content_safety.moderate_user_content(story.content)
    if not safety_result["is_safe"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Story contains inappropriate content: {safety_result['issues']}"
        )
    
    # Here you would save the story to your database
    return {"message": "Story created successfully", "story_id": "new_story_id"}

@app.get("/prompts", response_model=PromptResponse)
async def get_writing_prompt(prompt_request: PromptRequest, current_user: User = Depends(get_current_user)):
    """
    Generate a writing prompt for the user based on their history and preferences
    """
    # In a real implementation, you would:
    # 1. Fetch the user's previous stories
    # 2. Initialize the ProgressivePromptingSystem with real data
    # 3. Generate a personalized prompt
    
    # Mock implementation
    prompting_system = ProgressivePromptingSystem(
        openai_client=None,  # Would be initialized with actual client
        user_profile={"id": prompt_request.user_id},
        content_history=[]  # Would contain actual story history
    )
    
    # Generate a simple prompt for demonstration
    if prompt_request.prompt_type == "continuation":
        prompt = "Consider your most recent story. What happened next? How did the characters feel about it?"
    elif prompt_request.prompt_type == "new_topic":
        prompt = "Write about a childhood memory involving water. Was it a swimming pool, lake, ocean, or rain?"
    else:
        prompt = "Share a story about a time when you had to make a difficult decision."
    
    return PromptResponse(
        prompt_text=prompt,
        prompt_type=prompt_request.prompt_type,
        related_topics=["memory", "reflection", "personal growth"]
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
