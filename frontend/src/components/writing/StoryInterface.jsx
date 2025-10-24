/**
 * StoryInterface Component
 * 
 * This component provides the core writing interface for users to create and edit
 * their stories. It includes the AI prompt system, rich text editor, and feedback
 * mechanisms.
 */
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Editor } from '@tinymce/tinymce-react';
import { useAuth } from '../../contexts/AuthContext';
import PromptPanel from './PromptPanel';
import AISuggestionPanel from './AISuggestionPanel';
import SaveIndicator from '../ui/SaveIndicator';

import '../../styles/StoryInterface.css';

const StoryInterface = () => {
  const { storyId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const editorRef = useRef(null);
  
  // State variables
  const [story, setStory] = useState({
    title: '',
    content: '',
    tags: [],
    lastSaved: null
  });
  const [currentPrompt, setCurrentPrompt] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState('saved'); // 'saved', 'saving', 'error'
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  
  // Load existing story or get a new prompt
  useEffect(() => {
    const loadStoryOrPrompt = async () => {
      if (storyId) {
        // Load existing story
        try {
          // This would be a real API call in production
          const response = await fetch(`/api/stories/${storyId}`);
          if (response.ok) {
            const storyData = await response.json();
            setStory({
              title: storyData.title || '',
              content: storyData.content || '',
              tags: storyData.tags || [],
              lastSaved: new Date(storyData.lastEditedAt || storyData.createdAt)
            });
          } else {
            console.error('Failed to load story');
            navigate('/'); // Redirect to dashboard if story not found
          }
        } catch (error) {
          console.error('Error loading story', error);
        }
      } else {
        // New story - get a writing prompt
        fetchWritingPrompt();
      }
    };
    
    loadStoryOrPrompt();
  }, [storyId, navigate]);
  
  /**
   * Fetches a writing prompt from the backend API based on user history
   */
  const fetchWritingPrompt = async () => {
    try {
      // This would be a real API call in production
      // const response = await fetch('/api/prompts', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({ 
      //     user_id: user.id,
      //     prompt_type: 'new_topic' 
      //   }),
      // });
      
      // Mock response for demonstration
      const mockPrompt = {
        prompt_text: 'Write about a childhood memory that taught you an important life lesson. What happened, and how has that lesson stayed with you over the years?',
        prompt_type: 'new_topic',
        related_topics: ['memory', 'childhood', 'lessons', 'growth']
      };
      
      setCurrentPrompt(mockPrompt);
    } catch (error) {
      console.error('Error fetching writing prompt', error);
      // Set a fallback prompt
      setCurrentPrompt({
        prompt_text: 'Write about an experience that changed your perspective on something important to you.',
        prompt_type: 'fallback',
        related_topics: []
      });
    }
  };
  
  /**
   * Handles changes to the story title
   */
  const handleTitleChange = (e) => {
    setStory(prev => ({
      ...prev,
      title: e.target.value
    }));
    setSaveStatus('unsaved');
  };
  
  /**
   * Handles changes to the story content from the rich text editor
   */
  const handleEditorChange = (content) => {
    setStory(prev => ({
      ...prev,
      content: content
    }));
    setSaveStatus('unsaved');
    
    // Schedule auto-save
    debouncedSave();
  };
  
  /**
   * Debounced save function to prevent excessive API calls
   */
  const debouncedSave = useRef(
    setTimeout(() => {
      console.log('Debounce not yet initialized');
    }, 2000)
  ).current;
  
  useEffect(() => {
    // Clear timeout on component unmount
    return () => clearTimeout(debouncedSave);
  }, [debouncedSave]);
  
  /**
   * Saves the current story to the backend
   */
  const saveStory = async () => {
    if (story.content.trim() === '') return;
    
    setIsSaving(true);
    setSaveStatus('saving');
    
    try {
      // This would be a real API call in production
      // const response = await fetch(storyId ? `/api/stories/${storyId}` : '/api/stories', {
      //   method: storyId ? 'PUT' : 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     title: story.title,
      //     content: story.content,
      //     tags: story.tags
      //   }),
      // });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update save timestamp
      setStory(prev => ({
        ...prev,
        lastSaved: new Date()
      }));
      
      setSaveStatus('saved');
      
      // If this was a new story, redirect to the edit URL with the new ID
      if (!storyId) {
        // In a real app, you'd get the ID from the API response
        const newStoryId = 'new-story-' + Date.now();
        navigate(`/edit/${newStoryId}`, { replace: true });
      }
    } catch (error) {
      console.error('Error saving story', error);
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };
  
  /**
   * Gets AI suggestions for the current content
   */
  const getAISuggestions = async () => {
    if (story.content.trim() === '') return;
    
    try {
      // This would be a real API call to get AI suggestions in production
      // For now, we'll simulate some suggestions
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockSuggestions = [
        {
          type: 'style',
          suggestion: 'Consider adding more sensory details to the second paragraph to help readers visualize the scene.',
          context: 'paragraph 2'
        },
        {
          type: 'structure',
          suggestion: 'Your story might benefit from a stronger conclusion that ties back to the main theme.',
          context: 'ending'
        },
        {
          type: 'enhancement',
          suggestion: 'You could expand on the character\'s motivation when they decide to take action.',
          context: 'character development'
        }
      ];
      
      setAiSuggestions(mockSuggestions);
      setShowAISuggestions(true);
    } catch (error) {
      console.error('Error getting AI suggestions', error);
    }
  };
  
  return (
    <div className="story-interface">
      <div className="story-header">
        <input
          type="text"
          value={story.title}
          onChange={handleTitleChange}
          placeholder="Story Title"
          className="story-title-input"
        />
        <SaveIndicator status={saveStatus} lastSaved={story.lastSaved} />
      </div>
      
      {currentPrompt && (
        <PromptPanel 
          prompt={currentPrompt} 
          onNewPrompt={fetchWritingPrompt}
          onDismiss={() => setCurrentPrompt(null)}
        />
      )}
      
      <div className="editor-container">
        <Editor
          onInit={(evt, editor) => editorRef.current = editor}
          value={story.content}
          onEditorChange={handleEditorChange}
          init={{
            height: 500,
            menubar: false,
            plugins: [
              'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
              'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
              'insertdatetime', 'media', 'table', 'code', 'help', 'wordcount'
            ],
            toolbar: 'undo redo | formatselect | ' +
              'bold italic backcolor | alignleft aligncenter ' +
              'alignright alignjustify | bullist numlist outdent indent | ' +
              'removeformat | help',
            content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px }'
          }}
        />
      </div>
      
      <div className="story-actions">
        <button 
          className="primary-button" 
          onClick={saveStory} 
          disabled={isSaving || saveStatus === 'saved'}
        >
          {isSaving ? 'Saving...' : (storyId ? 'Save Changes' : 'Save Story')}
        </button>
        
        <button 
          className="secondary-button" 
          onClick={getAISuggestions}
        >
          Get AI Feedback
        </button>
      </div>
      
      {showAISuggestions && (
        <AISuggestionPanel 
          suggestions={aiSuggestions} 
          onClose={() => setShowAISuggestions(false)} 
        />
      )}
    </div>
  );
};

export default StoryInterface;
