# Frontend Service

A modern React-based frontend service built with TypeScript and Vite.

## Features

- ⚡️ **Vite** - Fast build tool and dev server
- ⚛️ **React 18** - Latest React with concurrent features
- 🔷 **TypeScript** - Type safety and better developer experience
- 🎨 **CSS** - Modern CSS with dark/light mode support
- 🐳 **Docker** - Containerized deployment with nginx
- 📦 **Code Quality** - ESLint and Prettier configured

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Docker (optional, for containerized deployment)

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server (runs on http://localhost:3000)
npm run dev
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Code Quality

```bash
# Run linter
npm run lint

# Format code
npm run format
```

### Docker

```bash
# Build Docker image
docker build -t frontend-service .

# Run container
docker run -p 80:80 frontend-service
```

## Project Structure

```
src/
├── components/
│   └── pages/
│       └── Home.tsx       # Home page component
├── App.tsx                # Main app component
├── main.tsx              # Application entry point
├── App.css               # App-specific styles
└── index.css             # Global styles
```

## Configuration

Environment variables can be configured in `.env` file (see `.env.example`):

- `VITE_API_URL` - Backend API URL

## Deployment

The application is containerized using Docker with a multi-stage build:
1. Build stage: Compiles TypeScript and bundles assets
2. Production stage: Serves static files with nginx

The nginx server includes:
- Static asset caching
- Gzip compression
- Security headers
- SPA routing support
