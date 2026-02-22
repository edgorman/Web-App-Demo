# Quick Deployment Guide

This guide walks you through deploying the Google Identity Platform authentication system.

## Prerequisites Checklist

- [ ] GCP account with billing enabled
- [ ] Terraform installed (v1.0+)
- [ ] Google Cloud SDK (gcloud CLI) installed
- [ ] Docker installed (for building container images)

## Step-by-Step Deployment

### 1. Create OAuth 2.0 Credentials (5 minutes)

1. Go to [GCP Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Select your project (or create a new one)
3. Click **"Create Credentials"** → **"OAuth client ID"**
4. If prompted, configure the OAuth consent screen:
   - User Type: External (for testing) or Internal (for organization)
   - App name: "Web App Demo"
   - User support email: your email
   - Developer contact: your email
5. For the OAuth client:
   - Application type: **Web application**
   - Name: "Web App Demo Frontend"
   - Authorized JavaScript origins:
     - `http://localhost:8080`
   - Authorized redirect URIs:
     - `http://localhost:8080`
6. Click **Create** and save:
   - **Client ID** (e.g., `123456.apps.googleusercontent.com`)
   - **Client Secret** (e.g., `GOCSPX-...`)

### 2. Configure Terraform Variables (2 minutes)

```bash
cd infrastructure/config/dev
cp ../terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
project_id = "your-gcp-project-id"  # Change this!
region     = "europe-west1"

# OAuth Configuration - Replace with values from step 1
google_oauth_client_id     = "123456.apps.googleusercontent.com"
google_oauth_client_secret = "GOCSPX-your-secret-here"

# Keep other defaults
frontend_min_instances = 0
backend_min_instances  = 0
```

### 3. Deploy Infrastructure with Terraform (10 minutes)

```bash
# Initialize Terraform
cd infrastructure/env
make switch dev
terraform init

# Review the plan
terraform plan

# Deploy (this will take 5-10 minutes)
terraform apply
# Type 'yes' when prompted

# Save the outputs
terraform output
```

**Important**: Save these outputs:
- `frontend_service_url` - You'll need this for step 4
- `backend_service_url` - Backend API endpoint

### 4. Update OAuth Redirect URIs (2 minutes)

After deployment, you need to update your OAuth client:

1. Go back to [GCP Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Click on your OAuth client ("Web App Demo Frontend")
3. Add the frontend Cloud Run URL to:
   - **Authorized JavaScript origins**: 
     - `https://frontend-abc123.run.app` (your actual URL)
   - **Authorized redirect URIs**:
     - `https://frontend-abc123.run.app` (your actual URL)
4. Click **Save**

### 5. Get Web API Key (1 minute)

1. Go to [Identity Platform Settings](https://console.cloud.google.com/customer-identity/settings)
2. Under "Application setup details", find the **Web API Key**
3. Copy this key (it's safe to expose publicly)

### 6. Build and Deploy Frontend (10 minutes)

#### Option A: Quick Test with Placeholder Image

The Terraform deployment already created the Cloud Run service with a placeholder "Hello World" image. To test the infrastructure:

```bash
# Just visit your frontend URL
echo "Visit: $(terraform output -raw frontend_service_url)"
```

#### Option B: Deploy Custom OAuth Frontend

Build and push the Docker image:

```bash
# Configure Docker for GCP
gcloud auth configure-docker

# Build the image
cd services/frontend
PROJECT_ID="your-gcp-project-id"
docker build -f Dockerfile.oauth -t gcr.io/$PROJECT_ID/frontend:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/frontend:latest

# Update the Cloud Run service
gcloud run deploy frontend \
  --image gcr.io/$PROJECT_ID/frontend:latest \
  --region europe-west1 \
  --project $PROJECT_ID
```

**Before deploying**, edit `oauth-login.html` with your values:

```javascript
const CONFIG = {
    projectId: 'your-gcp-project-id',
    apiKey: 'AIza...your-web-api-key',  // From step 5
    clientId: '123456.apps.googleusercontent.com',  // From step 1
    redirectUri: window.location.origin + window.location.pathname,
    // ... rest is fine as-is
};
```

### 7. Test the Application (2 minutes)

1. Visit your frontend URL: `https://frontend-abc123.run.app`
2. Click **"Sign in with Google"**
3. Complete the Google OAuth flow
4. You should see your email and name displayed!

## Local Testing (Optional)

Test the frontend locally before deploying:

```bash
cd services/frontend

# Edit oauth-login.html with your credentials (steps 1 and 5)

# Start a local server
python3 -m http.server 8080

# Visit http://localhost:8080/oauth-login.html
```

## Verification Checklist

After deployment, verify:

- [ ] Frontend Cloud Run service is running
- [ ] Backend Cloud Run service is running
- [ ] Identity Platform is enabled
- [ ] Google OAuth provider is configured
- [ ] OAuth redirect URIs include Cloud Run URL
- [ ] Frontend displays login button
- [ ] Login redirects to Google
- [ ] After login, user info is displayed
- [ ] JWT token is stored in localStorage

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Solution**: The redirect URI in your OAuth config doesn't match. Ensure:
1. In GCP Console, you added your Cloud Run URL to authorized redirect URIs
2. The URL matches exactly (no trailing slash differences)

### Error: "Access blocked: This app's request is invalid"

**Solution**: You need to configure the OAuth consent screen:
1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Fill in required fields
3. Add your email as a test user (if using External user type)

### Frontend shows "YOUR_PROJECT_ID"

**Solution**: You forgot to update the CONFIG in oauth-login.html
1. Edit `services/frontend/oauth-login.html`
2. Replace placeholder values with your actual credentials
3. Rebuild and redeploy the Docker image

### "Failed to decode JWT token"

**Solution**: The token might be corrupted
1. Clear localStorage: `localStorage.clear()` in browser console
2. Try logging in again

### Cloud Run service won't deploy

**Solution**: Check quotas and permissions
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable identitytoolkit.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Check quotas
gcloud compute project-info describe --project=your-project-id
```

## Cost Monitoring

Monitor your costs:

1. Go to [Billing Console](https://console.cloud.google.com/billing)
2. Set up budget alerts:
   - Budget: $10/month
   - Alert at: 50%, 90%, 100%

Expected costs:
- Cloud Run (with scale-to-zero): ~$0
- Identity Platform (< 50k MAU): $0
- **Total**: < $1/month for light usage

## Next Steps

Now that your app is deployed:

1. **Customize the UI**: Edit `oauth-login.html` to match your branding
2. **Add Features**: Implement additional pages, protected routes
3. **Monitor**: Set up Cloud Monitoring and Logging
4. **Production**: When ready, deploy to prod environment:
   ```bash
   cd infrastructure/env
   make switch prod
   terraform apply
   ```

## Cleanup

To delete all resources and stop billing:

```bash
cd infrastructure/env
terraform destroy
# Type 'yes' when prompted
```

This will delete:
- Cloud Run services (frontend and backend)
- Identity Platform configuration
- All deployed infrastructure

**Note**: This does NOT delete:
- The GCP project
- OAuth credentials
- Terraform state in GCS

## Support

For help:
- Check the [main README](../../README.md)
- Review [OAUTH_SETUP.md](../../services/frontend/OAUTH_SETUP.md)
- Review [IDENTITY_PLATFORM.md](../../infrastructure/env/IDENTITY_PLATFORM.md)
- Open an issue on GitHub

---

**Estimated Total Time**: 30-40 minutes for first-time deployment

Good luck! 🚀
