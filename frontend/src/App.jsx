/**
 * App.jsx
 * WHAT: Beautiful, simple UI to create/list stories and fetch AI prompts.
 * WHY: Demonstrate end-to-end interaction with clean design.
 * HOW: Guest user mode with localStorage, will add real auth later.
 */

import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function randomUserId() {
  if (typeof window === 'undefined') return 'guest_default';
  
  let id = window.localStorage.getItem('storyscribe_user');
  if (!id) {
    id = 'guest_' + Math.random().toString(36).slice(2, 10);
    window.localStorage.setItem('storyscribe_user', id);
  }
  return id;
}

const userId = randomUserId();

// Main app component
const App = () => {
  const [stories, setStories] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [prompt, setPrompt] = useState('');
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [saving, setSaving] = useState(false);

  async function loadStories() {
    try {
      const res = await fetch(`${API_BASE}/stories`, {
        headers: { 'X-User-Id': userId }
      });
      if (res.ok) {
        setStories(await res.json());
      }
    } catch (error) {
      console.error('Failed to load stories:', error);
    }
  }

  async function createStory() {
    if (!title.trim() || !content.trim()) return;
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/stories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId
        },
        body: JSON.stringify({ title, content })
      });
      if (res.ok) {
        const doc = await res.json();
        setStories(prev => [...prev, doc]);
        setTitle('');
        setContent('');
      }
    } catch (error) {
      console.error('Failed to create story:', error);
    } finally {
      setSaving(false);
    }
  }

  async function fetchPrompt() {
    setLoadingPrompt(true);
    try {
      const res = await fetch(`${API_BASE}/prompt?genre=memoir`);
      const data = await res.json();
      setPrompt(data.prompt || 'No prompt available');
    } catch (error) {
      console.error('Failed to fetch prompt:', error);
      setPrompt('Unable to fetch prompt. Please try again.');
    } finally {
      setLoadingPrompt(false);
    }
  }

  useEffect(() => {
    loadStories();
  }, []);

  return (
    <div className='app'>
      <header className='app-header'>
        <h1>✍️ StoryScribe</h1>
        <p>Your AI-powered writing companion</p>
        <div className='user-badge'>Guest: {userId}</div>
      </header>

      <div className="card">
        <h2>✨ Get Inspired</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
          Let AI help you find your next story to write
        </p>
        <button 
          className="btn-primary" 
          disabled={loadingPrompt} 
          onClick={fetchPrompt}
        >
          {loadingPrompt ? 'Generating...' : 'Get Writing Prompt'}
        </button>
        {prompt && (
          <div className="prompt-display">
            <p>{prompt}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h2>📝 Write Your Story</h2>
        <div className="input-group">
          <label htmlFor="story-title">Title</label>
          <input
            id="story-title"
            type="text"
            placeholder="Give your story a title..."
            value={title}
            onChange={e => setTitle(e.target.value)}
          />
        </div>
        <div className="input-group">
          <label htmlFor="story-content">Your Story</label>
          <textarea
            id="story-content"
            placeholder="Start writing your story here..."
            value={content}
            onChange={e => setContent(e.target.value)}
          />
        </div>
        <button 
          className="btn-primary" 
          onClick={createStory}
          disabled={!title.trim() || !content.trim() || saving}
        >
          {saving ? 'Saving...' : 'Save Story'}
        </button>
      </div>

      <div className="card">
        <h2>📚 Your Stories</h2>
        {stories.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📖</div>
            <p>No stories yet. Start writing to see them here!</p>
          </div>
        ) : (
          <ul className="stories-list">
            {stories.map(s => (
              <li key={s.id}>
                <div className="story-title">{s.title}</div>
                <div className="story-preview">
                  {s.content.slice(0, 120)}
                  {s.content.length > 120 ? '...' : ''}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

// Add displayName for React DevTools
App.displayName = 'App';

export default App;