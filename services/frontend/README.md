# Frontend Service

A React-based frontend service built with TypeScript and Vite.

## Prerequisites

- Node.js 18+ and npm

## Getting Started

```bash
# Install dependencies
make install

# Start development server
make dev
```

## Available Commands

Using Make:
- `make install` - Install dependencies
- `make dev` - Start development server on http://localhost:3000
- `make build` - Build for production
- `make preview` - Preview production build
- `make lint` - Run ESLint
- `make format` - Format code with Prettier
- `make clean` - Clean build artifacts and dependencies
- `make help` - Show all available commands

Or using npm directly:
- `npm install` - Install dependencies
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Project Structure

```
src/
├── components/
│   ├── common/
│   │   └── GoogleSignInButton.tsx
│   └── pages/
│       └── Home.tsx
├── hooks/
│   └── useGoogleAuth.ts
├── services/
│   └── api.ts
├── types/
│   ├── google.d.ts
│   └── models.ts
├── config/
│   └── app.ts
├── App.tsx
├── main.tsx
├── App.css
└── index.css
```

## Configuration

Environment variables can be configured in `.env` file (see `.env.example`):

- `VITE_BACKEND_URL` - Backend API URL
- `VITE_GOOGLE_CLIENT_ID` - Google OAuth 2.0 client ID used for Google Sign-In (see [Google Sign-In](../../documentation/services/google-sign-in.md))
