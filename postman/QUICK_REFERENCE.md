# Quick Reference: Flow Module Configurations

Copy-paste ready configurations for each flow module.

---

## 1. Ripgrep Search Tool

**Inputs:** `query`, `path`, `type`

**HTTP Request:**
- Method: `POST`
- URL: `{{RIPGREP_API_URL}}/api/search`
- Body:
```json
{
  "query": "{{query}}",
  "path": "{{path}}",
  "type": "{{type}}",
  "case_sensitive": false
}
```

**Output:** `files`, `total`, `is_new_feature`

---

## 2. Get Open PRs Tool

**Inputs:** `state`, `per_page`

**HTTP Request:**
- Method: `GET`
- URL: `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls?state={{state}}&per_page={{per_page}}`
- Headers:
```
Authorization: Bearer {{GITHUB_TOKEN}}
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

**Output:** `prs`, `count`

---

## 3. Get PR Files Tool

**Inputs:** `pr_number`

**HTTP Request:**
- Method: `GET`
- URL: `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls/{{pr_number}}/files`
- Headers: (same as above)

**Evaluate Block:**
```javascript
const files = data['Send Request'].body;
const filenames = files.map(f => f.filename);
return {
  files: filenames,
  count: filenames.length
};
```

**Output:** `files`, `count`

---

## 4. Claude Generate PR Tool

**Inputs:** `feature_request`, `impacted_files`, `is_new_feature`, `conflict_info`

**Evaluate Block (Build Prompt):**
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

**HTTP Request:**
- Method: `POST`
- URL: `https://api.anthropic.com/v1/messages`
- Headers:
```
x-api-key: {{CLAUDE_API_KEY}}
anthropic-version: 2023-06-01
Content-Type: application/json
```
- Body:
```json
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

**Output:** `pr_content`, `branch_name`

---

## 5. Create GitHub PR Tool

**Inputs:** `title`, `body`, `branch_name`

**HTTP Request:**
- Method: `POST`
- URL: `https://api.github.com/repos/{{REPO_OWNER}}/{{REPO_NAME}}/pulls`
- Headers:
```
Authorization: Bearer {{GITHUB_TOKEN}}
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
Content-Type: application/json
```
- Body:
```json
{
  "title": "{{title}}",
  "body": "{{body}}\n\n---\n🤖 Generated with PM Copilot",
  "head": "{{branch_name}}",
  "base": "main"
}
```

**Output:** `pr_url`, `pr_number`

---

## 6. Send Slack Notification Tool

**Inputs:** `feature_name`, `pr_number`, `pr_url`, `impacted_files`, `conflict_detected`, `conflict_score`, `reasoning_trace`

**Evaluate Block:**
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

**HTTP Request:**
- Method: `POST`
- URL: `{{SLACK_WEBHOOK_PM}}`
- Body: `{{Evaluate}}`

**Output:** `success`

---

## Environment Variables Needed

Make sure these are set in your Postman environment:

| Variable | Example Value |
|----------|--------------|
| `RIPGREP_API_URL` | `http://localhost:3001` |
| `CLAUDE_API_KEY` | `sk-ant-...` |
| `GITHUB_TOKEN` | `ghp_...` |
| `SLACK_WEBHOOK_PM` | `https://hooks.slack.com/services/...` |
| `REPO_OWNER` | `your-username` |
| `REPO_NAME` | `your-repo-name` |

---

## Block Connection Pattern

For each module:
```
Start → [Evaluate (optional)] → Send Request → [Evaluate (optional)] → Output
```

All connections use the **Success** port from each block.

---

## Snapshot Reminder

After creating each flow:
1. Click settings icon (⚙️)
2. Go to **"Snapshots"** tab
3. Click **"Create Snapshot"**
4. Name it **"v1"**
5. Click **"Save"**

Without a snapshot, the flow won't appear as a tool option!
