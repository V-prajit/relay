# PM Copilot

AI-powered automation tool that transforms product specifications into actionable GitHub pull requests.

## Overview

PM Copilot bridges the gap between product management and engineering by automatically:
- Parsing natural language feature requests
- Searching codebase for relevant files
- Detecting conflicts with existing PRs
- Generating pull requests with acceptance criteria
- Routing to available engineers

## Architecture

```
Slack/API Request
     |
Postman Flow (AI Agent + Multi-API Orchestration)
     |
     +-- Ripgrep API (Code Search)
     +-- Claude API (PR Generation)
     +-- GitHub API (PR Creation)
     +-- Slack API (Notifications)
     +-- Calendar API (Availability)
```

## Components

### Ripgrep API
HTTP wrapper for ripgrep code search tool
- Location: `ripgrep-api/`
- Port: 3001
- Endpoints: `/api/search`, `/api/health`

### Postman Flow
Main orchestration layer using Postman Flows
- AI Agent for intent parsing
- Multi-API coordination
- Conflict detection
- Engineer routing

### CI/CD Pipeline
Automated monitoring and testing
- GitHub Actions workflow
- Newman CLI integration
- Health checks every 30 minutes
- Slack notifications

## Setup

### Prerequisites
- Node.js 18+
- Postman Desktop v11.42.3+
- API Keys:
  - Claude API key
  - GitHub Personal Access Token
  - Slack webhook URL

### Ripgrep API

```bash
cd ripgrep-api
npm install
cp .env.example .env
npm start
```

### Postman Flow

1. Import collections from `postman/collections/`
2. Import environments from `postman/environments/`
3. Configure API keys in environment variables
4. Deploy Flow as Postman Action

### GitHub Actions

1. Add secrets to repository:
   - ACTION_URL
   - SLACK_WEBHOOK_URL
2. Push to main branch
3. Workflow runs automatically

## Configuration

### Environment Variables

Production (`postman/environments/production.json`):
- ACTION_URL: Deployed Postman Action URL
- CLAUDE_API_KEY: Anthropic API key
- GITHUB_TOKEN: GitHub PAT with repo scope
- SLACK_WEBHOOK_URL: Slack incoming webhook

Development (`postman/environments/dev.json`):
- Same as production with local URLs

### MCP Server

Model Context Protocol configuration for AI assistant integration.
See `docs/MCP_SETUP.md` for Claude Desktop setup.

## Testing

### Local Testing
```bash
newman run postman/collections/pm-copilot-health-check.json \
  --environment postman/environments/dev.json
```

### CI/CD Testing
Automated via GitHub Actions on push and schedule.

## Documentation

- `docs/MCP_SETUP.md` - MCP server integration guide
- `docs/CI_CD_SETUP.md` - CI/CD pipeline documentation
- `docs/POSTMAN_FLOW_NEW_FEATURES.md` - Feature handling guide
- `CLAUDE.md` - Project instructions for Claude Code

## Monitoring

### GitHub Actions
- Health checks every 30 minutes
- Performance testing on push
- Automated Slack alerts
- HTML reports as artifacts

### Postman Monitor
- 5-minute health checks
- Email notifications
- Multi-region monitoring

## API Endpoints

### Ripgrep API
- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/search` - Code search
- `GET /api/types` - Supported file types

### PM Copilot Flow
- `POST /` - Create PR from specification
- `GET /health` - Health check
- `GET /status` - Dashboard metrics
- `GET /dependencies` - Dependency status

## License

MIT License

## Support

GitHub Issues: github.com/yourusername/pm-copilot/issues
