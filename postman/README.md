# PM Copilot - Postman Workspace

This directory contains all Postman Flows, collections, mock servers, and environment configurations for the PM Copilot project.

## 📁 Structure

```
postman/
├── collections/              # API request collections
│   ├── ripgrep-api.json     # Code search API
│   ├── claude-api.json      # Claude Messages API
│   ├── github-api.json      # GitHub PR creation
│   └── slack-webhooks.json  # Slack notifications
├── mock-servers/            # Mock server definitions
│   └── code-samples.json    # Sample code responses
├── environments/            # Environment variables
│   └── pm-copilot-env.json  # Development environment
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Import Collections

1. Open **Postman Desktop** (v11.42.3+)
2. Click **Import** in the top left
3. Select **Folder** and choose the `postman/collections` directory
4. All 4 collections will be imported

### 2. Set Up Environment

1. Click **Import** → **File**
2. Select `postman/environments/pm-copilot-env.json`
3. Click on **Environments** in the left sidebar
4. Select **PM Copilot Environment**
5. Fill in the required values:
   - `CLAUDE_API_KEY`: Your Anthropic API key
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `SLACK_WEBHOOK_PM`: Your Slack webhook URL for PM notifications
   - `SLACK_WEBHOOK_ENG`: Your Slack webhook URL for engineer notifications
   - `REPO_OWNER`: Your GitHub username or organization
   - `REPO_NAME`: Your repository name

### 3. Create Mock Server

1. Import `postman/mock-servers/code-samples.json`
2. Right-click the collection → **Mock Collection**
3. Name: `Code Samples Mock Server`
4. Keep default settings → **Create Mock Server**
5. Copy the mock server URL
6. Add to environment as `MOCK_SERVER_URL`

### 4. Test Collections

**Test Ripgrep API:**
1. Start the ripgrep-api server: `cd ripgrep-api && npm run dev`
2. Open **Ripgrep API** collection
3. Send **Health Check** request → Should return `200 OK`
4. Send **Search Code** request → Should return file matches

**Test Claude API:**
1. Open **Claude API** collection
2. Send **Generate PR** request → Should return PR content

**Test GitHub API:**
1. Open **GitHub API** collection
2. Send **List Pull Requests** → Should return open PRs (if any)
3. **Note**: Don't create PRs yet (requires branch setup)

**Test Slack Webhooks:**
1. Open **Slack Webhooks** collection
2. Send **Send PM Notification** → Should post to Slack channel

## 🔧 Environment Variables

### Required Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `RIPGREP_API_URL` | Default | Ripgrep API endpoint | `http://localhost:3001` |
| `CLAUDE_API_KEY` | Secret | Anthropic API key | `sk-ant-...` |
| `GITHUB_TOKEN` | Secret | GitHub PAT with `repo` scope | `ghp_...` |
| `SLACK_WEBHOOK_PM` | Secret | Slack webhook for PM | `https://hooks.slack.com/...` |
| `SLACK_WEBHOOK_ENG` | Secret | Slack webhook for Engineer | `https://hooks.slack.com/...` |
| `REPO_OWNER` | Default | GitHub repo owner | `yourusername` |
| `REPO_NAME` | Default | GitHub repo name | `test-repo` |
| `MOCK_SERVER_URL` | Default | Mock server base URL | `https://abc123.mock.pstmn.io` |

### Getting API Keys

**Claude API Key:**
1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Go to **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-`)

**GitHub Token:**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. **Generate new token (classic)**
3. Scopes: `repo` (full control of private repositories)
4. Copy the token (starts with `ghp_`)

**Slack Webhooks:**
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. **Create New App** → **From scratch**
3. Enable **Incoming Webhooks**
4. **Add New Webhook to Workspace**
5. Select channel → Copy webhook URL

## 📦 Collections Overview

### 1. Ripgrep API

**Purpose:** Search codebase for patterns

**Endpoints:**
- `POST /api/search` - Search for pattern in code
- `GET /api/types` - Get supported file types
- `GET /api/health` - Health check

**Example Request:**
```json
POST {{RIPGREP_API_URL}}/api/search
{
  "query": "ProfileCard",
  "path": "src/",
  "type": "tsx"
}
```

### 2. Claude API

**Purpose:** Generate PR content with AI

**Endpoints:**
- `POST /v1/messages` - Generate PR description, code, acceptance criteria

**Example Request:**
```json
POST https://api.anthropic.com/v1/messages
{
  "model": "claude-sonnet-4.5-20250929",
  "max_tokens": 4000,
  "messages": [{
    "role": "user",
    "content": "Generate PR for ProfileCard feature..."
  }]
}
```

### 3. GitHub API

**Purpose:** Create and manage pull requests

**Endpoints:**
- `POST /repos/:owner/:repo/pulls` - Create PR
- `GET /repos/:owner/:repo/pulls` - List PRs
- `GET /repos/:owner/:repo/pulls/:number` - Get PR details

**Example Request:**
```json
POST https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls
{
  "title": "Add ProfileCard",
  "body": "PR description",
  "head": "feature/profile-card",
  "base": "main"
}
```

### 4. Slack Webhooks

**Purpose:** Send notifications to Slack

**Endpoints:**
- `POST {{SLACK_WEBHOOK_PM}}` - Notify PM
- `POST {{SLACK_WEBHOOK_ENG}}` - Notify Engineer

**Example Request:**
```json
POST {{SLACK_WEBHOOK_PM}}
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "✅ PR Created"
      }
    }
  ]
}
```

## 🎭 Mock Server

The **Code Samples Mock Server** provides test data for:
- Sample component code
- Sample route implementations
- Test data and fixtures
- Feature request examples

**Usage in Flows:**
```
GET {{MOCK_SERVER_URL}}/samples/ProfileCard
→ Returns sample ProfileCard component code
```

## 🌊 Building the Main Flow

### Flow Architecture

```
1. Request Block (webhook input)
     ↓
2. AI Agent Block (parse intent)
     ↓
3. HTTP Block → Ripgrep API
     ↓
4. HTTP Block → Mock Server (optional)
     ↓
5. HTTP Block → Claude API
     ↓
6. HTTP Block → GitHub API
     ↓
7. HTTP Block → Slack Webhook
     ↓
8. Response Block (return JSON)
```

### Creating the Flow

**In Postman:**
1. Click **Flows** in the left sidebar
2. **Create Flow** → Name: `PM Copilot Main Flow`
3. Drag blocks from the left panel:
   - 1x **Request** block
   - 2x **AI Agent** blocks
   - 4x **HTTP Request** blocks
   - 1x **Response** block
4. Connect blocks in sequence
5. Configure each block (see below)

### Block Configuration

**Request Block:**
- Automatically captures webhook data
- Outputs: `body`, `headers`, `params`

**AI Agent Block #1 (Intent Parser):**
- Model: GPT-5
- Prompt:
  ```
  Parse this PM feature request and extract:
  1. feature_name (short identifier)
  2. search_keywords (for code search)
  3. acceptance_criteria (3-5 bullets)
  4. target_route (URL path)

  Input: {workflow.request.body.text}
  Output: JSON with keys [feature_name, search_keywords, acceptance_criteria, target_route]
  ```

**HTTP Block #1 (Ripgrep API):**
- Method: POST
- URL: `{{RIPGREP_API_URL}}/api/search`
- Body:
  ```json
  {
    "query": "{{ai_agent.search_keywords}}",
    "path": "src/",
    "type": "tsx"
  }
  ```

**HTTP Block #2 (Mock Server):**
- Method: GET
- URL: `{{MOCK_SERVER_URL}}/samples/ProfileCard`
- Optional: For demo purposes

**HTTP Block #3 (Claude API):**
- Method: POST
- URL: `https://api.anthropic.com/v1/messages`
- Headers:
  ```
  x-api-key: {{CLAUDE_API_KEY}}
  anthropic-version: 2023-06-01
  ```
- Body:
  ```json
  {
    "model": "claude-sonnet-4.5-20250929",
    "max_tokens": 4000,
    "messages": [{
      "role": "user",
      "content": "Generate PR for: {{ai_agent.feature_name}}\nFiles: {{ripgrep.data.files}}"
    }]
  }
  ```

**HTTP Block #4 (GitHub API):**
- Method: POST
- URL: `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls`
- Headers:
  ```
  Authorization: Bearer {{GITHUB_TOKEN}}
  Accept: application/vnd.github+json
  ```
- Body: Extract from Claude response

**HTTP Block #5 (Slack):**
- Method: POST
- URL: `{{SLACK_WEBHOOK_PM}}`
- Body: Slack Block Kit JSON

**Response Block:**
- Input: Connect from final HTTP block
- Returns final JSON to webhook caller

### Deploy as Action

1. Click **Deploy** in top right
2. **Deploy New Version**
3. Copy the **Action URL**
4. Use this URL as Slack slash command endpoint

## 🧪 Testing the Flow

### Manual Test

1. In the Flow editor, click **Run**
2. Provide test input:
   ```json
   {
     "text": "Add ProfileCard to /users",
     "user_id": "@alice"
   }
   ```
3. Watch blocks execute in sequence
4. Check **Analytics** tab for tool call logs

### Webhook Test

```bash
curl -X POST {your-action-url} \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add dark mode toggle to settings",
    "user_id": "@bob"
  }'
```

## 📊 Flows Analytics

**View Analytics:**
1. Open the Flow
2. Click **Analytics** tab
3. View:
   - Run history
   - Tool call logs
   - System prompts
   - Response times
   - Error traces

## 🔧 Troubleshooting

### "Collection not found" error
- Re-import the collection
- Check environment is selected

### Ripgrep API connection failed
- Verify `ripgrep-api` server is running
- Check `RIPGREP_API_URL` in environment

### Claude API 401 Unauthorized
- Verify `CLAUDE_API_KEY` is correct
- Check API key is active at console.anthropic.com

### GitHub PR creation fails
- Verify `GITHUB_TOKEN` has `repo` scope
- Ensure branch exists before creating PR
- Check `REPO_OWNER` and `REPO_NAME` are correct

### Slack webhook returns "channel_not_found"
- Re-create webhook in Slack
- Verify webhook URL is complete (including `/services/...`)

### Flow doesn't execute
- Check all blocks are connected
- Verify environment variables are set
- Review Analytics tab for errors

## 📚 Resources

**Postman Docs:**
- [Flows Overview](https://learning.postman.com/docs/postman-flows/overview/)
- [AI Agent Block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Deploy Actions](https://learning.postman.com/docs/postman-flows/build-flows/actions/)
- [Mock Servers](https://learning.postman.com/docs/design-apis/mock-apis/overview/)

**API Docs:**
- [Claude API](https://docs.claude.com/en/api/messages)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Slack Block Kit](https://docs.slack.dev/block-kit/)

## 💡 Tips

**Best Practices:**
- Keep secrets in environment (never hardcode)
- Use descriptive block names
- Add comments to complex blocks
- Test each HTTP block individually first
- Use mock server for safe testing

**Performance:**
- Set timeouts on HTTP blocks (30s recommended)
- Add retry logic for critical blocks
- Use Decision blocks for error handling
- Monitor Analytics for slow blocks

## 🎯 Next Steps

1. ✅ Import all collections
2. ✅ Configure environment variables
3. ✅ Test individual API requests
4. ✅ Create mock server
5. ✅ Build main Postman Flow
6. ✅ Deploy as Action
7. ✅ Integrate with Slack
8. ✅ Demo to judges!

## 📧 Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review [CLAUDE.md](../CLAUDE.md) for architecture details
- See [docs/SETUP.md](../docs/SETUP.md) for detailed setup

## License

MIT - See [LICENSE](../LICENSE) for details
