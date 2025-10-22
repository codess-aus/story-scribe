# StoryScribe: AI-Assisted Writing Journey

StoryScribe is an innovative application that helps writers transform their thoughts and memories into published books through AI-assisted prompting, organization, and refinement.

story-scribe/  
├── .github/workflows/        # GitHub Actions CI/CD workflows  
├── backend/                  # Python FastAPI or Node.js Express backend  
│   ├── api/                  # API endpoints  
│   ├── ai/                   # AI service integrations  
│   ├── db/                   # Database models and migrations  
│   └── security/             # Auth and security features  
├── frontend/                 # React or Vue.js frontend  
│   ├── public/               # Static assets  
│   └── src/                  # Frontend source code  
├── infrastructure/           # Azure infrastructure as code (Terraform/ARM templates)  
│   ├── app-services/  
│   └── ai-services/  
├── docs/                     # Project documentation  
└── README.md                 # Project overview  

## Features

- **AI-Powered Writing Prompts**: Dynamic prompts that adapt to your writing style and history
- **Progressive Story Development**: Guides writers from initial ideas to complete narratives
- **Genre and Title Suggestions**: AI analysis to help identify the best fit for your content
- **Content Moderation**: Ensures all content meets ethical and safety standards
- **Secure and Private**: End-to-end encryption and robust privacy controls
- **Book Development Tools**: Assistance with structuring, editing, and preparing for publication

## Technology Stack

- **Frontend**: React with TypeScript
- **Backend**: Python FastAPI
- **AI Services**: Azure OpenAI Service, Azure AI Content Safety
- **Database**: Azure Cosmos DB
- **Authentication**: Azure Active Directory B2C
- **Infrastructure**: Azure App Service, Azure Functions, Azure Key Vault

## Getting Started

### Prerequisites

- Node.js 20.x
- Python 3.11+
- Azure subscription
- OpenAI API access

### Local Development

1. Clone this repository
2. Set up environment variables (see `.env.example`)
3. Install dependencies:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

4. Start the development servers:

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd ../frontend
npm run dev
```

## Responsible AI

StoryScribe is built with responsible AI principles at its core:

- Content safety filters for both user input and AI outputs
- Transparency in AI-generated suggestions
- User control over data usage and privacy
- Regular fairness and bias assessments
```

## Security and Privacy

All user stories are encrypted at rest and in transit. Users maintain full control over their content and can export or delete their data at any time.
