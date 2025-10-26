# 🚀 Pre-Deployment Checklist

Complete this checklist before deploying StoryScribe to Azure.

## ✅ Phase 1: Local Setup & Testing

### Environment Setup
- [x] Backend `.env` file created from `.env.example`
- [ ] Azure OpenAI credentials added (optional for AI prompts)
- [ ] Cosmos DB credentials added (optional for persistent storage)
- [x] Frontend `.env` file configured
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] All frontend dependencies installed (`npm install`)

### Local Testing
- [x] Backend starts without errors (`uvicorn main:app --reload`)
- [x] Frontend starts without errors (`npm run dev`)
- [x] Health endpoint responds: `curl http://localhost:8000/health`
- [x] API documentation accessible: http://localhost:8000/docs
- [x] Frontend loads in browser: http://localhost:5173
- [x] Integration tests pass: `./scripts/test-integration.sh`

### Functional Testing
- [ ] **Get Writing Prompt** button works
- [ ] Prompts display correctly
- [ ] **Create Story** form works
- [ ] Stories save successfully
- [ ] Stories list displays correctly
- [ ] Multiple stories can be created
- [ ] User ID persists across page refreshes
- [ ] No console errors in browser DevTools
- [ ] Mobile responsive design works

## ✅ Phase 2: Azure Resources Setup

### Azure OpenAI (Optional but Recommended)
- [ ] Azure OpenAI resource created
- [ ] GPT-4o-mini model deployed
- [ ] Endpoint URL documented
- [ ] Deployment name documented
- [ ] API key secured or Managed Identity configured
- [ ] Test prompt generation works with Azure OpenAI

### Cosmos DB (Optional but Recommended)
- [ ] Cosmos DB account created
- [ ] Database `StoryScribeDB` created
- [ ] Container `items` created with partition key `/userId`
- [ ] Connection string secured
- [ ] Test connection works

### Content Safety (Future)
- [ ] Azure Content Safety resource created (optional)
- [ ] Endpoint and key documented

### App Service / Container Apps
- [ ] Azure App Service or Container App plan created
- [ ] Resource naming convention followed
- [ ] Region selected (same as OpenAI for low latency)

## ✅ Phase 3: Code Quality & Security

### Security
- [x] No secrets in code
- [x] `.env` files in `.gitignore`
- [x] `.env.example` provides template
- [ ] Azure Key Vault configured for production secrets
- [ ] Managed Identity configured (recommended over API keys)
- [x] CORS configured for production domains

### Code Quality
- [x] No console errors in backend
- [x] No console errors in frontend
- [x] API follows RESTful conventions
- [x] Error handling implemented
- [x] Input validation in place
- [x] Code commented appropriately

### Documentation
- [x] README.md up to date
- [x] Architecture documented
- [x] Getting Started guide complete
- [x] Testing guide available
- [x] API endpoints documented

## ✅ Phase 4: Deployment Configuration

### Infrastructure as Code
- [ ] Azure resources defined (Bicep/Terraform)
- [ ] Environment variables documented
- [ ] Deployment scripts ready
- [ ] GitHub Actions workflow configured

### CI/CD Pipeline
- [ ] GitHub Actions workflow created
- [ ] Build steps configured
- [ ] Test steps added
- [ ] Deployment steps configured
- [ ] Secrets configured in GitHub
- [ ] Service Principal created and added to GitHub Secrets

### Environment Configuration
- [ ] Production environment variables set
- [ ] CORS origins updated for production
- [ ] Frontend API_BASE_URL updated
- [ ] Azure app settings configured

## ✅ Phase 5: Deployment Testing

### Post-Deployment Verification
- [ ] Production health endpoint responds
- [ ] Production API documentation accessible
- [ ] Frontend loads on production URL
- [ ] Writing prompts generate correctly
- [ ] Story creation works in production
- [ ] Story listing works in production
- [ ] User isolation works in production
- [ ] No console errors in production
- [ ] HTTPS enforced
- [ ] Custom domain configured (optional)

### Performance Testing
- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms
- [ ] Prompt generation < 5 seconds
- [ ] No memory leaks
- [ ] Handles concurrent users

### Monitoring Setup
- [ ] Application Insights configured
- [ ] Logging enabled
- [ ] Error tracking active
- [ ] Performance metrics tracked
- [ ] Alerts configured for errors

## ✅ Phase 6: Final Checks

### User Experience
- [ ] All features work as expected
- [ ] UI is responsive on all devices
- [ ] No broken links
- [ ] Forms validate correctly
- [ ] Error messages are user-friendly
- [ ] Loading states display correctly

### Accessibility
- [ ] Color contrast meets WCAG standards
- [ ] Keyboard navigation works
- [ ] Screen reader friendly
- [ ] Alt text for images (if any)

### Legal & Compliance
- [ ] Privacy policy added (if collecting data)
- [ ] Terms of service added (if needed)
- [ ] Cookie consent (if tracking users)
- [ ] GDPR compliance (if targeting EU)

## 🎯 Deployment Steps

### Step 1: Prepare Azure Resources
```bash
# Create resource group
az group create --name storyscribe-rg --location eastus

# Create Azure OpenAI (optional)
az cognitiveservices account create \
  --name storyscribe-openai \
  --resource-group storyscribe-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Deploy model
az cognitiveservices account deployment create \
  --name storyscribe-openai \
  --resource-group storyscribe-rg \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 1 \
  --sku-name Standard
```

### Step 2: Deploy Application
```bash
# Option A: Using Azure CLI
az webapp up --name storyscribe-app --resource-group storyscribe-rg

# Option B: Using GitHub Actions
git push origin main  # Triggers automated deployment
```

### Step 3: Configure App Settings
```bash
# Set environment variables
az webapp config appsettings set \
  --name storyscribe-app \
  --resource-group storyscribe-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://storyscribe-openai.openai.azure.com" \
    OPENAI_DEPLOYMENT="gpt-4o-mini" \
    OPENAI_API_VERSION="2024-08-01-preview"
```

### Step 4: Verify Deployment
```bash
# Test production endpoint
curl https://storyscribe-app.azurewebsites.net/health
```

## 📊 Success Criteria

Deployment is successful when:

1. ✅ All endpoints respond with 200 OK
2. ✅ Frontend loads without errors
3. ✅ AI prompts generate successfully
4. ✅ Stories can be created and retrieved
5. ✅ No console errors or warnings
6. ✅ Performance meets requirements
7. ✅ Monitoring and logging active
8. ✅ HTTPS enabled and working

## 🆘 Rollback Plan

If deployment fails:

1. Check Application Insights logs
2. Review deployment logs in Azure Portal
3. Verify environment variables are set
4. Test each endpoint individually
5. Rollback to previous version if needed:
   ```bash
   az webapp deployment slot swap \
     --name storyscribe-app \
     --resource-group storyscribe-rg \
     --slot staging \
     --target-slot production
   ```

## 📞 Support Contacts

- **Azure Support**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- **GitHub Issues**: https://github.com/YOUR-ORG/story-scribe/issues
- **Documentation**: https://learn.microsoft.com/azure/

---

**Last Updated**: {{ date }}
**Version**: 1.0.0
