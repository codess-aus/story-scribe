#!/bin/bash
# Deploy frontend to Azure Static Web Apps

set -e

echo "🚀 Deploying StoryScribe Frontend to Azure Static Web Apps"
echo "==========================================================="

# Variables
RESOURCE_GROUP="StoryScribe-RG"
LOCATION="swedencentral"
STATIC_WEB_APP_NAME="storyscribe-frontend"

# Check if Azure Static Web App already exists
if az staticwebapp show --name $STATIC_WEB_APP_NAME --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "✅ Static Web App already exists: $STATIC_WEB_APP_NAME"
else
    echo "📦 Creating Azure Static Web App..."
    az staticwebapp create \
        --name $STATIC_WEB_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Free
    echo "✅ Static Web App created: $STATIC_WEB_APP_NAME"
fi

# Build the frontend
echo "📦 Building frontend..."
cd "$(dirname "$0")/../frontend"
npm install
npm run build

# Get deployment token
echo "🔑 Getting deployment token..."
TOKEN=$(az staticwebapp secrets list \
    --name $STATIC_WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.apiKey" -o tsv)

# Deploy using SWA CLI (install if needed)
if ! command -v swa &> /dev/null; then
    echo "📦 Installing Azure Static Web Apps CLI..."
    npm install -g @azure/static-web-apps-cli
fi

echo "🚀 Deploying to Azure..."
swa deploy ./dist --deployment-token "$TOKEN" --env production

# Get the Static Web App URL
SWA_URL=$(az staticwebapp show \
    --name $STATIC_WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "defaultHostname" -o tsv)

echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo "Frontend URL: https://$SWA_URL"
echo "Backend URL: https://storyscribe-web-btbhgaduc3fubbhd.swedencentral-01.azurewebsites.net"
echo ""
echo "⚠️  Next Steps:"
echo "1. Update CORS in backend/main.py to allow: https://$SWA_URL"
echo "2. Test the application end-to-end"
echo "3. Configure custom domain (optional)"
