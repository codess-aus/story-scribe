# Azure Permissions Setup Guide

## 🚨 Current Issue: 403 Deployment Error

Your GitHub Actions workflow is failing with a **403 Forbidden** error when trying to deploy to Azure Functions because the service principal lacks permissions to upload to the storage account.

## 🎯 Solution: Manual Permission Assignment

Since the automated role assignment in the workflow requires elevated permissions, you need to **manually assign the role in Azure Portal**.

---

## 📋 Step-by-Step Instructions

### Step 1: Identify Your Service Principal

Your GitHub Actions uses federated credentials with these secrets:
- `AZURE_CLIENT_ID` - This is your service principal's Application (client) ID
- `AZURE_TENANT_ID` - Your Azure AD tenant ID
- `AZURE_SUBSCRIPTION_ID` - Your Azure subscription ID

### Step 2: Find Your Storage Account

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to **Resource Groups** → **StoryScribe-RG**
3. Look for a storage account - it will be named something like:
   - `storyscribefuncXXXX` (where XXXX is random characters)
   - Or any storage account in this resource group

### Step 3: Assign Storage Blob Data Contributor Role

1. **Open the storage account** from Step 2
2. Click **Access Control (IAM)** in the left menu
3. Click **+ Add** → **Add role assignment**
4. On the **Role** tab:
   - Search for: `Storage Blob Data Contributor`
   - Select it and click **Next**
5. On the **Members** tab:
   - Select **User, group, or service principal**
   - Click **+ Select members**
   - In the search box, paste your `AZURE_CLIENT_ID` value (from GitHub secrets)
   - Or search for your app registration name (likely "storyscribe" or similar)
   - Select it and click **Select**
   - Click **Next**
6. On the **Review + assign** tab:
   - Click **Review + assign** to complete

### Step 4: Verify the Assignment

1. Still in **Access Control (IAM)**
2. Click the **Role assignments** tab
3. Search for your service principal
4. Confirm it has **Storage Blob Data Contributor** role

---

## 🔄 Alternative: Use Azure CLI

If you prefer command-line, you can run this locally (requires Azure CLI and Owner/UAA role):

```bash
# Login to Azure
az login

# Set variables (replace with your actual values)
RESOURCE_GROUP="StoryScribe-RG"
CLIENT_ID="<your-AZURE_CLIENT_ID-from-github-secrets>"
SUBSCRIPTION_ID="<your-AZURE_SUBSCRIPTION_ID-from-github-secrets>"

# Find the storage account
STORAGE_ACCOUNT=$(az storage account list \
  --resource-group $RESOURCE_GROUP \
  --query "[0].name" -o tsv)

echo "Storage Account: $STORAGE_ACCOUNT"

# Assign the role
az role assignment create \
  --assignee $CLIENT_ID \
  --role "Storage Blob Data Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT"

echo "✅ Role assigned successfully!"
```

---

## 🎓 Understanding the Roles

| Role | What It Does | Why We Need It |
|------|-------------|----------------|
| **Storage Blob Data Contributor** | Upload, download, delete blobs | Function App deployment uploads ZIP to blob storage |
| **Contributor** (on Function App) | Manage app settings, deploy code | Already assigned (deployment works) |
| **Cognitive Services OpenAI User** | Call OpenAI APIs with managed identity | Already assigned (tests pass) |

---

## ✅ After Assignment

Once you've assigned the role:

1. **Wait 5 minutes** for Azure to propagate the permission changes
2. **Re-run the GitHub Actions workflow**:
   - Go to `https://github.com/codess-aus/story-scribe/actions`
   - Click on the latest failed run
   - Click **Re-run all jobs**

The deployment should now succeed! 🎉

---

## 🔍 Troubleshooting

### "I can't find my service principal"

Your service principal might be named differently. Try searching for:
- The Application (client) ID directly (from `AZURE_CLIENT_ID` secret)
- "GitHub" (if you named it during setup)
- Check Azure Portal → Azure Active Directory → App registrations → All applications

### "I don't have permission to assign roles"

You need one of these roles on the storage account or resource group:
- **Owner**
- **User Access Administrator**

If you don't have these, contact your Azure subscription administrator.

### "Role assignment worked but deployment still fails"

- Wait 5-10 minutes for propagation
- Verify the service principal has these roles:
  - Storage Blob Data Contributor (on storage account)
  - Contributor (on Function App)
  - Cognitive Services OpenAI User (on OpenAI resource)

---

## 📝 Why Automated Assignment Doesn't Work

The workflow tries to assign roles automatically, but this requires the service principal to have **User Access Administrator** or **Owner** role, which creates a security risk. Microsoft recommends:

✅ **Best Practice**: Manually assign minimum required permissions
❌ **Not Recommended**: Give service principal permission to assign roles

---

## 🎯 Next Steps

1. ✅ Assign the Storage Blob Data Contributor role (follow steps above)
2. ✅ Wait 5 minutes for propagation
3. ✅ Re-run the GitHub Actions workflow
4. ✅ Verify deployment succeeds

Need help? Check the [Azure RBAC documentation](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal).
