# 📖 StoryScribe: AI-Assisted Autobiographical Writing

> Transform your memories into stories with AI-powered writing prompts and a beautiful, intuitive interface.

[![Tests](https://img.shields.io/badge/tests-14%2F14%20passing-brightgreen)](./scripts/test-integration.sh)
[![Status](https://img.shields.io/badge/status-ready%20for%20deployment-blue)](./CURRENT_STATE.md)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

StoryScribe helps writers capture their personal stories through AI-generated writing prompts, beautiful UI, and seamless story management. Perfect for memoir writers, personal historians, and anyone who wants to preserve their life stories.

Access the App here: https://ambitious-cliff-0afea2203.3.azurestaticapps.net/  

## ✨ Features

- ✅ **AI-Powered Writing Prompts** - Get inspiring prompts (static or Azure OpenAI)
- ✅ **Beautiful UI** - Modern, gradient design with smooth interactions
- ✅ **Story Management** - Create, save, and view your stories
- ✅ **Guest Mode** - Start writing immediately, no account needed
- ✅ **Mobile Responsive** - Write on any device
- ✅ **User Isolation** - Your stories stay private to you
- ⚙️ **Azure Ready** - Easy deployment to Azure cloud

## 🚀 Quick Start

### Option 1: One-Command Start (Recommended)

```bash
git clone https://github.com/codess-aus/story-scribe.git
cd story-scribe
./scripts/start-dev.sh
```

Open your browser:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Manual Start

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev -- --host
```

## 🧪 Run Tests

```bash
# Automated integration tests
./scripts/test-integration.sh
```

**Current Test Status**: ✅ 14/14 tests passing

## 📁 Project Structure

```
story-scribe/
├── backend/                  # FastAPI REST API
│   ├── main.py              # API endpoints & AI integration
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Configuration (from .env.example)
├── frontend/                # React + Vite app
│   ├── src/
│   │   ├── App.jsx          # Main UI component
│   │   └── App.css          # Beautiful styling
│   └── package.json         # Node dependencies
├── functions/               # Azure Functions (optional)
│   └── generate_prompt/     # AI prompt generation
├── scripts/
│   ├── start-dev.sh         # Start all servers
│   └── test-integration.sh  # Run integration tests
└── docs/
    ├── GETTING_STARTED.md   # Detailed setup guide
    ├── TESTING_GUIDE.md     # Comprehensive testing
    ├── PRE_DEPLOYMENT_CHECKLIST.md  # Deployment guide
    ├── architecture.md      # System architecture
    └── CURRENT_STATE.md     # Current status summary
```  

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React + Vite | Fast, modern UI |
| **Backend** | FastAPI | RESTful API |
| **AI** | Azure OpenAI | Prompt generation |
| **Storage** | In-memory → Cosmos DB | Story persistence |
| **Auth** | Guest mode → Azure AD B2C | User management |
| **Deployment** | Azure App Service | Cloud hosting |
| **CI/CD** | GitHub Actions | Automation |

## 🤖 AI Integration

### Current Setup (Works Out of the Box)
- Static fallback prompts for 4 genres
- No Azure account required
- Great for development and testing

### Enhanced Setup (Optional)
1. Create Azure OpenAI resource
2. Deploy `gpt-4o-mini` model
3. Update `backend/.env`:
   ```bash
   OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com
   OPENAI_DEPLOYMENT=gpt-4o-mini
   OPENAI_API_KEY=your-key-here
   ```
4. Restart backend - AI prompts work automatically!

**Prompt Response Example:**
```json
{
  "prompt": "Write about a moment from your childhood...",
  "genre": "memoir",
  "source": "azure_openai",  // or "static_fallback"
  "model": "gpt-4o-mini"
}
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [CURRENT_STATE.md](./CURRENT_STATE.md) | Current status & features |
| [GETTING_STARTED.md](./docs/GETTING_STARTED.md) | Detailed setup guide |
| [TESTING_GUIDE.md](./docs/TESTING_GUIDE.md) | How to test everything |
| [PRE_DEPLOYMENT_CHECKLIST.md](./docs/PRE_DEPLOYMENT_CHECKLIST.md) | Deploy to Azure |
| [architecture.md](./docs/architecture.md) | System design |

## 🎯 Usage

### Create Your First Story

1. **Get Inspired**: Click "Get Writing Prompt"
2. **Write**: Enter your title and story content
3. **Save**: Click "Save Story"
4. **View**: See your stories displayed below

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get writing prompt
curl http://localhost:8000/prompt?genre=memoir

# Create story
curl -X POST http://localhost:8000/stories \
  -H "Content-Type: application/json" \
  -H "X-User-Id: guest_123" \
  -d '{"title":"My Story","content":"Once upon a time..."}'

# List stories
curl http://localhost:8000/stories \
  -H "X-User-Id: guest_123"
```

Interactive API documentation: http://localhost:8000/docs

## 🚀 Deployment

### Prerequisites
- Azure subscription
- GitHub account
- Azure CLI installed

### Deploy Steps

1. **Review Checklist**:
   ```bash
   cat docs/PRE_DEPLOYMENT_CHECKLIST.md
   ```

2. **Run Tests**:
   ```bash
   ./scripts/test-integration.sh
   ```

3. **Create Azure Resources** (see checklist)

4. **Deploy**:
   ```bash
   # Option A: Azure CLI
   az webapp up --name storyscribe-app --resource-group storyscribe-rg
   
   # Option B: GitHub Actions (push triggers deployment)
   git push origin main
   ```

5. **Verify**:
   ```bash
   curl https://storyscribe-app.azurewebsites.net/health
   ```

## 💰 Cost Estimate (Azure)

| Service | Tier | Monthly |
|---------|------|---------|
| App Service | B1 Basic | ~$13 |
| Azure OpenAI | Pay-as-you-go | ~$5-20 |
| Cosmos DB | Serverless | ~$0-10 |
| **Total** | | **~$18-43** |

*Free tier available for testing.*

## 🔒 Security & Privacy

- ✅ No secrets in code (`.env` configuration)
- ✅ User data isolation (stories per user)
- ✅ CORS protection
- ✅ Input validation
- ✅ Guest mode (no personal data required)
- 🔜 Azure Key Vault for production secrets
- 🔜 Azure AD B2C authentication
- 🔜 Content Safety moderation

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `./scripts/test-integration.sh`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure App Service](https://learn.microsoft.com/azure/app-service/)

## 💬 Support

- 📖 Documentation: Check the `docs/` folder
- 🐛 Issues: [GitHub Issues](https://github.com/codess-aus/story-scribe/issues)
- 💡 Discussions: [GitHub Discussions](https://github.com/codess-aus/story-scribe/discussions)

## 🌟 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Vite](https://vitejs.dev/) - Build tool
- [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service) - AI capabilities

---

**📝 Start writing your story today!** 🚀
