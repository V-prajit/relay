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

1. **Backend (FastAPI)**: Git analysis, Claude AI integration, DeepSeek OCR for visual context compression (10-40x token reduction)
2. **Search Infrastructure (Elastic Serverless)**: Commit indexing and search with Postman Flow orchestration
3. **Frontend (Next.js)**: User interface with diff viewer and commit timeline

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
- **Visual Context Compression**: DeepSeek-OCR for rendering text as images (10-40x token reduction)
- **GitHub Integration**: PyGithub 2.1.1

## Configuration & Environment

### Backend Environment Variables
Located in `backend/.env` (see `backend/.env.example`):
- `PORT`: Server port (default: 8000)
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `ELASTIC_API_KEY`: Elasticsearch API key
- `ELASTIC_ENDPOINT`: Elasticsearch serverless endpoint URL
- `GITHUB_TOKEN`: GitHub personal access token
- `DEEPSEEK_API_KEY`: DeepSeek API key (optional - for local OCR model if using compression storage mode)
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
- **Visual Context Compression**: Render large diffs as images using DeepSeek-OCR technique (10-40x token reduction)
- **AI Analysis**: Use Claude Vision API to analyze diff images, saving 90%+ on token costs
- **GitHub PR Creation**: Automated pull request generation with fix suggestions

**Key Innovation:** Instead of sending 5000-line diffs as text (4000 tokens), we render them as images (100-256 vision tokens) and leverage Claude's vision capabilities. This enables cost-effective analysis of massive codebases.

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
- Responsive design with Tailwind CSS custom theme
- Polished animations and loading states

**Note:** The "killer feature" is backend visual compression (invisible to users), not a frontend upload feature.

## Visual Context Compression (DeepSeek-OCR)

### The Innovation

Traditional approach: Send 5000-line git diff as text → 4000 tokens → expensive + slow
Our approach: Render diff as image → 100-256 vision tokens → Claude Vision reads it → 97% token savings

### How It Works

1. **Backend receives git diff** (could be 10,000+ lines)
2. **Render as high-quality image** using LaTeX or HTML-to-PNG pipeline
   - 640x640 resolution = 100 vision tokens
   - 1024x1024 resolution = 256 vision tokens
3. **Send image to Claude Vision API** with prompt: "Analyze this diff for bug origins"
4. **Claude reads text from image** and performs analysis
5. **Return results** with 90-97% token cost reduction

### Compression Ratios

- **≤10x compression:** Near-lossless (97% OCR precision)
- **10-20x compression:** Minor formatting loss, still usable
- **>20x compression:** Lossy, good for memory/summaries only

### Implementation Location

- `app/services/image_renderer.py`: Text-to-image rendering (LaTeX/HTML)
- `app/services/claude_service.py`: Vision API integration
- `app/services/deepseek_service.py`: Optional local 3B model for decompression

### Token Savings Example

**Traditional (text-based):**
5000-line refactor diff = 4000 text tokens
Claude API cost: $0.12 (input) + $0.60 (output) = $0.72

**With Visual Compression:**
Same diff rendered as 640x640 image = 100 vision tokens
Claude API cost: $0.003 (input) + $0.60 (output) = $0.60
Savings: 97% reduction in input tokens

### Hardware Requirements

- **Text rendering:** CPU-only (LaTeX, WeasyPrint)
- **Optional local OCR model:** RTX 3060 (12GB VRAM) - runs DeepSeek-OCR 3B
- **Vision API:** Claude Sonnet 4.5 with vision support

### References

- Paper: [DeepSeek-OCR: Contexts Optical Compression](https://arxiv.org/abs/2510.18234)
- Model: [deepseek-ai/DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR) (3B params, MIT license)
- Independent study: [Text or Pixels? It Takes Half](https://arxiv.org/html/2510.18279v1) (confirms 2x token reduction)

**This is the hackathon differentiator:** While competitors hit token limits on large diffs, we analyze entire framework refactors for pennies.

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
