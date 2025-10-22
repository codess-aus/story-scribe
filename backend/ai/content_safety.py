"""
Progressive Prompting System
----------------------------
This module provides intelligent writing prompts to users based on their
writing history, preferences, and current stage in their book development.

The system adapts over time to help users develop more comprehensive and
cohesive narratives that can form chapters in their book.
"""
import json
import logging
import random
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

import azure.ai.openai as openai
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptType(str, Enum):
    CONTINUATION = "continuation"
    NEW_TOPIC = "new_topic"
    GENRE_SUGGESTION = "genre_suggestion"
    TITLE_RECOMMENDATION = "title_recommendation"
    REFINEMENT = "refinement"
    REFLECTION = "reflection"

class StoryMetadata(BaseModel):
    """Metadata about a user's story for analysis purposes"""
    story_id: str
    title: Optional[str]
    content_preview: str  # First ~200 chars of content
    created_at: datetime
    word_count: int
    completion_status: float  # 0 to 1 value estimating story completeness
    themes: Optional[List[str]] = []
    characters: Optional[List[str]] = []
    sentiment: Optional[str] = None

class UserProfile(BaseModel):
    """Information about the user to personalize prompts"""
    user_id: str
    display_name: Optional[str] = None
    writing_frequency: Optional[float] = None  # Average stories per week
    favorite_genres: Optional[List[str]] = []
    writing_goals: Optional[str] = None
    genre_selected: bool = False
    title_selected: bool = False

class ProgressivePromptingSystem:
    """
    A system that provides intelligent writing prompts based on user's 
    writing history and current stage in their book development journey.
    """
    
    def __init__(
        self,
        openai_client,
        user_profile: Dict,
        content_history: List[Dict] = None
    ):
        """
        Initialize the prompting system with user information and content history.
        
        Args:
            openai_client: Azure OpenAI client for generating personalized prompts
            user_profile: Information about the user
            content_history: List of user's previous stories/entries
        """
        self.openai_client = openai_client
        self.user_profile = UserProfile(**user_profile)
        self.content_history = []
        
        # Process content history if provided
        if content_history:
            for story in content_history:
                if isinstance(story, dict):
                    self.content_history.append(StoryMetadata(**story))
                else:
                    self.content_history.append(story)
        
        # Determine the current prompting stage based on user history
        self.prompting_stage = self._determine_prompting_stage()
        logger.info(f"Initialized prompting system in stage: {self.prompting_stage}")
    
    def _determine_prompting_stage(self) -> PromptType:
        """
        Determines what stage of prompting is appropriate based on user's content
        history and profile.
        
        Returns:
            PromptType: The appropriate prompt type for the user's current state
        """
        # If no content yet, start with a new topic
        if not self.content_history:
            return PromptType.NEW_TOPIC
        
        # Get most recent story
        recent_entry = self.content_history[-1]
        
        # If the most recent story is incomplete, suggest continuing it
        if recent_entry.completion_status < 0.8:
            return PromptType.CONTINUATION
        
        # Suggest genre after enough stories have been written
        if len(self.content_history) >= 10 and not self.user_profile.genre_selected:
            return PromptType.GENRE_SUGGESTION
        
        # Suggest title after genre is selected and more content is available
        if (len(self.content_history) >= 15 and 
            self.user_profile.genre_selected and 
            not self.user_profile.title_selected):
            return PromptType.TITLE_RECOMMENDATION
        
        # Alternate between new topics and refinement based on content amount
        if len(self.content_history) % 3 == 0:
            return PromptType.REFINEMENT
        else:
            return PromptType.NEW_TOPIC
    
    async def generate_next_prompt(self) -> Dict:
        """
        Generates the most appropriate next prompt for the user based on 
        their history, profile, and current stage.
        
        Returns:
            Dict: The generated prompt with metadata
        """
        try:
            # Determine which type of prompt to generate
            if self.prompting_stage == PromptType.CONTINUATION:
                result = await self._create_continuation_prompt()
            elif self.prompting_stage == PromptType.NEW_TOPIC:
                result = await self._create_new_topic_prompt()
            elif self.prompting_stage == PromptType.GENRE_SUGGESTION:
                result = await self._suggest_genres()
            elif self.prompting_stage == PromptType.TITLE_RECOMMENDATION:
                result = await self._recommend_titles()
            elif self.prompting_stage == PromptType.REFINEMENT:
                result = await self._create_refinement_prompt()
            else:
                result = await self._create_reflection_prompt()
            
            return {
                "prompt_text": result["prompt"],
                "prompt_type": self.prompting_stage,
                "related_topics": result.get("related_topics", []),
                "additional_context": result.get("additional_context", {})
            }
            
        except Exception as e:
            logger.error(f"Error generating prompt: {e}")
            # Fallback to a simple prompt if the AI service fails
            return {
                "prompt_text": self._get_fallback_prompt(),
                "prompt_type": "fallback",
                "related_topics": ["writing", "creativity"],
                "additional_context": {"error": str(e)}
            }
    
    async def _create_continuation_prompt(self) -> Dict:
        """Generate a prompt to continue the user's most recent story"""
        if not self.content_history:
            return self._create_new_topic_prompt()
        
        recent_story = self.content_history[-1]
        
        # In a real implementation, you would use the OpenAI client to generate 
        # a personalized continuation prompt based on the recent story content
        # For this example, we'll return a templated response
        
        prompt = (
            f"Let's continue developing your story \"{recent_story.title or 'your recent story'}\". "
            f"You wrote about {recent_story.content_preview}... "
            f"What happens next? How do the events unfold from here?"
        )
        
        return {
            "prompt": prompt,
            "related_topics": recent_story.themes or ["narrative", "development", "continuation"]
        }
    
    async def _create_new_topic_prompt(self) -> Dict:
        """Generate a prompt for a new story topic"""
        # For a production app, this would use the OpenAI client to generate
        # a personalized topic based on user's history and preferences
        
        # Example topics that could be expanded with AI generation
        topic_templates = [
            "Write about a time when you felt completely out of your element. What happened and how did you adapt?",
            "Share a memory involving a specific smell or taste that transports you back to a specific moment.",
            "Describe an encounter with a stranger that left a lasting impression on you.",
            "Write about a tradition in your family or community that has special meaning to you.",
            "Share a story about a journey - either literal or metaphorical - that changed your perspective.",
            "Describe a moment when you had to make a difficult choice between two things you wanted.",
        ]
        
        return {
            "prompt": random.choice(topic_templates),
            "related_topics": ["memory", "experience", "reflection"]
        }
    
    async def _suggest_genres(self) -> Dict:
        """Analyze existing stories and suggest potential genres for the book"""
        # In a real implementation, you would analyze the content history
        # using Azure OpenAI to identify common themes and suggest genres
        
        # For this example, we'll provide a mock response
        suggested_genres = ["Memoir", "Personal Development", "Travel Writing", "Coming of Age"]
        
        prompt = (
            "Based on the stories you've shared so far, your writing might fit well into "
            f"these genres: {', '.join(suggested_genres)}. \n\n"
            "Which of these resonates with you? Or is there another genre you'd prefer? "
            "Share a story that reflects the genre you're most interested in exploring further."
        )
        
        return {
            "prompt": prompt,
            "related_topics": ["genre", "book development", "writing style"],
            "additional_context": {
                "suggested_genres": suggested_genres
            }
        }
    
    async def _recommend_titles(self) -> Dict:
        """Suggest potential book titles based on content analysis"""
        # For a real implementation, this would analyze themes and content
        # using Azure OpenAI to generate appropriate title suggestions
        
        # Mock response
        suggested_titles = [
            "Echoes of Memory: A Personal Journey",
            "Between the Lines of Life",
            "Moments That Defined Me",
            "The Tapestry of Experience"
        ]
        
        prompt = (
            "Your collection of stories is taking shape! Here are some potential titles "
            f"for your book: {', '.join(suggested_titles)}. \n\n"
            "Do any of these titles speak to you? Write a story that could serve as the "
            "opening chapter, setting the tone for your book under your favorite title."
        )
        
        return {
            "prompt": prompt,
            "related_topics": ["book title", "introduction", "theme development"],
            "additional_context": {
                "suggested_titles": suggested_titles
            }
        }
    
    async def _create_refinement_prompt(self) -> Dict:
        """Generate a prompt to refine or expand an existing story"""
        if not self.content_history:
            return self._create_new_topic_prompt()
        
        # In a real implementation, this would select a story that could benefit
        # from refinement based on AI analysis of the content
        
        # For this example, choose a random story from the user's history
        story_to_refine = random.choice(self.content_history)
        
        prompt = (
            f"Let's revisit your story \"{story_to_refine.title or 'from before'}\". "
            "Consider adding more sensory details or dialogue to make it more vivid. "
            "How might you expand on the emotions or thoughts of the people involved? "
            "Try rewriting a section with these enhancements."
        )
        
        return {
            "prompt": prompt,
            "related_topics": ["editing", "enhancement", "detail"],
            "additional_context": {
                "story_id": story_to_refine.story_id
            }
        }
    
    def _create_reflection_prompt(self) -> Dict:
        """Generate a prompt asking the user to reflect on their stories"""
        prompt = (
            "Looking back on the stories you've written so far, what themes or patterns "
            "do you notice emerging? Which stories feel most meaningful to you, and why? "
            "Write a reflection on your journey as an author up to this point."
        )
        
        return {
            "prompt": prompt,
            "related_topics": ["reflection", "themes", "writer's journey"]
        }
    
    def _get_fallback_prompt(self) -> str:
        """Provide a simple fallback prompt if AI generation fails"""
        fallback_prompts = [
            "Write about a memorable conversation you've had recently.",
            "Describe a place that has special meaning to you.",
            "Share a story about an object you treasure.",
            "Write about a skill you've learned or want to learn."
        ]
        return random.choice(fallback_prompts)
