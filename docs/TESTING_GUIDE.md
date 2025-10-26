# 🧪 StoryScribe Testing Guide

## Pre-Deployment Testing Checklist

This guide will help you test all functionality before deploying to Azure.

## 1. Local Environment Setup

### Step 1: Environment Variables

Create `.env` files from the example:

```bash
# Copy example to actual env file
cp .env.example backend/.env
cp .env.example frontend/.env
```

**Backend `.env`:**
```bash
# Azure OpenAI (for AI-powered prompts)
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
OPENAI_DEPLOYMENT=gpt-4o-mini
OPENAI_API_VERSION=2024-08-01-preview

# For local development, you can use API key or Azure Identity
# OPENAI_API_KEY=your-key-here  # OR use Azure DefaultAzureCredential

# Optional: Cosmos DB (for persistent storage)
COSMOS_ENDPOINT=https://YOUR-COSMOS.documents.azure.com:443/
COSMOS_KEY=your-key-here
COSMOS_DB=StoryScribeDB
COSMOS_CONTAINER=items
```

**Frontend `.env`:**
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Step 2: Install Dependencies

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

## 2. Start Services

### Option A: Use the convenience script
```bash
./scripts/start-dev.sh
```

### Option B: Manual start (for debugging)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev -- --host
```

## 3. Manual Testing Checklist

### ✅ Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok","mode":"no-auth"}
```

### ✅ API Documentation

Open in browser: http://localhost:8000/docs

You should see:
- Interactive Swagger UI
- All endpoints documented
- Try-it-out functionality

### ✅ Writing Prompt Generation

**Test 1: Basic prompt (static fallback)**
```bash
curl http://localhost:8000/prompt?genre=memoir
```

**Test 2: Different genres**
```bash
curl http://localhost:8000/prompt?genre=adventure
curl http://localhost:8000/prompt?genre=reflection
curl http://localhost:8000/prompt?genre=creative
```

Expected: Different prompts for each genre

**Test 3: AI-powered prompts (if Azure OpenAI configured)**
After integrating Azure OpenAI, prompts should be dynamically generated.

### ✅ Story CRUD Operations

**Test 1: Create a story**
```bash
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test_user_123" \
  -d '{
    "title": "My First Memory",
    "content": "I remember the first time I saw the ocean. The waves crashed against the shore, and I felt so small yet so alive."
  }'
```

Expected: Returns story with ID, timestamps

**Test 2: List stories**
```bash
curl http://localhost:8000/stories \
  -H "X-User-Id: test_user_123"
```

Expected: Returns array with the story you created

**Test 3: Create multiple stories**
```bash
# Story 2
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test_user_123" \
  -d '{
    "title": "A Lesson Learned",
    "content": "My grandmother taught me that kindness costs nothing but means everything."
  }'

# Story 3
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test_user_123" \
  -d '{
    "title": "The Journey",
    "content": "Every adventure begins with a single step into the unknown."
  }'
```

**Test 4: List all stories again**
```bash
curl http://localhost:8000/stories \
  -H "X-User-Id: test_user_123"
```

Expected: Returns array with all 3 stories

**Test 5: User isolation**
```bash
# Different user
curl http://localhost:8000/stories \
  -H "X-User-Id: different_user_456"
```

Expected: Returns empty array (stories are per-user)

### ✅ Frontend Testing

Open in browser: http://localhost:5173

**Visual Checks:**
- [ ] Beautiful gradient header displays
- [ ] "Get Writing Prompt" button is visible
- [ ] Story creation form is visible
- [ ] Responsive design works on different screen sizes

**Functional Tests:**

1. **Get Writing Prompt**
   - Click "Get Writing Prompt"
   - Button should show "Generating..."
   - Prompt should appear below button
   - Click again to get a different prompt

2. **Create Story**
   - Enter a title (e.g., "Test Story")
   - Enter content in textarea
   - Click "Save Story"
   - Button should show "Saving..."
   - Success message should appear
   - Form should clear
   - Story should appear in list below

3. **View Stories**
   - Created stories should display in cards
   - Each card shows title, content, and timestamp
   - Multiple stories should stack nicely

4. **User Persistence**
   - Open DevTools > Application > Local Storage
   - Check for `storyscribe_userId`
   - Refresh page
   - Stories should persist (same user ID)
   - Clear Local Storage
   - Refresh page
   - New user ID should be generated
   - Stories list should be empty

## 4. Error Handling Tests

### ✅ Missing Headers
```bash
# Should return 401
curl http://localhost:8000/stories
```

### ✅ Invalid JSON
```bash
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test_user_123" \
  -d 'invalid json'
```

### ✅ Missing Required Fields
```bash
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test_user_123" \
  -d '{"title": "No content field"}'
```

## 5. Performance Tests

### Load Test (Optional)

Install `wrk` or `ab` (Apache Bench):

```bash
# Test health endpoint
wrk -t2 -c10 -d10s http://localhost:8000/health

# Test prompt endpoint
wrk -t2 -c10 -d10s http://localhost:8000/prompt?genre=memoir
```

## 6. Azure OpenAI Integration Test

If you've configured Azure OpenAI:

```bash
# Should return AI-generated prompt
curl http://localhost:8000/prompt?genre=memoir
```

Check response for:
- Unique, creative prompt (not from hardcoded list)
- Appropriate length (~40 words)
- Relevant to the genre
- Well-formed, inspiring content

## 7. Browser Compatibility

Test in multiple browsers:
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

## 8. Mobile Responsiveness

Test on different screen sizes:
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

Use Chrome DevTools > Toggle Device Toolbar

## 9. Console Checks

### Backend Console
- [ ] No error messages
- [ ] Request logs show proper status codes
- [ ] Startup message indicates successful initialization

### Frontend Console (Browser DevTools)
- [ ] No error messages
- [ ] No CORS errors
- [ ] API calls succeed with 200 status
- [ ] No console warnings

## 10. Pre-Deployment Checklist

Before deploying to Azure:

- [ ] All environment variables documented
- [ ] Azure OpenAI integration tested (if enabled)
- [ ] Backend health check passes
- [ ] Frontend loads and displays correctly
- [ ] Story CRUD operations work
- [ ] Prompt generation works
- [ ] Error handling works gracefully
- [ ] No console errors
- [ ] Mobile-responsive design verified
- [ ] CORS configured for production domains
- [ ] Secrets are NOT in code (use .env)
- [ ] .gitignore includes .env files
- [ ] README.md is up to date

## 11. Integration Testing Script

Run the automated test script:

```bash
./scripts/test-integration.sh
```

This will test all API endpoints automatically.

## 12. Known Limitations (Demo Mode)

Current limitations to be aware of:
- ✅ Stories stored in memory (reset on restart)
- ✅ No authentication (guest mode)
- ✅ No persistence across server restarts
- ✅ Prompts may be static (if Azure OpenAI not configured)

These are by design for demo purposes and will be addressed in production deployment.

## Next Steps After Testing

Once all tests pass:

1. Review `docs/architecture.md`
2. Update Azure resources configuration
3. Set up GitHub Actions for CI/CD
4. Deploy to Azure App Service + Functions
5. Configure custom domain (optional)
6. Enable monitoring and logging

---

**Happy Testing! 🎉**
