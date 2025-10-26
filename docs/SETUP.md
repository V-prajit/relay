# PM Copilot - Complete Setup Guide

This guide will walk you through setting up the entire PM Copilot system from scratch.

## Prerequisites

### Required Software
- ✅ **Node.js** 18+ ([nodejs.org](https://nodejs.org))
- ✅ **Postman Desktop** v11.42.3+ ([postman.com/downloads](https://www.postman.com/downloads/))
- ✅ **Git** ([git-scm.com](https://git-scm.com/))
- ✅ **Code Editor** (VS Code recommended)

### Required Accounts
- ✅ **Anthropic** - Claude API access ([console.anthropic.com](https://console.anthropic.com))
- ✅ **GitHub** - For PR creation ([github.com](https://github.com))
- ✅ **Slack** - For notifications ([slack.com](https://slack.com))

## Part 1: Clone and Install

### 1.1 Clone Repository

```bash
git clone https://github.com/yourusername/youareabsolutelyright.git
cd youareabsolutelyright
```

### 1.2 Install Ripgrep API Dependencies

```bash
cd ripgrep-api
npm install
```

**Expected output:**
```
added 150 packages in 5s
```

### 1.3 Configure Ripgrep API

```bash
cp .env.example .env
```

Edit `.env` (defaults are fine for most cases):
```bash
PORT=3001
NODE_ENV=development
ALLOWED_ORIGINS=*
MAX_SEARCH_RESULTS=50
```

### 1.4 Test Ripgrep API

**Start server:**
```bash
npm run dev
```

**Expected output:**
```
╔════════════════════════════════════════════╗
║        Ripgrep API Server Running         ║
╠════════════════════════════════════════════╣
║  Port:        3001                        ║
║  Environment: development                 ║
║  CORS:        *                           ║
╚════════════════════════════════════════════╝
```

**Test in another terminal:**
```bash
curl http://localhost:3001/api/health
```

**Expected response:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-10-25T..."
}
```

✅ **Ripgrep API is working!** Leave it running.

## Part 2: API Keys Setup

### 2.1 Get Claude API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Click **API Keys** in the left sidebar
4. Click **Create Key**
5. Name: `PM Copilot`
6. Copy the key (starts with `sk-ant-api-...`)

**Save this key** - you'll need it in Part 3.

### 2.2 Get GitHub Personal Access Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Note: `PM Copilot Token`
4. Scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click **Generate token**
6. Copy the token (starts with `ghp_...`)

**Save this token** - you'll need it in Part 3.

### 2.3 Create Slack App

**Step 1: Create App**
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App**
3. Choose **From scratch**
4. App Name: `PM Copilot`
5. Workspace: Select your workspace
6. Click **Create App**

**Step 2: Enable Incoming Webhooks**
1. In the left sidebar, click **Incoming Webhooks**
2. Toggle **Activate Incoming Webhooks** to **On**
3. Scroll down, click **Add New Webhook to Workspace**
4. Select channel: `#pm-notifications` (or create new channel)
5. Click **Allow**
6. Copy the **Webhook URL** (starts with `https://hooks.slack.com/...`)

**Repeat for Engineer Notifications:**
1. **Add New Webhook to Workspace**
2. Select channel: `#engineering` (or create new channel)
3. Copy the second webhook URL

**Save both webhook URLs** - you'll need them in Part 3.

### 2.4 Optional: Slack Slash Command

**If you want `/impact` command:**
1. In Slack App settings, click **Slash Commands**
2. Click **Create New Command**
3. Command: `/impact`
4. Request URL: `{your-postman-action-url}` (we'll add this later)
5. Short Description: `Generate PR from PM spec`
6. Usage Hint: `[feature description]`
7. Click **Save**

**Note:** We'll update the Request URL after deploying the Postman Action in Part 4.

## Part 3: Postman Setup

### 3.1 Import Collections

1. Open **Postman Desktop**
2. Click **Import** (top left)
3. Click **Folder**
4. Navigate to `youareabsolutelyright/postman/collections`
5. Select the folder and click **Open**
6. 4 collections imported:
   - ✅ Ripgrep API
   - ✅ Claude API
   - ✅ GitHub API
   - ✅ Slack Webhooks

### 3.2 Import Environment

1. Click **Import** → **File**
2. Navigate to `youareabsolutelyright/postman/environments`
3. Select `pm-copilot-env.json`
4. Click **Open**

### 3.3 Configure Environment Variables

1. Click **Environments** in the left sidebar
2. Select **PM Copilot Environment**
3. Fill in the values:

| Variable | Your Value |
|----------|-----------|
| `RIPGREP_API_URL` | `http://localhost:3001` ✅ (default) |
| `CLAUDE_API_KEY` | `sk-ant-api-...` (from Part 2.1) |
| `GITHUB_TOKEN` | `ghp_...` (from Part 2.2) |
| `SLACK_WEBHOOK_PM` | `https://hooks.slack.com/...` (from Part 2.3) |
| `SLACK_WEBHOOK_ENG` | `https://hooks.slack.com/...` (from Part 2.3) |
| `REPO_OWNER` | Your GitHub username |
| `REPO_NAME` | `test-repo` (or your test repository) |
| `MOCK_SERVER_URL` | Leave blank for now |

4. Click **Save**

### 3.4 Create Mock Server

1. Click **Import** → **File**
2. Select `youareabsolutelyright/postman/mock-servers/code-samples.json`
3. Right-click **Code Samples Mock Server** collection
4. Select **Mock Collection**
5. Name: `Code Samples Mock`
6. ✅ Make mock server public
7. Click **Create Mock Server**
8. **Copy the mock server URL** (e.g., `https://abc123.mock.pstmn.io`)
9. Go back to **Environments** → **PM Copilot Environment**
10. Set `MOCK_SERVER_URL` to the copied URL
11. Click **Save**

### 3.5 Test Individual Collections

**Select Environment:**
- In the top right, ensure **PM Copilot Environment** is selected

**Test Ripgrep API:**
1. Open **Ripgrep API** collection
2. Click **Health Check**
3. Click **Send**
4. ✅ Status: `200 OK`, Body: `{"success": true}`

**Test Claude API:**
1. Open **Claude API** collection
2. Click **Generate PR**
3. Click **Send**
4. ✅ Status: `200 OK`, Body contains PR content

**Test GitHub API:**
1. Open **GitHub API** collection
2. Click **List Pull Requests**
3. Click **Send**
4. ✅ Status: `200 OK`, Body: `[]` (empty list is fine)

**Test Slack Webhooks:**
1. Open **Slack Webhooks** collection
2. Click **Send PM Notification**
3. Click **Send**
4. ✅ Status: `200 OK`, Body: `ok`
5. **Check Slack** - you should see a message in `#pm-notifications`!

**All green?** ✅ Collections working!

## Part 4: Build the Main Flow

### 4.1 Create New Flow

1. In Postman, click **Flows** in the left sidebar
2. Click **Create Flow**
3. Name: `PM Copilot Main Flow`
4. Click **Create**

### 4.2 Add Blocks

**Drag these blocks from the left panel:**
1. **Request** block (automatically added for Actions)
2. **AI Agent** block (for intent parsing)
3. **HTTP Request** block (for Ripgrep API)
4. **HTTP Request** block (for Mock Server)
5. **HTTP Request** block (for Claude API)
6. **HTTP Request** block (for GitHub API)
7. **HTTP Request** block (for Slack)
8. **Response** block (automatically added for Actions)

### 4.3 Configure Block 1: Request Block

- Already configured by default
- Outputs: `body`, `headers`, `params`
- No configuration needed

### 4.4 Configure Block 2: AI Agent (Intent Parser)

1. Click the **AI Agent** block
2. Model: Select **GPT-5** (default)
3. Prompt:
   ```
   You are a PM Copilot assistant. Parse this feature request and extract structured data.

   Input: {workflow.request.body.text}

   Extract:
   1. feature_name: Short identifier (e.g., "profile-card")
   2. search_keywords: Keywords for code search (e.g., "ProfileCard component")
   3. acceptance_criteria: Array of 3-5 bullet points describing what to build
   4. target_route: Target URL route (e.g., "/users")

   Output ONLY valid JSON in this exact format:
   {
     "feature_name": "...",
     "search_keywords": "...",
     "acceptance_criteria": ["...", "...", "..."],
     "target_route": "..."
   }
   ```
4. Context: Add variable
   - Label: `feature_request`
   - Value: `{{request.body.text}}`

### 4.5 Configure Block 3: HTTP Request (Ripgrep API)

1. Click the **HTTP Request** block
2. Method: **POST**
3. URL: `{{RIPGREP_API_URL}}/api/search`
4. Headers:
   ```
   Content-Type: application/json
   ```
5. Body (raw JSON):
   ```json
   {
     "query": "{{ai_agent.search_keywords}}",
     "path": "src/",
     "type": "tsx",
     "case_sensitive": false
   }
   ```
6. Connect: `AI Agent` output → This block input

### 4.6 Configure Block 4: HTTP Request (Mock Server)

1. Method: **GET**
2. URL: `{{MOCK_SERVER_URL}}/samples/ProfileCard`
3. No headers or body needed
4. Connect: Previous block → This block (sequential)

### 4.7 Configure Block 5: HTTP Request (Claude API)

1. Method: **POST**
2. URL: `https://api.anthropic.com/v1/messages`
3. Headers:
   ```
   x-api-key: {{CLAUDE_API_KEY}}
   anthropic-version: 2023-06-01
   Content-Type: application/json
   ```
4. Body (raw JSON):
   ```json
   {
     "model": "claude-sonnet-4.5-20250929",
     "max_tokens": 4000,
     "messages": [
       {
         "role": "user",
         "content": "You are a senior engineer. Generate a ≤30-line PR patch for this feature:\n\nFeature: {{ai_agent.feature_name}}\nRoute: {{ai_agent.target_route}}\nImpacted files: {{ripgrep.data.files}}\n\nProvide:\n1. PR title\n2. PR description with summary\n3. Code changes (≤30 lines total)\n4. Acceptance criteria\n\nUse TypeScript and React 19. Format as markdown with code blocks."
       }
     ]
   }
   ```
5. Connect: Previous block → This block

### 4.8 Configure Block 6: HTTP Request (GitHub API)

**Note:** This is simplified. You'll need to parse Claude's response to extract PR title/body.

1. Method: **POST**
2. URL: `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls`
3. Headers:
   ```
   Authorization: Bearer {{GITHUB_TOKEN}}
   Accept: application/vnd.github+json
   X-GitHub-Api-Version: 2022-11-28
   Content-Type: application/json
   ```
4. Body (simplified - adjust based on Claude output):
   ```json
   {
     "title": "Add {{ai_agent.feature_name}} to {{ai_agent.target_route}}",
     "body": "{{claude.content[0].text}}\n\n## Impacted Files\n{{ripgrep.data.files}}",
     "head": "feature/{{ai_agent.feature_name}}",
     "base": "main"
   }
   ```
5. Connect: Previous block → This block

**Important:** For PR creation to work, the branch `feature/{feature_name}` must exist. For demo, you can skip this block or create a test branch manually.

### 4.9 Configure Block 7: HTTP Request (Slack)

1. Method: **POST**
2. URL: `{{SLACK_WEBHOOK_PM}}`
3. Headers:
   ```
   Content-Type: application/json
   ```
4. Body (raw JSON):
   ```json
   {
     "blocks": [
       {
         "type": "header",
         "text": {
           "type": "plain_text",
           "text": "✅ PR Created: {{ai_agent.feature_name}}"
         }
       },
       {
         "type": "section",
         "fields": [
           {
             "type": "mrkdwn",
             "text": "*Feature:*\n{{ai_agent.feature_name}}"
           },
           {
             "type": "mrkdwn",
             "text": "*Impacted Files:*\n{{ripgrep.data.total}}"
           }
         ]
       },
       {
         "type": "section",
         "text": {
           "type": "mrkdwn",
           "text": "*Acceptance Criteria:*\n{{ai_agent.acceptance_criteria}}"
         }
       },
       {
         "type": "actions",
         "elements": [
           {
             "type": "button",
             "text": {
               "type": "plain_text",
               "text": "View PR"
             },
             "url": "{{github.html_url}}",
             "style": "primary"
           }
         ]
       }
     ]
   }
   ```
5. Connect: Previous block → This block

### 4.10 Configure Block 8: Response Block

1. Click the **Response** block
2. Status Code: `200`
3. Body:
   ```json
   {
     "success": true,
     "feature": "{{ai_agent.feature_name}}",
     "pr_url": "{{github.html_url}}",
     "impacted_files": "{{ripgrep.data.files}}",
     "acceptance_criteria": "{{ai_agent.acceptance_criteria}}"
   }
   ```
4. Connect: Previous block → This block

### 4.11 Test the Flow

1. Click **Run** in the top right
2. Provide test input:
   ```json
   {
     "text": "Add ProfileCard component to /users route",
     "user_id": "@alice"
   }
   ```
3. Click **Run**
4. Watch blocks execute (they'll light up green/red)
5. Check **Analytics** tab for detailed logs

**Expected result:**
- ✅ AI Agent parses intent
- ✅ Ripgrep API returns file matches (or empty if no files)
- ✅ Mock server returns sample code
- ✅ Claude generates PR content
- ⚠️ GitHub PR may fail if branch doesn't exist (OK for demo)
- ✅ Slack receives notification

### 4.12 Deploy as Action

1. Click **Deploy** in the top right
2. Click **Deploy New Version**
3. ✅ Flow deployed!
4. **Copy the Action URL** (e.g., `https://flows-action.postman.com/abc123`)

**Save this URL** - this is your public endpoint!

### 4.13 Update Slack Slash Command (Optional)

If you created `/impact` command in Part 2.4:

1. Go back to [api.slack.com/apps](https://api.slack.com/apps)
2. Select your **PM Copilot** app
3. Click **Slash Commands**
4. Click the `/impact` command
5. Update **Request URL** to your Postman Action URL
6. Click **Save**

## Part 5: End-to-End Test

### Test from curl

```bash
curl -X POST {your-action-url} \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add dark mode toggle to settings",
    "user_id": "@bob"
  }'
```

**Expected:**
1. ⏱️ Wait 5-10 seconds...
2. ✅ JSON response with PR URL and impacted files
3. ✅ Slack notification appears in `#pm-notifications`

### Test from Slack (if slash command configured)

In Slack:
```
/impact Add search bar to navigation
```

**Expected:**
1. ⏱️ "Working on it..." (if you add ack logic)
2. ✅ Slack message with PR details
3. ✅ Check GitHub - PR created (if branch exists)

## Part 6: Verify Setup

### Checklist

**Ripgrep API:**
- [ ] Server running on port 3001
- [ ] Health check returns 200 OK
- [ ] Can search for patterns

**Postman Collections:**
- [ ] All 4 collections imported
- [ ] Environment variables configured
- [ ] Mock server created and URL saved
- [ ] All test requests succeed

**Main Flow:**
- [ ] 8 blocks added and configured
- [ ] Connections made between blocks
- [ ] Test run succeeds (or shows expected failures)
- [ ] Deployed as Action
- [ ] Action URL copied

**Integrations:**
- [ ] Slack notifications working
- [ ] Claude API returning PR content
- [ ] GitHub API accessible (PR creation may need branch)
- [ ] Mock server returning sample data

**Optional:**
- [ ] Slack slash command configured
- [ ] Test repository created with branches

## Troubleshooting

### Ripgrep API won't start

**Error: `Cannot find module '@vscode/ripgrep'`**
```bash
cd ripgrep-api
rm -rf node_modules package-lock.json
npm install
```

**Error: `Port 3001 already in use`**
```bash
# Change port in .env
PORT=3002
```

### Postman Flow errors

**"Variable not found"**
- Check variable names match block outputs
- Use `{{block_name.field_name}}` syntax
- Review Analytics tab for exact variable names

**HTTP Request timeouts**
- Increase timeout to 30s in block settings
- Check API endpoints are accessible
- Verify environment variables are set

### Claude API errors

**401 Unauthorized**
- Check `CLAUDE_API_KEY` in environment
- Verify key is active at console.anthropic.com
- Ensure `x-api-key` header (not `Authorization`)

**429 Rate Limit**
- You've exceeded free tier limits
- Wait 60 seconds or upgrade plan

### GitHub API errors

**404 Not Found**
- Check `REPO_OWNER` and `REPO_NAME` are correct
- Verify repository exists and is accessible

**422 Validation Failed**
- Branch `feature/{name}` must exist before creating PR
- Create a test branch manually:
  ```bash
  git checkout -b feature/test
  git push origin feature/test
  ```

### Slack webhook errors

**"channel_not_found"**
- Recreate webhook at api.slack.com/apps
- Ensure webhook URL is complete

**"invalid_payload"**
- Check JSON syntax in Block Kit payload
- Validate at api.slack.com/block-kit

## Next Steps

1. ✅ Setup complete!
2. See [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) for judge demo
3. See [API_EXAMPLES.md](./API_EXAMPLES.md) for more examples
4. See [../CLAUDE.md](../CLAUDE.md) for architecture details

## Support

Issues? Check:
- [Postman Learning Center](https://learning.postman.com)
- [Claude API Docs](https://docs.claude.com)
- [Slack API Docs](https://api.slack.com)
- [GitHub API Docs](https://docs.github.com/rest)

---

**Setup time:** 30-45 minutes
**Difficulty:** Intermediate
**Prerequisites:** Basic API knowledge, Node.js familiarity
