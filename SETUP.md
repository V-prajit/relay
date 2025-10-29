# Relay Setup Guide

Complete installation and configuration instructions for deploying Relay from scratch.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Ripgrep API Setup](#ripgrep-api-setup)
3. [Postman Flow Setup](#postman-flow-setup)
4. [Slack App Configuration](#slack-app-configuration)
5. [Action Deployment](#action-deployment)
6. [Testing](#testing)
7. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required Software

- **Node.js**: Version 18 or later
- **npm**: Version 9 or later
- **Postman Desktop**: Version 11.42.3 or later
- **Git**: For cloning repositories
- **curl**: For testing API endpoints

### Required Accounts

- **GitHub**: Personal account with ability to create repositories
- **Slack**: Workspace with admin privileges
- **Postman**: Account with Flows access
- **DigitalOcean** (optional): For production deployment

### Required Credentials

1. **GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Copy token (starts with `ghp_`)

2. **Slack Webhook URL**:
   - Created during Slack app setup (see below)

---

## Ripgrep API Setup

The Ripgrep API provides fast code search functionality.

### 1. Clone Repository

```bash
git clone https://github.com/V-prajit/relay.git
cd relay/ripgrep-api
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```bash
# Server Configuration
PORT=3001

# GitHub Repository Configuration
REPO_OWNER=V-prajit
REPO_NAME=postman-api-toolkit

# Search Configuration
CLONE_DIR=/tmp/ripgrep-repo-cache
MAX_SEARCH_RESULTS=50
ALLOWED_ORIGINS=*
```

**Configuration Details**:
- `PORT`: Local server port (default 3001, avoid conflicts with other services)
- `REPO_OWNER`: GitHub username or organization
- `REPO_NAME`: Repository to search
- `CLONE_DIR`: Temporary directory for repository clones
- `MAX_SEARCH_RESULTS`: Maximum files returned per search
- `ALLOWED_ORIGINS`: CORS configuration (use `*` for development, restrict in production)

### 4. Start Development Server

```bash
npm run dev
```

Expected output:

```
Ripgrep API listening on port 3001
Repository will be cloned to: /tmp/ripgrep-repo-cache
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:3001/api/health

# Expected response:
# {"success":true,"status":"healthy","service":"Ripgrep API"}

# Test search
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"import"}'

# Expected response:
# {"success":true,"data":{"files":[...],"total":5,"is_new_feature":false}}
```

---

## Postman Flow Setup

### 1. Install Postman Desktop

Download from [postman.com/downloads](https://www.postman.com/downloads/) and install.

**Minimum version**: 11.42.3 (required for TypeScript support in Evaluate blocks)

### 2. Import Flow Modules

Flow Modules are reusable sub-workflows that the main Action calls.

**Steps**:

1. Open Postman Desktop
2. Navigate to **Flows** tab in left sidebar
3. Click **Import** button
4. Select all module files from `postman/modules/` directory:
   - `ripgrep-search-module.json`
   - `get-open-prs-module.json`
   - `get-pr-files-module.json`
   - `claude-generate-pr-module.json`
   - `create-github-issue-module.json`
   - `send-slack-notification-module.json`

5. For each imported collection:
   - Right-click the collection name
   - Select **"Create Flow Module"**
   - Confirm module creation

**Verification**: Check that all 6 modules appear in the **Modules** section of Postman Flows.

### 3. Create Main Action Flow

**Steps**:

1. Click **"+ Create New Flow"**
2. Name it: `"Process API request and generate AI response"`
3. Add blocks in this order:

**Block Configuration**:

#### A. Request Block

- Drag **Request** block from left panel
- This is the entry point for Slack webhooks
- No configuration needed (automatically receives HTTP POST data)

#### B. Evaluate Block (Array Flattening)

- Drag **Evaluate** block after Request
- Wire: `Request → Body → Evaluate → data`
- Click Evaluate block → Select **TypeScript** mode
- Enter code:

```typescript
const flatten = (obj: Record<string, any>) =>
  Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [k, Array.isArray(v) ? v[0] : v])
  );

flatten(data);
```

**Purpose**: Converts Slack's array-wrapped values (`{text: ["hello"]}`) to strings (`{text: "hello"}`).

#### C. Validate Block

- Drag **Validate** block after Evaluate
- Wire: `Evaluate → Result → Validate → Data`
- Click Validate block → Enter schema:

```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": ["text"]
}
```

**Purpose**: Ensures `text` field is present and non-empty before proceeding.

#### D. Response Block

- Drag **Response** block
- Wire: `Validate → Pass → Response`
- Configure Response:
  - **Status Code**: `202`
  - **Headers**: `{}` (empty object)
  - **Body**:
    ```json
    {
      "success": true,
      "message": "Workflow triggered"
    }
    ```

**Purpose**: Returns immediate 202 Accepted to Slack (before background work completes).

#### E. Get Configuration Block

- Drag **Get Configuration** block
- Wire: `Validate → Pass → Get Configuration`
- Click block → Add configuration:
  - **Key**: `GITHUB_PAT`
  - **Type**: `Secret`
  - **Value**: Your GitHub personal access token (from Prerequisites)

**Purpose**: Securely retrieve GitHub token for API calls.

#### F. Module Block

- Drag the **"Search using RIPGREP API and process AI responses"** module (created in step 2)
- Wire inputs:
  - `Validate → Pass → text (extract text field) → Module → text`
  - `Get Configuration → GITHUB_PAT → Module → github_token`

**Purpose**: Execute background workflow (search code, generate issue, create on GitHub).

**Final Flow Structure**:

```
Request → Evaluate → Validate → Fork (Validate.Pass connects to both):
                                   ├─→ Response (202)
                                   └─→ Module (background)
                                        Get Configuration → Module.github_token
```

### 4. Configure Module Internals

Open the **"Search using RIPGREP API and process AI responses"** module and verify:

**Module Inputs** (should already be configured):
- `text` (string)
- `github_token` (string)

**Module Flow**:

1. **HTTP Request** → Ripgrep API:
   - URL: `https://pm-copilot-ripgrep-api.ondigitalocean.app/api/search`
   - Method: `POST`
   - Headers: `Content-Type: application/json`
   - Body:
     ```json
     {
       "query": "{{Start.text}}"
     }
     ```

2. **HTTP Request** → GitHub Get Open PRs:
   - URL: `https://api.github.com/repos/V-prajit/postman-api-toolkit/pulls?state=open`
   - Method: `GET`
   - Headers:
     ```json
     {
       "Authorization": "Bearer {{github_token}}",
       "Accept": "application/vnd.github.v3+json"
     }
     ```
   - **Variables** section: Wire `Start.github_token → variables.github_token`

3. **HTTP Request** → Generate Issue Content:
   - This could call Snowflake backend (optional) or use a simpler template generation
   - See SNOWFLAKE_MLH.md for optional AI-powered generation

4. **HTTP Request** → GitHub Create Issue:
   - URL: `https://api.github.com/repos/V-prajit/postman-api-toolkit/issues`
   - Method: `POST`
   - Headers:
     ```json
     {
       "Authorization": "Bearer {{github_token}}",
       "Accept": "application/vnd.github.v3+json",
       "Content-Type": "application/json"
     }
     ```
   - Body:
     ```json
     {
       "title": "{{generated_title}}",
       "body": "{{generated_description}}"
     }
     ```
   - **Variables** section: Wire `Start.github_token → variables.github_token`

5. **HTTP Request** → Slack Webhook:
   - URL: Your Slack incoming webhook URL
   - Method: `POST`
   - Body:
     ```json
     {
       "text": "GitHub issue created: #{{issue_number}}",
       "blocks": [
         {
           "type": "section",
           "text": {
             "type": "mrkdwn",
             "text": "*Issue Created:* <{{issue_url}}|#{{issue_number}} - {{issue_title}}>"
           }
         }
       ]
     }
     ```

**Critical Detail**: Module inputs (text, github_token) are data ports. To use them as variables in HTTP Request blocks, you must wire them to the **Variables** input section of each HTTP Request block.

---

## Slack App Configuration

### 1. Create Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Enter app name: `"Relay"`
5. Select your workspace
6. Click **"Create App"**

### 2. Configure Slash Command

1. In left sidebar, click **"Slash Commands"**
2. Click **"Create New Command"**
3. Configure:
   - **Command**: `/relay`
   - **Request URL**: Leave blank for now (will add after Action deployment)
   - **Short Description**: `Create GitHub issue from feature request`
   - **Usage Hint**: `<feature description>`
4. Click **"Save"**

### 3. Configure Incoming Webhooks

1. In left sidebar, click **"Incoming Webhooks"**
2. Toggle **"Activate Incoming Webhooks"** to ON
3. Click **"Add New Webhook to Workspace"**
4. Select channel for notifications (e.g., `#new-channel`)
5. Click **"Allow"**
6. Copy the webhook URL (starts with `https://hooks.slack.com/services/...`)

**Save this URL** - you'll need it for Postman module configuration.

### 4. Important Settings

**Socket Mode**: Must be DISABLED

1. In left sidebar, click **"Socket Mode"**
2. Ensure toggle is OFF
3. Socket Mode blocks the Request URL field and prevents webhook integration

**Verification**: Go back to Slash Commands - the Request URL field should now be editable.

### 5. Install App to Workspace

1. In left sidebar, click **"Install App"**
2. Click **"Install to Workspace"**
3. Review permissions
4. Click **"Allow"**

---

## Action Deployment

Deploy the Postman Flow as a publicly accessible Action.

### 1. Deploy Flow

1. Open your main Flow in Postman
2. Click **"Deploy"** button (top right)
3. Select **"Create new snapshot"** (important: not "Redeploy")
4. Name snapshot: `v1-array-flatten` (or current date)
5. Click **"Deploy"**
6. Wait for deployment to complete (usually 10-30 seconds)

### 2. Copy Action URL

After deployment:

1. Click **"Copy URL"** button
2. URL format: `https://[random].flows.pstmn.io/api/default/[endpoint]`
3. Save this URL

Example: `https://logic-helium-core.flows.pstmn.io/api/default/testing-async-pm-help`

### 3. Update Slack Command

1. Return to [api.slack.com/apps](https://api.slack.com/apps)
2. Select your Relay app
3. Click **"Slash Commands"** in left sidebar
4. Click the pencil icon next to `/relay` command
5. Paste Action URL into **Request URL** field
6. Click **"Save"**

### 4. Verify Action Configuration

In Postman:

1. Click deployed Action name
2. Navigate to **"Action Configuration"** tab
3. Verify `GITHUB_PAT` is listed with type "Secret"
4. If missing, click **"Add Configuration"**:
   - Key: `GITHUB_PAT`
   - Type: `Secret`
   - Value: Your GitHub token

**Important**: Each time you deploy a new snapshot, verify that Action Configuration is preserved.

---

## Testing

### 1. Test Ripgrep API (Local)

```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"ProfileCard","type":"tsx"}'
```

**Expected Response**:

```json
{
  "success": true,
  "data": {
    "files": ["./src/components/ProfileCard.tsx"],
    "total": 1,
    "is_new_feature": false,
    "message": "Found existing files that may be related to this feature."
  }
}
```

### 2. Test Action with cURL

Simulate Slack's form-encoded request:

```bash
curl -X POST 'https://your-action-url.flows.pstmn.io/api/default/endpoint' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'text=test+feature+request+from+curl'
```

**Expected Response** (immediate):

```json
{
  "success": true,
  "message": "Workflow triggered"
}
```

**Background Execution**: Check Postman Analytics (Action → Run History) to see full execution after 10-20 seconds.

### 3. Test in Slack

In any Slack channel where the app is installed:

```
/relay add dark mode toggle to settings
```

**Expected Behavior**:

1. Command input disappears (Slack receives 202 immediately)
2. After 10-20 seconds: Slack notification appears with GitHub issue link
3. Check GitHub: New issue created with title, description, and acceptance criteria

### 4. Verify GitHub Issue

1. Go to your GitHub repository
2. Navigate to **Issues** tab
3. Find the newly created issue
4. Verify:
   - Title matches feature request
   - Description includes acceptance criteria
   - Impacted files are listed (if found by search)

---

## Production Deployment

### Deploy Ripgrep API to DigitalOcean

1. Create DigitalOcean account at [digitalocean.com](https://www.digitalocean.com/)

2. Create new App Platform app:
   - Click **"Create App"**
   - Select **"GitHub"** as source
   - Authorize DigitalOcean to access your repository
   - Select repository: `V-prajit/relay`
   - Select source directory: `ripgrep-api`

3. Configure build settings:
   - **Build Command**: `npm install`
   - **Run Command**: `npm start`
   - **Port**: `3001`

4. Add environment variables:
   ```
   PORT=3001
   REPO_OWNER=V-prajit
   REPO_NAME=postman-api-toolkit
   CLONE_DIR=/tmp/ripgrep-repo-cache
   MAX_SEARCH_RESULTS=50
   ALLOWED_ORIGINS=*
   ```

5. Click **"Deploy"**

6. After deployment, copy the public URL (e.g., `https://pm-copilot-ripgrep-api.ondigitalocean.app`)

7. Update Postman Flow module:
   - Open Ripgrep API HTTP Request block
   - Replace URL with production URL

8. Redeploy Postman Action:
   - Click **"Deploy"** → **"Create new snapshot"** → Name: `v2-production-ripgrep`

### Update Production Environment Variables

In Postman:

1. Create new environment: `"Production"`
2. Add variables:
   ```
   RIPGREP_API_URL = https://pm-copilot-ripgrep-api.ondigitalocean.app
   GITHUB_TOKEN = [your token]
   SLACK_WEBHOOK_URL = [your webhook]
   REPO_OWNER = V-prajit
   REPO_NAME = postman-api-toolkit
   ```

3. Select **"Production"** environment before deploying Action

---

## Troubleshooting

See [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for detailed error solutions.

**Common Issues**:

**"Validation failed: must be string"**:
- Ensure Evaluate block is wired correctly
- Check that Validate receives Evaluate.Result (not Request.Body directly)
- Verify TypeScript code in Evaluate has no syntax errors

**"GitHub 401 Unauthorized"**:
- Verify GitHub token has `repo` scope
- Check Action Configuration has `GITHUB_PAT` set as Secret
- Ensure Get Configuration block output is wired to Module input

**"Slack command not showing"**:
- Disable Socket Mode in Slack app settings
- Verify Request URL matches deployed Action URL
- Reinstall app to workspace

**"Module input not accessible in HTTP Request"**:
- Wire module input to HTTP Request block's **Variables** section
- Use `{{variable_name}}` syntax in URL/body after wiring to Variables

**"No GitHub issue created"**:
- Check Postman Action Analytics for error details
- Verify Ripgrep API is accessible from Postman cloud
- Review GitHub API response in Run History

---

## Next Steps

After successful setup:

1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for technical implementation details
2. Explore [ROADMAP.md](./ROADMAP.md) for planned enhancements
3. Review [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for common issues
4. See [SNOWFLAKE_MLH.md](./SNOWFLAKE_MLH.md) for optional AI-powered PR generation

---

## Support

If you encounter issues not covered in this guide:

1. Check [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)
2. Review Postman Flow Analytics (Action → Run History → Details)
3. Check Ripgrep API logs (DigitalOcean → App → Runtime Logs)
4. Create GitHub issue with error details and screenshots

---

## Quick Reference

**Ports**:
- Ripgrep API: 3001
- Snowflake Backend (optional): 8000
- Dashboard API (optional): 3002
- Dashboard Frontend (optional): 3000

**Key URLs**:
- Postman Action: Check Deployment page in Postman Flows
- Slack Webhook: Slack App → Incoming Webhooks
- GitHub API: `https://api.github.com`
- Ripgrep API (production): Check DigitalOcean App Platform

**Configuration Files**:
- Ripgrep API: `ripgrep-api/.env`
- Postman: Environment variables + Action Configuration
- Slack: App configuration at api.slack.com/apps
