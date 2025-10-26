# Complete Flow Module Setup Guide

**Goal**: Create 6 flow modules with snapshots so the AI Agent can use them as tools.

**Time Required**: ~30-45 minutes total (5-7 minutes per module)

---

## Pre-Flight Checklist

Before starting, make sure:
- ✅ Postman Desktop is open
- ✅ You're in the correct workspace
- ✅ Ripgrep API is running on `http://localhost:3001`
- ✅ You have your environment variables ready:
  - `RIPGREP_API_URL` = http://localhost:3001
  - `CLAUDE_API_KEY` = your Claude API key
  - `GITHUB_TOKEN` = your GitHub token
  - `SLACK_WEBHOOK_PM` = your Slack webhook URL
  - `REPO_OWNER` = your GitHub username/org
  - `REPO_NAME` = your repository name

---

## Module 1/6: Ripgrep Search Tool

### Create the Flow

1. **Go to Flows** (left sidebar) → Click **"+"** or **"New"**
2. Select **"Create Flow"**
3. Name it: **"Ripgrep Search Tool"**

### Build the Flow

**Add Start Block:**
1. Drag **"Start"** block to canvas
2. Click "Add input"
3. Add these inputs:
   - `query` (String) - Search pattern
   - `path` (String) - Directory path (default: "src/")
   - `type` (String) - File type (default: "tsx")

**Add Send Request Block:**
1. Click **"+ Block"** → Select **"Send Request"**
2. Connect Start block output → Send Request block input
3. Configure the request:

**Request Configuration:**
```
Method: POST
URL: {{RIPGREP_API_URL}}/api/search

Headers:
  Content-Type: application/json

Body (JSON):
{
  "query": "{{query}}",
  "path": "{{path}}",
  "type": "{{type}}",
  "case_sensitive": false
}
```

**Add Output Block:**
1. Click **"+ Block"** → Select **"Output"**
2. Connect Send Request success → Output
3. Configure to return:
   - `files` = `{{Send Request.body.data.files}}`
   - `total` = `{{Send Request.body.data.total}}`
   - `is_new_feature` = `{{Send Request.body.data.is_new_feature}}`

### Create Snapshot

1. Click the **settings icon (⚙️)** or **"Snapshots"** tab
2. Click **"Create Snapshot"**
3. Name it: **"v1"**
4. Click **"Save"**

### Test It

1. Click **"Run"**
2. Enter test values:
   - query: "ProfileCard"
   - path: "src/"
   - type: "tsx"
3. Should return files array

✅ **Module 1 Complete!**

---

## Module 2/6: Get Open PRs Tool

### Create the Flow

1. **Flows** → **"New"** → **"Create Flow"**
2. Name: **"Get Open PRs Tool"**

### Build the Flow

**Add Start Block:**
1. Drag **"Start"** block
2. Add inputs:
   - `state` (String) - PR state (default: "open")
   - `per_page` (Number) - Results per page (default: 10)

**Add Send Request Block:**
1. Add **"Send Request"** block
2. Connect Start → Send Request

**Request Configuration:**
```
Method: GET
URL: https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls?state={{state}}&per_page={{per_page}}

Headers:
  Authorization: Bearer {{GITHUB_TOKEN}}
  Accept: application/vnd.github+json
  X-GitHub-Api-Version: 2022-11-28
```

**Add Output Block:**
1. Add **"Output"** block
2. Connect Send Request success → Output
3. Return:
   - `prs` = `{{Send Request.body}}`
   - `count` = `{{Send Request.body.length}}`

### Create Snapshot

1. Settings → **"Create Snapshot"** → Name: **"v1"**

### Test It

1. Run with:
   - state: "open"
   - per_page: 10
2. Should return array of PRs

✅ **Module 2 Complete!**

---

## Module 3/6: Get PR Files Tool

### Create the Flow

1. **Flows** → **"New"** → **"Create Flow"**
2. Name: **"Get PR Files Tool"**

### Build the Flow

**Add Start Block:**
1. Drag **"Start"** block
2. Add input:
   - `pr_number` (Number) - PR number to fetch files for

**Add Send Request Block:**
1. Add **"Send Request"** block
2. Connect Start → Send Request

**Request Configuration:**
```
Method: GET
URL: https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls/{{pr_number}}/files

Headers:
  Authorization: Bearer {{GITHUB_TOKEN}}
  Accept: application/vnd.github+json
  X-GitHub-Api-Version: 2022-11-28
```

**Add Evaluate Block (Extract Filenames):**
1. Add **"Evaluate"** block
2. Connect Send Request success → Evaluate
3. Add this JavaScript:

```javascript
// Extract just the filenames
const files = data['Send Request'].body;
const filenames = files.map(f => f.filename);

return {
  files: filenames,
  count: filenames.length
};
```

**Add Output Block:**
1. Add **"Output"** block
2. Connect Evaluate → Output
3. Return:
   - `files` = `{{Evaluate.files}}`
   - `count` = `{{Evaluate.count}}`

### Create Snapshot

1. Settings → **"Create Snapshot"** → Name: **"v1"**

### Test It

1. Run with:
   - pr_number: (use a real PR number from your repo)
2. Should return array of file paths

✅ **Module 3 Complete!**

---

## Module 4/6: Claude Generate PR Tool

### Create the Flow

1. **Flows** → **"New"** → **"Create Flow"**
2. Name: **"Claude Generate PR Tool"**

### Build the Flow

**Add Start Block:**
1. Drag **"Start"** block
2. Add inputs:
   - `feature_request` (String) - The feature description
   - `impacted_files` (String) - JSON array of files
   - `is_new_feature` (Boolean) - Whether it's a new feature
   - `conflict_info` (String) - Conflict details

**Add Evaluate Block (Build Prompt):**
1. Add **"Evaluate"** block
2. Connect Start → Evaluate
3. Add this JavaScript:

```javascript
const timestamp = new Date().toISOString().split('T')[0];
const guid = Math.random().toString(36).substring(2, 10);
const featureName = data.Start.feature_request
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .slice(0, 30);

const branchName = `feature/${featureName}-${timestamp}-${guid}`;

const prompt = `You are a senior engineer working on a codebase.

Feature Request: ${data.Start.feature_request}

Impacted Files: ${data.Start.impacted_files}
Is New Feature: ${data.Start.is_new_feature}
Conflict Information: ${data.Start.conflict_info || 'No conflicts'}

IMPORTANT INSTRUCTIONS:
- If this is a NEW FEATURE (no files found), create new files and suggest a file structure
- If files were found, modify those existing files with a ≤30-line patch
- Consider the conflict information when generating changes

Provide:
1. PR Title (clear and concise)
2. PR Description (markdown formatted)
3. Code changes or new file structure
4. Acceptance criteria (3-5 bullet points)

Use TypeScript and React 19. Keep total changes ≤30 lines.`;

return {
  prompt: prompt,
  branch_name: branchName
};
```

**Add Send Request Block (Claude API):**
1. Add **"Send Request"** block
2. Connect Evaluate → Send Request

**Request Configuration:**
```
Method: POST
URL: https://api.anthropic.com/v1/messages

Headers:
  x-api-key: {{CLAUDE_API_KEY}}
  anthropic-version: 2023-06-01
  Content-Type: application/json

Body (JSON):
{
  "model": "claude-sonnet-4.5-20250929",
  "max_tokens": 4000,
  "messages": [
    {
      "role": "user",
      "content": "{{Evaluate.prompt}}"
    }
  ]
}
```

**Add Output Block:**
1. Add **"Output"** block
2. Connect Send Request success → Output
3. Return:
   - `pr_content` = `{{Send Request.body.content[0].text}}`
   - `branch_name` = `{{Evaluate.branch_name}}`

### Create Snapshot

1. Settings → **"Create Snapshot"** → Name: **"v1"**

### Test It

1. Run with:
   - feature_request: "Add dark mode toggle"
   - impacted_files: '["src/Settings.tsx"]'
   - is_new_feature: false
   - conflict_info: "No conflicts"
2. Should return PR content

✅ **Module 4 Complete!**

---

## Module 5/6: Create GitHub PR Tool

### Create the Flow

1. **Flows** → **"New"** → **"Create Flow"**
2. Name: **"Create GitHub PR Tool"**

### Build the Flow

**Add Start Block:**
1. Drag **"Start"** block
2. Add inputs:
   - `title` (String) - PR title
   - `body` (String) - PR description
   - `branch_name` (String) - Branch name

**Add Send Request Block:**
1. Add **"Send Request"** block
2. Connect Start → Send Request

**Request Configuration:**
```
Method: POST
URL: https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls

Headers:
  Authorization: Bearer {{GITHUB_TOKEN}}
  Accept: application/vnd.github+json
  X-GitHub-Api-Version: 2022-11-28
  Content-Type: application/json

Body (JSON):
{
  "title": "{{title}}",
  "body": "{{body}}\n\n---\n🤖 Generated with [PM Copilot](https://github.com/youareabsolutelyright)",
  "head": "{{branch_name}}",
  "base": "main"
}
```

**Add Output Block:**
1. Add **"Output"** block
2. Connect Send Request success → Output
3. Return:
   - `pr_url` = `{{Send Request.body.html_url}}`
   - `pr_number` = `{{Send Request.body.number}}`

### Create Snapshot

1. Settings → **"Create Snapshot"** → Name: **"v1"**

### Test It (Manual)

Note: This requires the branch to exist. You can test after creating a branch, or skip testing for now.

✅ **Module 5 Complete!**

---

## Module 6/6: Send Slack Notification Tool

### Create the Flow

1. **Flows** → **"New"** → **"Create Flow"**
2. Name: **"Send Slack Notification Tool"**

### Build the Flow

**Add Start Block:**
1. Drag **"Start"** block
2. Add inputs:
   - `feature_name` (String)
   - `pr_number` (Number)
   - `pr_url` (String)
   - `impacted_files` (String) - JSON array
   - `conflict_detected` (Boolean)
   - `conflict_score` (Number)
   - `reasoning_trace` (String) - JSON array

**Add Evaluate Block (Build Slack Message):**
1. Add **"Evaluate"** block
2. Connect Start → Evaluate
3. Add this JavaScript:

```javascript
const hasConflict = data.Start.conflict_detected;
const conflictScore = data.Start.conflict_score || 0;
const files = JSON.parse(data.Start.impacted_files || '[]');
const trace = JSON.parse(data.Start.reasoning_trace || '[]');

const conflictBlocks = hasConflict ? [
  {
    type: "section",
    text: {
      type: "mrkdwn",
      text: `:warning: *CONFLICT DETECTED* - Risk: ${conflictScore}%`
    }
  },
  { type: "divider" }
] : [];

const reasoningText = trace.slice(0, 5).map(step => `• ${step}`).join('\n');
const filesText = files.slice(0, 5).map(f => `\`${f}\``).join('\n');

return {
  blocks: [
    ...conflictBlocks,
    {
      type: "header",
      text: {
        type: "plain_text",
        text: `✅ PR Created: ${data.Start.feature_name}`
      }
    },
    {
      type: "section",
      text: {
        type: "mrkdwn",
        text: `*🧠 Agent Reasoning Trace:*\n${reasoningText}`
      }
    },
    {
      type: "section",
      fields: [
        { type: "mrkdwn", text: `*PR:*\n#${data.Start.pr_number}` },
        { type: "mrkdwn", text: `*Files:*\n${files.length}` }
      ]
    },
    {
      type: "section",
      text: {
        type: "mrkdwn",
        text: `*Impacted Files:*\n${filesText}`
      }
    },
    {
      type: "actions",
      elements: [
        {
          type: "button",
          text: { type: "plain_text", text: "View PR" },
          url: data.Start.pr_url,
          style: "primary"
        }
      ]
    }
  ]
};
```

**Add Send Request Block:**
1. Add **"Send Request"** block
2. Connect Evaluate → Send Request

**Request Configuration:**
```
Method: POST
URL: {{SLACK_WEBHOOK_PM}}

Headers:
  Content-Type: application/json

Body (JSON):
{{Evaluate}}
```

**Add Output Block:**
1. Add **"Output"** block
2. Connect Send Request success → Output
3. Return:
   - `success` = `{{Send Request.status == 200}}`

### Create Snapshot

1. Settings → **"Create Snapshot"** → Name: **"v1"**

### Test It

1. Run with sample data:
   - feature_name: "test-feature"
   - pr_number: 123
   - pr_url: "https://github.com/test/test/pull/123"
   - impacted_files: '["src/test.tsx"]'
   - conflict_detected: false
   - conflict_score: 0
   - reasoning_trace: '["Step 1", "Step 2"]'
2. Should send Slack message

✅ **Module 6 Complete!**

---

## Final Step: Configure AI Agent

Now that all 6 flow modules are created with snapshots:

### 1. Go to Your Main Flow

Open **"PM-Copilot-v2"** flow (or create it)

### 2. Click AI Agent Block

Click the AI Agent block to open settings

### 3. Add All Tools

Click **"Add a tool"** and add each:
1. ✅ Ripgrep Search Tool
2. ✅ Get Open PRs Tool
3. ✅ Get PR Files Tool
4. ✅ Claude Generate PR Tool
5. ✅ Create GitHub PR Tool
6. ✅ Send Slack Notification Tool

### 4. Paste System Prompt

Copy the entire prompt from `/postman/AI-AGENT-CONFIGURATION.md` and paste into the **Prompt** field.

### 5. Save

Click **"Save"** on the flow

### 6. Test!

Click **"Run"** and enter:
```json
{
  "text": "Add dark mode toggle to settings",
  "user_id": "@alice"
}
```

Watch the AI Agent automatically call all your tools!

---

## Troubleshooting

### "No tools available" in AI Agent

**Fix**: Make sure each flow module has a snapshot created

### Tool doesn't appear in dropdown

**Fix**: Refresh Postman or check that the flow is in the same workspace

### Request fails with 401/403

**Fix**: Check environment variables are set correctly

---

## Progress Tracking

Update `/CLAUDE.md` as you complete each module:

```
- ✅ Step 1/6: Ripgrep Search Tool - DONE
- ✅ Step 2/6: Get Open PRs Tool - DONE
- ✅ Step 3/6: Get PR Files Tool - DONE
- ✅ Step 4/6: Claude Generate PR Tool - DONE
- ✅ Step 5/6: Create GitHub PR Tool - DONE
- ✅ Step 6/6: Send Slack Notification Tool - DONE
- ⏳ Step 7: Configure AI Agent - IN PROGRESS
```

---

**Total Time**: ~40 minutes for all 6 modules + AI Agent configuration

**Next**: Deploy as Postman Action → Configure Slack → Test end-to-end!
