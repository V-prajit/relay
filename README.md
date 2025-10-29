# Relay

**PM Copilot** - Transform vague PM specs into actionable GitHub PRs and issues through intelligent workflow automation.

---

## Inspiration

Our project solves a real problem that we, SWE interns to PMs face: vague product requirements and incompatible interpretations. Engineers have to decode and figure out:

- Clarifying requirements back and forth
- Searching which files to change
- Writing acceptance criteria
- Creating boring boilerplate PRs

---

## What It Does

This is how our Agent System works:

1. **PM in Slack**: "Fix React version issue"
2. **Postman AI Agent** processes the request
3. **Ripgrep** finds relevant code files (Settings.tsx, theme.ts)
4. **Snowflake Cortex AI** generates PR code (≤30 lines)
5. **GitHub PR** created automatically
6. **Slack** notifies team with reasoning trace
7. **Dashboard** shows history and the current usage of current PRs and Snowflake in general

**Result**: PR + acceptance criteria + impacted files in 30 seconds.

---

## Architecture

![Architecture Diagram](./architecture-diagram.jpg)

**Flow**:
- PM submits request via Slack
- Postman AI Agents orchestrate the workflow
- Ripgrep searches codebase
- Snowflake Cortex AI generates PR content
- GitHub receives PR/Issue
- DigitalOcean hosts the deployment
- Slack notifies team with results

---

## Current Features

### 1. Postman AI Agent Orchestration
- **Autonomous workflow**: No manual loops or decision blocks
- **Multi-API coordination**: Ripgrep, Snowflake Cortex, GitHub, Slack
- **Reasoning transparency**: Shows every decision step
- **Flow Modules**: Reusable tools for clean architecture

### 2. Intelligent Code Search (Ripgrep API)
- **Fast code search**: Uses ripgrep with glob patterns
- **New feature detection**: Handles both new features and existing code modifications
- **Context-aware results**: Returns structured file information for AI analysis

### 3. AI-Powered PR Generation (Snowflake Cortex)
- **Natural language processing**: Understands vague PM requests
- **Structured output**: Generates titles, descriptions, acceptance criteria
- **Code-aware**: Tailors content based on impacted files
- **PR size constraint**: Keeps PRs under 30 lines for easy review

### 4. GitHub Integration
- **Issue creation**: Working end-to-end
- **PR creation**: In development (placeholder commits)
- **Automated branching**: Creates feature branches automatically

### 5. Slack Integration
- **Slash command**: `/impact "feature request"`
- **Rich notifications**: Block Kit formatting with buttons
- **Reasoning traces**: Full transparency into AI decisions
- **One-click navigation**: Direct links to GitHub

### 6. Dashboard (Proof of Concept)
- **PR history**: Track all generated PRs and issues
- **Snowflake usage**: Monitor Cortex API usage and costs
- **Analytics**: Workflow metrics and system health
- **Visualization**: Reasoning traces and decision steps

---

## Tech Stack

**Postman Flows**
- AI Agent Block (GPT-5 autonomous reasoning)
- Flow Modules (reusable tools)
- Actions (deployed with public URL)
- Analytics (tool call logging)

**Backend APIs**
- Ripgrep API (Node.js/Express code search)
- FastAPI backend (Snowflake Cortex integration)
- GitHub REST API (PR/issue creation)
- Slack Webhooks (Block Kit notifications)

**AI/LLM**
- Snowflake Cortex (Arctic LLM for PR generation)
- GPT-5 (Postman AI Agent orchestration)

**Infrastructure**
- DigitalOcean (deployment)
- Next.js (dashboard - proof of concept)

---

## Quick Start

### Prerequisites

- Postman Desktop (v11.42.3+)
- Node.js 18+
- GitHub Personal Access Token (`repo` scope)
- Slack App with Incoming Webhook
- Snowflake account with Cortex access

### Setup

**Full setup instructions**: See `SETUP.md`

**Quick start**:

1. **Clone repository**
   ```bash
   git clone https://github.com/V-prajit/relay.git
   cd relay
   ```

2. **Setup Ripgrep API**
   ```bash
   cd ripgrep-api
   npm install && npm run dev
   ```

3. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```

4. **Configure Postman Flow**
   - Import modules from `postman/modules/`
   - Setup AI Agent with prompt from `postman/AI-AGENT-CONFIGURATION.md`
   - Deploy as Action

5. **Setup Slack**
   - Create slash command `/impact`
   - Point to Postman Action URL

6. **Test**
   ```
   /impact "Fix React version issue"
   ```

**Deployment**: Currently deployed on DigitalOcean. See `SETUP.md` for deployment instructions.

---

## Project Structure

```
relay/
├── postman/
│   ├── modules/              # 6 Flow Modules (AI Agent tools)
│   ├── AI-AGENT-CONFIGURATION.md
│   └── collections/          # API collections
├── ripgrep-api/              # Code search API (Node.js)
│   ├── src/
│   └── package.json
├── backend/                  # FastAPI backend (Snowflake integration)
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic
│   └── requirements.txt
├── frontend/                 # Dashboard (Next.js - POC)
├── docs/                     # Documentation and guides
├── architecture-diagram.jpg  # System architecture
├── README.md                 # This file
├── CLAUDE.md                 # Developer instructions
└── SETUP.md                  # Complete setup guide
```

---

## Future Implementations

### Phase 1: Enhanced Search & Context

**Elasticsearch Integration**
- Advanced code indexing and semantic search
- Faster search across large codebases
- Historical code pattern analysis

**OCR Integration**
- Extract code from screenshots and design mockups
- Increase context window for larger codebases
- Support multiple file analysis in single request
- Visual context compression for better AI understanding

### Phase 2: Multi-Repository Support

**Multiple Repositories**
- Cross-repo dependency detection
- Microservices architecture support
- Unified PR creation across repos
- Repository relationship mapping

### Phase 3: Testing & CI/CD Integration

**Test Environment Integration**
- Automated test generation for PRs
- Sandbox environment creation
- Integration test execution
- Test coverage reporting

**CI/CD Pipeline Integration**
- Auto-trigger builds on PR creation
- Pre-merge validation
- Automated deployment to staging
- Rollback capabilities

### Phase 4: Advanced Conflict Detection

**Smart Conflict Analysis**
- Co-change analysis (files that change together)
- Historical conflict patterns
- Calendar integration for engineer availability
- Predictive conflict warnings

### Phase 5: Project Management Integration

**Asana/Jira Integration**
- Auto-create tasks from feature requests
- Link PRs to project milestones
- Assign based on code ownership
- Sync status updates

### Phase 6: Improved User Experience

**Postman Feature Request & Flow Feedback**
- User feedback loop for generated PRs
- Quality rating system
- Iterative improvement based on feedback
- Custom template support

**Customizable Timing & Constraints**
- Remove hardcoded time limits
- Configurable PR size constraints
- Custom validation rules
- Team-specific workflows

**Environment Variable UX Improvement**
- Better variable management interface
- Role-based access control
- Prevent concurrent edits
- Notification conflict resolution
- Variable version history

### Phase 7: Code Quality & Review

**CodeRabbit AI Review Integration**
- Automated code review on generated PRs
- Security vulnerability scanning
- Best practice recommendations
- Automated fix suggestions

**Multi-Model Routing**
- GPT-5 for orchestration
- Claude for code generation
- Specialized models for different tasks
- Cost optimization based on task complexity

---

## Use Cases

### For PMs
- **Faster iteration**: Feature request → Issue/PR automatically
- **Better clarity**: Auto-generated acceptance criteria
- **Full visibility**: Reasoning trace shows every decision
- **Reduced back-and-forth**: Engineers get complete context upfront

### For Engineers
- **Less clarification needed**: All context provided in issue/PR
- **Conflict awareness**: Know about overlaps before coding
- **Ready to implement**: Files identified, requirements clear
- **Focus on coding**: Skip manual PR drafting

### For Teams
- **Reduced friction**: Eliminate lengthy clarification cycles
- **Async friendly**: PM requests don't block engineers
- **Audit trail**: Slack history + reasoning traces
- **Scalable process**: Handles multiple requests efficiently

---

## Troubleshooting

### Common Issues

**Ripgrep API not responding**:
```bash
cd ripgrep-api && npm run dev
curl http://localhost:3001/api/health
```

**Backend not responding**:
```bash
cd backend && python -m uvicorn app.main:app --reload
curl http://localhost:8000/health
```

**Postman Flow errors**:
- Check environment variables are set correctly
- Verify GitHub token has `repo` scope
- Ensure Slack webhook URL is correct
- See `docs/POSTMAN_FLOW_FIX_GUIDE.md`

**Slack command not working**:
- Reinstall Slack app
- Verify Request URL matches Postman Action URL
- Check webhook points to correct channel

**GitHub PR/Issue not created**:
- Verify `GITHUB_TOKEN` is valid
- Check repository name format: `owner/repo`
- See `GITHUB_PR_FIX.md` for recent fixes

**Detailed troubleshooting**: See `CLAUDE.md` for comprehensive guide.

---

## Contributing

See `CLAUDE.md` for development guidelines.

**Quick Guide**:
1. Create new Flow Module for new API integrations
2. Update AI Agent prompt to reference new tools
3. Add error handling and comprehensive documentation
4. Test end-to-end via Slack before committing

---

## Resources

**Documentation**:
- `SETUP.md` - Complete setup and deployment guide
- `CLAUDE.md` - Developer instructions and architecture
- `GITHUB_PR_FIX.md` - Recent bug fixes and solutions
- `postman/AI-AGENT-CONFIGURATION.md` - AI Agent configuration
- `docs/` - Additional troubleshooting guides

**Postman Resources**:
- [AI Agent Block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Flow Modules](https://learning.postman.com/docs/postman-flows/reference/modules/)
- [Deploy Actions](https://learning.postman.com/docs/postman-flows/build-flows/actions/)

**API Documentation**:
- [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)

---

## License

MIT License - See LICENSE file for details

---

## Contact

**Team**: Relay

**GitHub**: https://github.com/V-prajit/relay

**Deployment**: Live on DigitalOcean

---

**Built with Postman Flows + AI-powered automation**

*Transforming vague PM specs into actionable engineering tasks.*
