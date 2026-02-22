# Google Identity Platform OAuth Setup

This document provides instructions for setting up Google Identity Platform with OAuth2/OIDC redirect flow (without Firebase SDK).

## Prerequisites

1. A GCP project with Identity Platform enabled
2. Google OAuth 2.0 credentials configured
3. Terraform installed (for infrastructure deployment)

## Infrastructure Setup

### Step 1: Configure OAuth Credentials in GCP Console

Before running Terraform, you need to create OAuth 2.0 credentials:

1. Go to [GCP Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Configure:
   - **Name**: "Web App Demo Frontend"
   - **Authorized JavaScript origins**: 
     - `http://localhost:8080` (for local testing)
     - Your Cloud Run service URL (add after deployment)
   - **Authorized redirect URIs**:
     - `http://localhost:8080` (for local testing)
     - Your Cloud Run service URL (add after deployment)
5. Save the **Client ID** and **Client Secret**

### Step 2: Get the Web API Key

After enabling Identity Platform:

1. Go to [Identity Platform](https://console.cloud.google.com/customer-identity/providers)
2. The Web API Key will be displayed in the settings
3. Save this key for frontend configuration

### Step 3: Configure Terraform Variables

Create or update `infrastructure/config/dev/terraform.tfvars`:

```hcl
project_id = "your-project-id"
region     = "europe-west1"

# OAuth Configuration
google_oauth_client_id     = "YOUR_CLIENT_ID.apps.googleusercontent.com"
google_oauth_client_secret = "YOUR_CLIENT_SECRET"

# Authorized domains for OAuth redirects
identity_platform_authorized_domains = [
  "localhost",
  "your-cloud-run-domain.run.app"
]
```

### Step 4: Deploy Infrastructure

```bash
cd infrastructure/env
make switch dev
terraform init
terraform plan
terraform apply
```

This will:
- Enable the Identity Toolkit API
- Configure Identity Platform with Google Login
- Deploy frontend and backend Cloud Run services

### Step 5: Update OAuth Redirect URIs

After deployment:
1. Note the frontend Cloud Run URL from Terraform outputs
2. Go back to GCP Console → Credentials
3. Edit your OAuth client ID
4. Add the Cloud Run URL to:
   - Authorized JavaScript origins: `https://your-service-xyz.run.app`
   - Authorized redirect URIs: `https://your-service-xyz.run.app`

## Frontend Configuration

### Option 1: Using the Standalone HTML File (Minimal)

Edit `services/frontend/oauth-login.html` and update the CONFIG object:

```javascript
const CONFIG = {
    projectId: 'your-project-id',
    apiKey: 'your-web-api-key',
    clientId: 'YOUR_CLIENT_ID.apps.googleusercontent.com',
    redirectUri: window.location.origin + window.location.pathname,
    authEndpoint: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenEndpoint: 'https://oauth2.googleapis.com/token',
};
```

### Option 2: Using Environment Variables (Recommended)

For the build process, you can use environment variables. Create a `.env` file:

```env
VITE_GCP_PROJECT_ID=your-project-id
VITE_IDENTITY_API_KEY=your-web-api-key
VITE_OAUTH_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
```

## Local Testing

1. Serve the HTML file locally:
   ```bash
   cd services/frontend
   python3 -m http.server 8080
   ```

2. Open http://localhost:8080/oauth-login.html
3. Click "Sign in with Google"
4. Complete the OAuth flow
5. You should see your email and name displayed

## How It Works

### Pure OAuth2/OIDC Flow (No Firebase SDK)

1. **Check JWT in localStorage**: On page load, checks for existing token
2. **Redirect to Google**: If no token, button redirects to Google OAuth endpoint
3. **OAuth Callback**: Google redirects back with `id_token` in URL fragment
4. **Parse Token**: JavaScript parses the token from URL hash
5. **Decode JWT**: Custom function decodes JWT without external libraries
6. **Display User Info**: Shows email and name from JWT payload
7. **Token Storage**: JWT stored in localStorage as single source of truth

### Security Features

- **State parameter**: CSRF protection using random state
- **Nonce**: Additional security for token replay attacks
- **Token expiry check**: Validates token hasn't expired
- **No backend required**: Completely client-side authentication
- **No database**: JWT is the only source of truth

## Architecture

```
┌─────────────┐
│   Browser   │
│             │
│ localStorage│ ← JWT stored here (only source of truth)
└──────┬──────┘
       │
       │ 1. Redirect to Google OAuth
       ▼
┌─────────────────────┐
│  Google OAuth       │
│  accounts.google.com│
└──────┬──────────────┘
       │
       │ 2. Return with id_token
       ▼
┌─────────────────────┐
│   Cloud Run         │
│   (Frontend)        │
│   - Static HTML/JS  │
│   - No backend      │
│   - No database     │
└─────────────────────┘
```

## Cost Optimization

- **Cloud Run scaling to 0**: No cost when not in use
- **No database**: No Cloud SQL or Firestore costs
- **No backend API**: Pure static frontend
- **Minimal compute**: Only pays for request time

## Troubleshooting

### "Error: redirect_uri_mismatch"
- Ensure the redirect URI in your code matches exactly what's configured in GCP Console
- Include both `http://localhost:8080` and your Cloud Run URL

### "Invalid JWT format"
- Check that the token is being properly extracted from the URL fragment
- Verify the token hasn't been truncated

### "Token expired"
- JWT tokens typically expire after 1 hour
- Click "Sign in with Google" again to get a new token

## Next Steps

1. Customize the UI to match your branding
2. Add additional OAuth scopes if needed
3. Implement token refresh logic
4. Add monitoring and error tracking
