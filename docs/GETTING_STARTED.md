# 🚀 StoryScribe - Quick Start Guide

## Architecture Overview

StoryScribe follows a **simple, demo-friendly architecture**:

- **Frontend**: React (Vite) - Beautiful, responsive UI
- **Backend**: FastAPI - Story CRUD + health endpoint
- **AI**: Azure Function with OpenAI - Prompt generation (future)
- **Auth**: Guest mode (demo) - No authentication needed
- **Storage**: In-memory (demo) - Will upgrade to Cosmos DB

## Quick Start

### Option 1: Use the Start Script (Recommended)

```bash
./scripts/start-dev.sh
```

This will:
1. Set up Python virtual environment
2. Install all dependencies
3. Start backend (port 8000)
4. Start frontend (port 5173)

### Option 2: Manual Start

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Access the App

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

## Features Available Now

✅ **Create Stories** - Write and save your stories  
✅ **View Stories** - See all your saved stories  
✅ **Get Prompts** - Request AI-generated writing prompts  
✅ **Beautiful UI** - Modern, clean design with gradients  
✅ **Guest Mode** - No login required, uses localStorage  

## Project Structure

```
story-scribe/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints (stories, prompt, health)
│   ├── ai/              # Content safety module (future)
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.jsx     # Main app component
│   │   ├── App.css     # Beautiful styling
│   │   └── main.jsx    # Entry point
│   ├── index.html      # HTML template
│   ├── vite.config.js  # Vite configuration
│   └── package.json    # Node dependencies
├── functions/           # Azure Functions (future)
│   └── generate_prompt/ # AI prompt generation
└── scripts/
    └── start-dev.sh    # Convenience start script
```

## Development Tips

### Backend Development
- API auto-reloads on file changes
- View API docs at `/docs` endpoint
- Stories stored in memory (reset on restart)
- Each user identified by localStorage ID

### Frontend Development
- Hot module reload enabled
- CSS follows modern design patterns
- Mobile-responsive layout
- Accessible color contrast

### Testing Endpoints

**Get Writing Prompt:**
```bash
curl http://localhost:8000/prompt?genre=memoir
```

**Create Story:**
```bash
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "X-User-Id: guest_abc123" \
  -d '{"title":"My Story","content":"Once upon a time..."}'
```

**List Stories:**
```bash
curl http://localhost:8000/stories \
  -H "X-User-Id: guest_abc123"
```

## Future Enhancements

🔜 **Azure OpenAI Integration** - Real AI-powered prompts  
🔜 **Cosmos DB** - Persistent storage  
🔜 **Content Safety** - AI moderation  
🔜 **Azure AD B2C** - Real authentication  
🔜 **Deployment** - Azure App Service + Functions  

## Environment Variables

Copy `.env.example` to `.env` in each directory and configure:

**Backend (.env):**
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint (future)
- `OPENAI_DEPLOYMENT` - Model deployment name (future)
- `COSMOS_ENDPOINT` - Cosmos DB endpoint (future)

**Frontend (.env):**
- `VITE_API_BASE_URL` - Backend URL (default: http://localhost:8000)

## Troubleshooting

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

**Dependencies issues:**
```bash
# Backend
cd backend && rm -rf venv && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Frontend
cd frontend && rm -rf node_modules && npm install
```

## Architecture Alignment

This setup follows `docs/architecture.md`:
- ✅ Guest user mode (no auth)
- ✅ FastAPI backend with story CRUD
- ✅ In-memory storage (Cosmos DB ready)
- ✅ React frontend (Vite)
- ✅ Azure Function structure (ready for OpenAI)
- ✅ Simple and demo-friendly
- ✅ Beautiful, modern UI

## Contributing

Keep the architecture **simple** while adding functionality:
1. Maintain the guest user model
2. Keep UI clean and accessible
3. Prepare for future Azure integration
4. Document all changes

---

**Built with ❤️ for writers everywhere**
