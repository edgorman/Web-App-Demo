# OAuth2 Flow Diagram

This document illustrates the pure OAuth2/OIDC redirect flow implemented in this project.

## Flow Diagram

```
┌─────────────┐                                           ┌─────────────────┐
│             │                                           │                 │
│   Browser   │                                           │  Google OAuth   │
│             │                                           │  (accounts.     │
│             │                                           │   google.com)   │
└──────┬──────┘                                           └────────┬────────┘
       │                                                           │
       │  1. User visits frontend                                 │
       │     Check localStorage for JWT                           │
       │     ↓ No token found                                     │
       │                                                           │
       │  2. User clicks "Sign in with Google"                    │
       ├──────────────────────────────────────────────────────────>
       │     GET https://accounts.google.com/o/oauth2/v2/auth     │
       │     ?client_id=...                                       │
       │     &redirect_uri=https://frontend.run.app               │
       │     &response_type=id_token                              │
       │     &scope=openid email profile                          │
       │     &state=random_csrf_token                             │
       │     &nonce=random_nonce                                  │
       │                                                           │
       │                                                           │  3. Google
       │                                                           │     authenticates
       │                                                           │     user
       │                                                           │
       │  4. Google redirects back with token                     │
       <──────────────────────────────────────────────────────────┤
       │     https://frontend.run.app#                            │
       │       id_token=eyJhbGc...                               │
       │       &state=random_csrf_token                           │
       │                                                           │
       │  5. JavaScript parses URL fragment                       │
       │     - Extract id_token from hash                         │
       │     - Verify state matches (CSRF protection)             │
       │     - Decode JWT (custom function)                       │
       │     - Extract: email, name, exp                          │
       │                                                           │
       │  6. Save token to localStorage                           │
       │     localStorage.setItem('id_token', token)              │
       │                                                           │
       │  7. Display user info                                    │
       │     Show: email, name, expiry                            │
       │                                                           │
       │  8. On future visits                                     │
       │     Check localStorage                                   │
       │     Validate token not expired                           │
       │     Display user if valid                                │
       │                                                           │
       │  9. Logout                                               │
       │     localStorage.removeItem('id_token')                  │
       │                                                           │
       ▼                                                           ▼
```

## Detailed Step-by-Step

### Step 1: Initial Page Load

```javascript
// Check localStorage for existing token
const token = localStorage.getItem('id_token');

if (token && !isTokenExpired(token)) {
    displayUserInfo(token);
} else {
    showLogin();
}
```

### Step 2: User Clicks Login

```javascript
// Build OAuth URL
const state = generateRandomState();
sessionStorage.setItem('oauth_state', state);

const authUrl = 'https://accounts.google.com/o/oauth2/v2/auth' +
    '?client_id=' + CLIENT_ID +
    '&redirect_uri=' + REDIRECT_URI +
    '&response_type=id_token' +
    '&scope=openid email profile' +
    '&state=' + state +
    '&nonce=' + generateRandomNonce();

window.location.href = authUrl;
```

### Step 3: Google Authentication

Google handles:
- User login
- Consent screen (if needed)
- Token generation
- Redirect back to app

### Step 4: Parse OAuth Response

```javascript
// Parse URL fragment
const hash = window.location.hash.substring(1);
const params = new URLSearchParams(hash);

const idToken = params.get('id_token');
const state = params.get('state');

// Verify state (CSRF protection)
const savedState = sessionStorage.getItem('oauth_state');
if (state !== savedState) {
    throw new Error('Invalid state');
}
```

### Step 5: Decode JWT

```javascript
function decodeJWT(token) {
    const parts = token.split('.');
    const payload = parts[1];
    
    // Base64 URL decode
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(
        base64.length + (4 - base64.length % 4) % 4, 
        '='
    );
    
    // Decode and parse
    const jsonPayload = decodeURIComponent(
        atob(padded)
            .split('')
            .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
    );
    
    return JSON.parse(jsonPayload);
}

// Extract user info
const decoded = decodeJWT(idToken);
// decoded.email = "user@example.com"
// decoded.name = "John Doe"
// decoded.exp = 1234567890 (Unix timestamp)
```

### Step 6: Store and Display

```javascript
// Store token
localStorage.setItem('id_token', idToken);

// Display user info
document.getElementById('userEmail').textContent = decoded.email;
document.getElementById('userName').textContent = decoded.name;
```

## JWT Token Structure

```
eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMyJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiJjbGllbnRfaWQiLCJhdWQiOiJjbGllbnRfaWQiLCJzdWIiOiIxMjM0NTY3ODkwIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxNTE2MjQyNjIyfQ.signature
│                    HEADER                    │                                                           PAYLOAD                                                            │ SIGNATURE │
```

### Header (decoded)

```json
{
  "alg": "RS256",
  "kid": "123"
}
```

### Payload (decoded)

```json
{
  "iss": "https://accounts.google.com",
  "azp": "client_id",
  "aud": "client_id",
  "sub": "1234567890",
  "email": "user@example.com",
  "email_verified": true,
  "name": "John Doe",
  "picture": "https://lh3.googleusercontent.com/...",
  "iat": 1516239022,
  "exp": 1516242622
}
```

### What We Extract

- `email` - User's email address
- `name` - User's full name
- `exp` - Token expiration (Unix timestamp)
- `picture` - Profile picture URL (optional)

## Security Considerations

### 1. State Parameter (CSRF Protection)

```javascript
// Before redirect
const state = crypto.getRandomValues(new Uint8Array(16));
sessionStorage.setItem('oauth_state', state);

// After redirect
if (params.get('state') !== sessionStorage.getItem('oauth_state')) {
    throw new Error('CSRF attack detected');
}
```

### 2. Nonce Parameter (Replay Protection)

```javascript
const nonce = crypto.getRandomValues(new Uint8Array(16));
// Include in OAuth request
// Google will include it in the JWT
// Can be verified if needed
```

### 3. Token Expiry

```javascript
function isTokenExpired(token) {
    const decoded = decodeJWT(token);
    return decoded.exp * 1000 < Date.now();
}
```

### 4. HTTPS Only

- Cloud Run enforces HTTPS
- Tokens never sent over HTTP
- URL fragments not sent to server

### 5. Content Security Policy

```nginx
Content-Security-Policy: 
    default-src 'self';
    script-src 'self' 'unsafe-inline';
    connect-src 'self' https://accounts.google.com https://oauth2.googleapis.com;
```

## No Backend Required

This implementation is **entirely client-side**:

✅ No server-side code  
✅ No database  
✅ No API endpoints  
✅ No token verification server  
✅ No refresh token handling  

JWT token is the **only source of truth**.

## Comparison: Implicit Flow vs Authorization Code Flow

### Implicit Flow (Used Here)

```
Browser → Google → Browser (with token in URL)
```

**Pros:**
- No backend required
- Simpler implementation
- Instant token delivery

**Cons:**
- Token in URL (visible in history)
- No refresh token
- Less secure

### Authorization Code Flow (More Secure)

```
Browser → Google → Browser (with code)
Browser → Backend → Google (exchange code for token)
Backend → Browser (return token)
```

**Pros:**
- More secure
- Supports refresh tokens
- Token never in URL

**Cons:**
- Requires backend server
- More complex
- Higher cost

**For "dirt cheap" architecture, Implicit Flow is appropriate.**

## Token Storage Comparison

### localStorage (Used Here)

**Pros:**
- Persists across sessions
- Simple to use
- No backend needed

**Cons:**
- Vulnerable to XSS
- Accessible from JavaScript

### httpOnly Cookies (More Secure)

**Pros:**
- Not accessible from JavaScript
- XSS protection
- Automatic CSRF protection

**Cons:**
- Requires backend server
- More complex setup

**For "no database" architecture, localStorage is appropriate.**

## Future Enhancements

1. **Token Refresh**: Implement refresh token flow (requires backend)
2. **Token Verification**: Verify JWT signature on backend
3. **Authorization Code Flow**: More secure OAuth flow (requires backend)
4. **Multiple Providers**: Support Facebook, GitHub, etc.
5. **Role-Based Access**: Add user roles and permissions

---

**Current Implementation**: Optimized for "dirt cheap" cost with reasonable security.
