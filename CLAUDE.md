# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ First Time Setup - Important!

**Before editing this file**, run this command to keep your local changes private:
```bash
git update-index --assume-unchanged CLAUDE.md
```

This allows you to customize CLAUDE.md for your needs without affecting the shared version. Your edits will stay local and won't be committed to the repository.

To later update the shared version (if needed):
```bash
git update-index --no-assume-unchanged CLAUDE.md
```

## Project Overview

**youareabsolutelyright** (also known as "BugRewind") is a full-stack application that performs "git archaeology" to trace bug origins through commit history analysis. The system combines AI-powered code analysis with OCR capabilities to identify when and where bugs were introduced in a codebase.

### Architecture

This is a **multi-component system** with three developer tracks:

1. **Backend (FastAPI)**: Git analysis, Claude AI integration, DeepSeek OCR for document scanning
2. **Search Infrastructure (Elastic Serverless)**: Commit indexing and search with Postman Flow orchestration
3. **Frontend (Next.js)**: User interface with diff viewer, commit timeline, and OCR image upload

## Development Commands

### Frontend (Next.js)
```bash
cd frontend
npm run dev      # Development server on http://localhost:3000
npm run build    # Production build
npm start        # Production server
npm run lint     # Run ESLint
```

### Backend (FastAPI)
```bash
cd backend
source venv/bin/activate  # Activate virtual environment (Windows: venv\Scripts\activate)
python app/main.py        # Start development server on port 8000 (with reload)
```

**Backend setup** (if needed):
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Tech Stack

### Frontend
- **Framework**: Next.js 16.0.0 (App Router)
- **React**: 19.2.0
- **Styling**: Tailwind CSS v4 with PostCSS
- **TypeScript**: v5 with strict mode
- **Path alias**: `@/*` maps to project root

### Backend (Planned)
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Git Operations**: GitPython 3.1.40
- **Search**: Elasticsearch 8.11.0
- **AI Integration**: Claude API via httpx
- **OCR**: DeepSeek API
- **GitHub Integration**: PyGithub 2.1.1

## Configuration & Environment

### Backend Environment Variables
Located in `backend/.env` (see `backend/.env.example`):
- `PORT`: Server port (default: 8000)
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `ELASTIC_API_KEY`: Elasticsearch API key
- `ELASTIC_ENDPOINT`: Elasticsearch serverless endpoint URL
- `GITHUB_TOKEN`: GitHub personal access token
- `DEEPSEEK_API_KEY`: DeepSeek OCR API key
- `CLONE_DIR`: Directory for temporary git clones (default: `/tmp/bugrewind-clones`)

### Frontend Environment Variables
Located in `frontend/.env.local`:
- `NEXT_PUBLIC_BACKEND_URL`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_POSTMAN_ACTION_URL`: Postman Action URL for flows

**Note**: Frontend variables must use `NEXT_PUBLIC_` prefix to be accessible in browser.

## Project Structure

```
youareabsolutelyright/
├── frontend/              # Next.js application
│   ├── app/              # App Router pages and layouts
│   │   ├── page.tsx     # Home page
│   │   ├── layout.tsx   # Root layout with Geist fonts
│   │   └── globals.css  # Global styles
│   ├── package.json     # Frontend dependencies
│   └── tsconfig.json    # TypeScript config with @/* paths
│
├── backend/              # FastAPI application (in development)
│   ├── app/             # Application code (planned structure)
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic (git, Claude, OCR)
│   │   ├── utils/       # Helper functions
│   │   └── models/      # Pydantic models
│   ├── .env            # Environment variables (gitignored)
│   ├── .env.example    # Template for environment setup
│   └── requirements.txt # Python dependencies
│
├── postman/             # Postman collections and flows
├── demo-repos/          # Test repositories for development
├── DEV_A.md            # Backend development guide (22-hour plan)
├── DEV_B.md            # Elastic + Postman development guide
└── DEV_C.md            # Frontend development guide
```

## Key Implementation Details

### Backend Architecture (from DEV_A.md)
The FastAPI backend is structured around:
- **Git Analysis**: Clone repos, traverse commit history, identify file changes
- **AI Analysis**: Use Claude API to analyze code diffs and identify bug introduction points
- **OCR Integration**: DeepSeek API for scanning error screenshots/documents
- **GitHub PR Creation**: Automated pull request generation with fix suggestions

Expected API structure:
- `/health`: Health check endpoint
- `/api/*`: Main API routes for bug analysis

### Search Infrastructure (from DEV_B.md)
- **Elastic Serverless**: Indexes commit data for fast historical search
- **Postman Flow**: AI Agent orchestration for complex analysis workflows
- Public Postman Action for external integration

### Frontend Features (from DEV_C.md)
- Input form for repository URLs and bug descriptions
- Diff viewer for commit comparisons
- Commit timeline visualization
- **Killer feature**: OCR image upload to analyze error screenshots
- Responsive design with Tailwind CSS custom theme

## Development Workflow

### Multi-Track Development
This project is designed for **three parallel developers** (DEV A, B, C) working on backend, search, and frontend respectively. The guides (DEV_A.md, DEV_B.md, DEV_C.md) contain detailed 22-hour implementation plans for each track.

### TypeScript Configuration
- Strict mode enabled
- Target: ES2017
- JSX: react-jsx (not preserve)
- Module resolution: bundler
- Path aliases: `@/*` for imports

### Git Workflow
- Main branch: `main`
- Environment files (`.env`) are gitignored
- Clean working directory at project start
