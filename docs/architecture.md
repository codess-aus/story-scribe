# Architecture Overview

## Current State (Demo)
- Frontend: React (Vite), guest user mode (no auth)
- Backend: FastAPI (story CRUD + health)
- Serverless: Azure Function (prompt generation)
- Persistence: In-memory (swap to Cosmos DB / `items` container with partition key `/userId`)
- AI: Azure OpenAI (prompt generation), Content Safety planned
- Secrets: To be stored in Azure Key Vault (future)
- CI/CD: GitHub Actions (build artifacts, future deploy steps)

## Component Interaction
1. User (guest) requests prompt → Azure Function calls OpenAI.
2. User creates story → FastAPI stores in memory (later Cosmos).
3. Frontend lists stories → Partition by `userId` (even in demo).

## Future Layers
- Auth: Azure AD B2C (replace guest ID)
- Moderation: Content Safety gating before returning AI text
- Semantic: Vector indexing for story similarity

## Interesting Fact
By deferring auth, iteration speed improves while still enforcing a data partition model. This prevents later “all data under single key” refactor pain.