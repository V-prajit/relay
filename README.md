# Relay

Transform vague PM specifications into actionable GitHub issues through intelligent workflow automation powered by Postman Flows.

---

## Overview

Relay automates the PM-to-Engineer handoff by converting natural language feature requests into structured GitHub issues with acceptance criteria and impacted file lists. A single Slack command triggers an autonomous workflow that searches your codebase, analyzes requirements, and creates actionable issues in seconds.

**Problem**: Product managers and engineers spend significant time clarifying requirements, searching for relevant code, and drafting structured issues manually.

**Solution**: `/relay "add dark mode toggle"` in Slack creates a complete GitHub issue with acceptance criteria, impacted files, and implementation guidance in 30 seconds.

---

## How It Works

```
Slack: /relay "fix mobile login"
    ↓
Postman Action receives form-encoded webhook
    ↓
Request → Evaluate → Validate → Fork
    ├─→ Immediate 202 response to Slack
    └─→ Background execution:
        ├─→ Ripgrep API searches codebase
        ├─→ AI generates structured issue content
        ├─→ GitHub creates issue
        └─→ Slack notification with results
```

**Key Features**:
- Asynchronous processing with immediate acknowledgment
- Intelligent code search with ripgrep
- Automatic new feature detection
- GitHub Issues API integration
- Slack notifications with reasoning traces

---

## Technology Stack

**Core Services**:
- **Postman Flows**: Orchestration layer with AI Agent Block, Flow Modules, and deployed Actions
- **Ripgrep API**: Fast code search service (Node.js/Express wrapper around ripgrep CLI)
- **GitHub REST API**: Issue creation and repository management
- **Slack**: Slash commands and incoming webhooks

**Optional Components** (see SNOWFLAKE_MLH.md):
- Snowflake Cortex for AI-powered PR generation
- Next.js dashboard for analytics visualization
- FastAPI backend for extended LLM integration

**Infrastructure**:
- DigitalOcean for API deployment
- Postman cloud for Action hosting

---

## Quick Start

### Prerequisites

- Postman Desktop (v11.42.3 or later)
- Node.js 18+ (for Ripgrep API)
- GitHub personal access token with `repo` scope
- Slack workspace with admin access

### Installation

```bash
# Clone repository
git clone https://github.com/V-prajit/relay.git
cd relay

# Set up Ripgrep API
cd ripgrep-api
npm install
cp .env.example .env
# Edit .env: PORT=3001
npm run dev

# Test Ripgrep API
curl http://localhost:3001/api/health
```

**Detailed setup instructions**: See [SETUP.md](./SETUP.md)

---

## Architecture

The system uses an asynchronous Postman Flow pattern to handle Slack's 3-second timeout requirement:

1. **Request Block**: Receives form-encoded data from Slack
2. **Evaluate Block**: Flattens Slack's array-wrapped values (`{text: ["hello"]}` → `{text: "hello"}`)
3. **Validate Block**: Ensures required fields are present
4. **Fork Pattern**:
   - One path immediately returns 202 Accepted to Slack
   - Another path executes background workflow (up to 60 minutes)
5. **Module Execution**: Searches code, generates content, creates GitHub issue

**Technical details**: See [ARCHITECTURE.md](./ARCHITECTURE.md)

---

## Project Structure

```
relay/
├── postman/
│   ├── modules/                      # 6 reusable Flow Modules
│   ├── AI-AGENT-CONFIGURATION.md     # AI Agent system prompt
│   └── collections/                  # Postman API collections
├── ripgrep-api/                      # Code search service
│   ├── src/
│   │   ├── index.js                  # Express server
│   │   └── routes/search.js          # Search endpoint
│   ├── package.json
│   └── .env.example
├── backend/                          # Optional: Snowflake integration
├── frontend/                         # Optional: Analytics dashboard
├── docs/
│   ├── FLOW_MODULES.md               # Module documentation
│   ├── TROUBLESHOOTING.md            # Common issues and fixes
│   └── CI_CD_SETUP.md                # GitHub Actions configuration
├── README.md                         # This file
├── SETUP.md                          # Installation guide
├── ARCHITECTURE.md                   # System design documentation
├── DEPLOYMENT.md                     # Production deployment guide
├── ROADMAP.md                        # Planned features
├── CLAUDE.md                         # Developer instructions (for Claude Code)
└── SNOWFLAKE_MLH.md                  # Optional Snowflake Cortex integration
```

---

## Documentation

### Core Documentation
- **[SETUP.md](./SETUP.md)**: Complete installation and configuration guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: System design, data flow, and technical implementation
- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Production deployment to DigitalOcean
- **[ROADMAP.md](./ROADMAP.md)**: Planned features and future enhancements

### Specialized Guides
- **[docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)**: Common issues, error codes, and solutions
- **[docs/FLOW_MODULES.md](./docs/FLOW_MODULES.md)**: Postman Flow Module specifications
- **[postman/AI-AGENT-CONFIGURATION.md](./postman/AI-AGENT-CONFIGURATION.md)**: AI Agent system prompt and configuration

### Developer Resources
- **[CLAUDE.md](./CLAUDE.md)**: Instructions for Claude Code (AI pair programmer)
- **[docs/CI_CD_SETUP.md](./docs/CI_CD_SETUP.md)**: GitHub Actions and automation
- **[SNOWFLAKE_MLH.md](./SNOWFLAKE_MLH.md)**: Optional Snowflake Cortex integration for MLH hackathon

---

## Deployment

### Local Development

```bash
# Terminal 1: Ripgrep API
cd ripgrep-api && npm run dev

# Terminal 2 (optional): Snowflake backend
cd backend && python -m uvicorn app.main:app --reload

# Terminal 3 (optional): Dashboard
cd frontend && npm run dev
```

### Production

The core system requires:
1. **Ripgrep API**: Deployed to DigitalOcean App Platform
2. **Postman Action**: Deployed from Postman Flows interface
3. **Slack App**: Configured with Action URL as webhook

**Full deployment guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## Testing

### Test Ripgrep API

```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ProfileCard", "type": "tsx"}'
```

### Test Postman Action (deployed)

```bash
curl -X POST 'https://your-action-url.flows.pstmn.io/api/default/endpoint' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'text=test+feature+request'
```

### Test in Slack

```
/relay add dark mode toggle to settings
```

Expected result: GitHub issue created within 15 seconds, Slack notification with issue link.

---

## Troubleshooting

### Common Issues

**Ripgrep API not responding**:
```bash
lsof -i :3001
curl http://localhost:3001/api/health
```

**Postman Flow validation errors**:
- Check that Slack data is being flattened correctly (arrays → strings)
- Verify Action Configuration secrets are set (GITHUB_PAT)
- Ensure Request → Evaluate → Validate wiring is correct

**GitHub issue not created**:
- Verify GitHub token has `repo` scope
- Check repository name format: `owner/repo`
- Review Postman Flow run logs for HTTP 401/422 errors

**Slack command not responding**:
- Verify Slash Command Request URL matches deployed Action URL
- Disable Socket Mode in Slack app settings
- Check that webhook response is 202 within 3 seconds

**Detailed troubleshooting**: See [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)

---

## Contributing

Contributions are welcome. When adding features:

1. Create a new Flow Module for new API integrations
2. Update the AI Agent prompt to reference new tools
3. Add comprehensive error handling
4. Document in relevant .md files
5. Test end-to-end via Slack before submitting PR

See [CLAUDE.md](./CLAUDE.md) for development guidelines.

---

## Use Cases

### For Product Managers
- Convert feature ideas to structured issues instantly
- Automatically generate acceptance criteria
- Get visibility into which code files are impacted
- Reduce back-and-forth clarification cycles

### For Engineers
- Receive complete context in GitHub issues
- See impacted files before starting work
- Get clear acceptance criteria upfront
- Focus on implementation instead of requirements gathering

### For Teams
- Streamline PM-to-Engineer handoff
- Enable asynchronous collaboration
- Maintain audit trail in Slack and GitHub
- Scale feature request processing

---

## Resources

**Postman Documentation**:
- [AI Agent Block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Flow Modules](https://learning.postman.com/docs/postman-flows/reference/modules/)
- [Deploy Actions](https://learning.postman.com/docs/postman-flows/build-flows/actions/)
- [TypeScript in Flows](https://learning.postman.com/docs/postman-flows/typescript/typescript-overview/)

**API Documentation**:
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Slash Commands](https://api.slack.com/interactivity/slash-commands)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)

**Related Projects**:
- [Ripgrep](https://github.com/BurntSushi/ripgrep): Fast code search tool
- [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex): Optional LLM integration

---

## License

MIT License - See LICENSE file for details.

---

## Team

**Shashank Yaji** - [LinkedIn](https://www.linkedin.com/in/shashankyaji/)
**Prajit Viswanadha** - [LinkedIn](https://www.linkedin.com/in/prajit-viswanadha/)
**Rabib Husain** - [LinkedIn](https://www.linkedin.com/in/rabib-husain/)

---

**GitHub**: https://github.com/V-prajit/relay
**Demo**: Live on DigitalOcean
**Built with**: Postman Flows, Node.js, GitHub API, Slack
