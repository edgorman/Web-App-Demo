# Web-App-Demo

A "dirt cheap" web application on GCP featuring:
- 🔐 Google Identity Platform (GCIP) authentication with pure OAuth2/OIDC (no Firebase SDK)
- ☁️ Cloud Run services that scale to zero for cost optimization
- 🚫 No database - JWT is the only source of truth
- 🔧 Infrastructure as Code with Terraform

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GCP Project                               │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Identity Platform (GCIP)                        │       │
│  │  - Google OAuth Provider                         │       │
│  │  - Pure OAuth2/OIDC Redirect Flow                │       │
│  │  - No Firebase SDK                               │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Cloud Run - Frontend Service                    │       │
│  │  - Nginx serving static HTML/JS                  │       │
│  │  - OAuth2 redirect flow                          │       │
│  │  - JWT decode (no external libraries)            │       │
│  │  - Scales to 0 (cost savings)                    │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Cloud Run - Backend Service                     │       │
│  │  - Scales to 0 (cost savings)                    │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 🔐 Authentication
- **Pure OAuth2/OIDC**: Direct Google OAuth flow without Firebase SDK
- **Client-side only**: No backend authentication required
- **JWT-based**: User identity stored in JWT token (localStorage)
- **No database**: JWT is the single source of truth
- **CSRF protection**: State parameter validates redirect authenticity

### 💰 Cost Optimization
- **Scale to zero**: Cloud Run services only charge when handling requests
- **No database costs**: No Cloud SQL, Firestore, or any database service
- **Minimal resources**: 512Mi RAM, 1 CPU - sufficient for static frontend
- **No Firebase SDK**: Smaller bundle size, faster load times

### 🏗️ Infrastructure
- **Terraform**: Complete infrastructure as code
- **Multi-environment**: Separate dev and prod configurations
- **CI/CD Ready**: GitHub Actions integration with Workload Identity
- **Security**: OAuth secrets managed as sensitive variables

## Quick Start

### Prerequisites

- GCP account with billing enabled
- Terraform installed
- Google OAuth 2.0 credentials

### 1. Create OAuth Credentials

1. Go to [GCP Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID (Web application)
3. Add authorized origins: `http://localhost:8080`
4. Add redirect URIs: `http://localhost:8080`
5. Save Client ID and Secret

### 2. Configure Terraform

```bash
cd infrastructure/config/dev
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

Required variables:
```hcl
project_id                 = "your-gcp-project"
google_oauth_client_id     = "YOUR_CLIENT_ID.apps.googleusercontent.com"
google_oauth_client_secret = "YOUR_CLIENT_SECRET"
```

### 3. Deploy Infrastructure

```bash
cd infrastructure/env
make switch dev
terraform init
terraform plan
terraform apply
```

### 4. Update Frontend Configuration

Edit `services/frontend/oauth-login.html`:

```javascript
const CONFIG = {
    projectId: 'your-gcp-project',
    apiKey: 'YOUR_WEB_API_KEY',  // From Identity Platform Console
    clientId: 'YOUR_CLIENT_ID.apps.googleusercontent.com',
    redirectUri: window.location.origin + window.location.pathname,
    // ...
};
```

### 5. Test Locally

```bash
cd services/frontend
python3 -m http.server 8080
# Open http://localhost:8080/oauth-login.html
```

## Documentation

- [Infrastructure Setup](infrastructure/env/IDENTITY_PLATFORM.md) - Terraform configuration details
- [OAuth Setup Guide](services/frontend/OAUTH_SETUP.md) - Complete OAuth configuration
- [Frontend README](services/frontend/README.md) - Frontend development guide

## Project Structure

```
.
├── infrastructure/
│   ├── env/                          # Environment-specific resources
│   │   ├── gcp_identity_platform.tf  # Identity Platform config
│   │   ├── gcp_cloud_run.tf          # Cloud Run services
│   │   ├── gcp_services.tf           # Enable APIs
│   │   ├── variables.tf              # Input variables
│   │   └── outputs.tf                # Output values
│   ├── config/
│   │   ├── dev/terraform.tfvars      # Dev environment config
│   │   └── prod/terraform.tfvars     # Prod environment config
│   └── root/                         # Root-level resources
├── services/
│   ├── frontend/
│   │   ├── oauth-login.html          # Pure OAuth2 login page
│   │   ├── Dockerfile.oauth          # Container image
│   │   └── nginx.conf                # Nginx configuration
│   └── backend/                      # Backend service
└── README.md
```

## How It Works

### OAuth Flow

1. **Initial Load**: Check localStorage for JWT token
2. **Login Click**: Redirect to Google OAuth (`accounts.google.com`)
3. **User Authentication**: User signs in with Google
4. **Redirect Back**: Google returns to app with `id_token` in URL fragment
5. **Parse Token**: Extract token from URL hash parameters
6. **Decode JWT**: Custom JavaScript function decodes token (no libraries)
7. **Display User**: Show email and name from JWT payload
8. **Store Token**: Save JWT to localStorage for future sessions

### Security

- ✅ State parameter prevents CSRF attacks
- ✅ Nonce prevents token replay
- ✅ Token expiry validation
- ✅ HTTPS enforced by Cloud Run
- ✅ No secrets in client code (API key is public)

## Cost Breakdown

Estimated monthly costs (assuming light usage):

| Service | Cost | Notes |
|---------|------|-------|
| Cloud Run (Frontend) | ~$0 | Scales to 0, free tier covers most usage |
| Cloud Run (Backend) | ~$0 | Scales to 0, free tier covers most usage |
| Identity Platform | Free | First 50k MAU free |
| Cloud Storage | ~$0.01 | Terraform state only |
| **Total** | **< $1/month** | 💰 Dirt cheap! |

## Troubleshooting

### "redirect_uri_mismatch"
- Ensure redirect URI in code matches GCP Console exactly
- Check for trailing slashes

### "Token expired"
- Tokens expire after 1 hour by default
- Click "Sign in" again to get new token

### "Invalid JWT"
- Check browser console for errors
- Verify token is complete (not truncated)

## Development

### Local Development

```bash
# Frontend
cd services/frontend
python3 -m http.server 8080

# Or use the React/Vite version
npm install
npm run dev
```

### Deploy to Cloud Run

```bash
# Build and push container
cd services/frontend
docker build -f Dockerfile.oauth -t gcr.io/YOUR_PROJECT/frontend .
docker push gcr.io/YOUR_PROJECT/frontend

# Deploy via Terraform
cd infrastructure/env
terraform apply
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `/infrastructure/env/IDENTITY_PLATFORM.md`
- Review the OAuth setup guide in `/services/frontend/OAUTH_SETUP.md`

## Next Steps

- [ ] Add token refresh mechanism
- [ ] Implement logout flow with Google
- [ ] Add monitoring and analytics
- [ ] Create CI/CD pipeline for deployments
- [ ] Add additional OAuth scopes
- [ ] Implement role-based access control

