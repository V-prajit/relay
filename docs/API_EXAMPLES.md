# API Examples: You Are Absolutely Right - PM Copilot

This document provides detailed examples for all API integrations used in the PM Copilot system.

---

## 1. Ripgrep API

**Base URL:** `http://localhost:3001` (local) or your deployed URL

### 1.1 Health Check

**Request:**
```bash
curl http://localhost:3001/api/health
```

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-10-25T12:00:00.000Z"
}
```

---

### 1.2 Search Code

**Endpoint:** `POST /api/search`

**Request:**
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ProfileCard",
    "path": "src/",
    "type": "tsx",
    "case_sensitive": false
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "files": [
      "src/components/ProfileCard.tsx",
      "src/pages/UserProfile.tsx"
    ],
    "matches": [
      {
        "file": "src/components/ProfileCard.tsx",
        "line": 15,
        "content": "export const ProfileCard = ({ user }: Props) => {"
      },
      {
        "file": "src/pages/UserProfile.tsx",
        "line": 8,
        "content": "import { ProfileCard } from '@/components/ProfileCard';"
      }
    ],
    "total": 2
  },
  "timestamp": "2025-10-25T12:00:00.000Z"
}
```

---

### 1.3 Search with Case Sensitivity

**Request:**
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CONST",
    "path": "src/",
    "case_sensitive": true
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "files": [],
    "matches": [],
    "total": 0
  },
  "timestamp": "2025-10-25T12:00:00.000Z"
}
```

---

### 1.4 Search All File Types

**Request:**
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "export default",
    "path": "."
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "files": [
      "src/index.ts",
      "src/components/Header.tsx",
      "src/utils/helper.js"
    ],
    "matches": [
      {
        "file": "src/index.ts",
        "line": 42,
        "content": "export default app;"
      }
    ],
    "total": 3
  }
}
```

---

### 1.5 Error: Invalid Query

**Request:**
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "success": false,
  "error": "Query parameter is required",
  "timestamp": "2025-10-25T12:00:00.000Z"
}
```

---

## 2. Claude API

**Base URL:** `https://api.anthropic.com/v1`

### 2.1 Generate PR Content

**Endpoint:** `POST /messages`

**Request:**
```bash
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4.5-20250929",
    "max_tokens": 4000,
    "messages": [
      {
        "role": "user",
        "content": "You are a senior engineer. Generate a ≤30-line PR patch that adds a ProfileCard component to the /users route. Use TypeScript and React 19. Include:\n1. PR title\n2. PR description\n3. Code changes (≤30 lines)\n4. Acceptance criteria (3-5 bullets)\n\nImpacted files: src/pages/users.tsx, src/components/ProfileCard.tsx"
      }
    ]
  }'
```

**Response:**
```json
{
  "id": "msg_01ABC123",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "# PR: Add ProfileCard to /users route\n\n## Summary\nImplements a new ProfileCard component to display user information on the /users page.\n\n## Changes\n\n**src/components/ProfileCard.tsx** (New file):\n```tsx\nimport React from 'react';\n\ninterface ProfileCardProps {\n  user: {\n    id: string;\n    name: string;\n    avatar: string;\n  };\n}\n\nexport const ProfileCard: React.FC<ProfileCardProps> = ({ user }) => (\n  <div className=\"profile-card\">\n    <img src={user.avatar} alt={user.name} />\n    <h3>{user.name}</h3>\n  </div>\n);\n```\n\n**src/pages/users.tsx** (Modified):\n```tsx\nimport { ProfileCard } from '@/components/ProfileCard';\n\n// Add to render:\n{users.map(user => <ProfileCard key={user.id} user={user} />)}\n```\n\n## Acceptance Criteria\n- [ ] ProfileCard component displays user avatar and name\n- [ ] Component is properly typed with TypeScript\n- [ ] /users route renders ProfileCard for each user\n- [ ] Component has basic styling\n- [ ] Snapshot tests cover ProfileCard component"
    }
  ],
  "model": "claude-sonnet-4.5-20250929",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 125,
    "output_tokens": 287
  }
}
```

---

### 2.2 Generate Bug Fix PR

**Request:**
```bash
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4.5-20250929",
    "max_tokens": 4000,
    "messages": [
      {
        "role": "user",
        "content": "Generate a ≤30-line PR patch to fix a memory leak in the dashboard analytics component. File: src/components/Dashboard.tsx. Include cleanup in useEffect."
      }
    ]
  }'
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "# PR: Fix memory leak in Dashboard analytics\n\n## Summary\nAdds cleanup logic to Dashboard component to prevent memory leaks from analytics subscription.\n\n## Changes\n\n**src/components/Dashboard.tsx**:\n```tsx\nuseEffect(() => {\n  const subscription = analytics.subscribe(handleUpdate);\n  \n  // Add cleanup\n  return () => {\n    subscription.unsubscribe();\n  };\n}, []);\n```\n\n## Acceptance Criteria\n- [ ] Analytics subscription cleaned up on unmount\n- [ ] No memory leaks in DevTools profiler\n- [ ] Dashboard still receives analytics updates\n- [ ] Tests verify cleanup is called"
    }
  ]
}
```

---

### 2.3 Error: Rate Limit

**Response:**
```json
{
  "type": "error",
  "error": {
    "type": "rate_limit_error",
    "message": "Rate limit exceeded. Please wait before making more requests."
  }
}
```

**Solution:** Wait 60 seconds and retry.

---

## 3. GitHub API

**Base URL:** `https://api.github.com`

### 3.1 List Pull Requests

**Endpoint:** `GET /repos/{owner}/{repo}/pulls`

**Request:**
```bash
curl -X GET https://api.github.com/repos/yourusername/youareabsolutelyright/pulls \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28"
```

**Response:**
```json
[
  {
    "id": 123456,
    "number": 42,
    "state": "open",
    "title": "Add ProfileCard to /users route",
    "body": "## Summary\nImplements ProfileCard component...",
    "html_url": "https://github.com/yourusername/youareabsolutelyright/pull/42",
    "created_at": "2025-10-25T12:00:00Z",
    "user": {
      "login": "yourusername"
    }
  }
]
```

---

### 3.2 Create Pull Request

**Endpoint:** `POST /repos/{owner}/{repo}/pulls`

**Request:**
```bash
curl -X POST https://api.github.com/repos/yourusername/youareabsolutelyright/pulls \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Add ProfileCard to /users route",
    "body": "## Summary\nImplements ProfileCard component\n\n## Acceptance Criteria\n- [ ] ProfileCard displays avatar\n- [ ] /users route updated\n- [ ] Tests pass",
    "head": "feature/profile-card",
    "base": "main"
  }'
```

**Response:**
```json
{
  "id": 123456,
  "number": 42,
  "state": "open",
  "title": "Add ProfileCard to /users route",
  "html_url": "https://github.com/yourusername/youareabsolutelyright/pull/42",
  "created_at": "2025-10-25T12:00:00Z"
}
```

---

### 3.3 Error: Branch Doesn't Exist

**Response:**
```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "resource": "PullRequest",
      "code": "invalid",
      "field": "head"
    }
  ]
}
```

**Solution:** Create the branch first:
```bash
git checkout -b feature/profile-card
git push origin feature/profile-card
```

---

## 4. Slack Incoming Webhooks

**Base URL:** `https://hooks.slack.com/services/...` (your webhook URL)

### 4.1 Simple Text Message

**Request:**
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "text": "PR Created: Add ProfileCard to /users"
  }'
```

**Response:**
```
ok
```

**Slack Output:**
```
PR Created: Add ProfileCard to /users
```

---

### 4.2 Block Kit Message (Full Featured)

**Request:**
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "blocks": [
      {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": "✅ PR Created: profile-card"
        }
      },
      {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*Feature:*\nProfileCard component"
          },
          {
            "type": "mrkdwn",
            "text": "*Impacted Files:*\n2"
          }
        ]
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Acceptance Criteria:*\n• ProfileCard displays avatar\n• /users route updated\n• Tests pass"
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
            "url": "https://github.com/yourusername/youareabsolutelyright/pull/42",
            "style": "primary"
          }
        ]
      }
    ]
  }'
```

**Slack Output:**
```
╔════════════════════════════════════════╗
║ ✅ PR Created: profile-card            ║
╠════════════════════════════════════════╣
║ Feature: ProfileCard component         ║
║ Impacted Files: 2                      ║
║                                        ║
║ Acceptance Criteria:                   ║
║ • ProfileCard displays avatar          ║
║ • /users route updated                 ║
║ • Tests pass                           ║
║                                        ║
║ [View PR]                              ║
╚════════════════════════════════════════╝
```

---

### 4.3 Message with Sections and Dividers

**Request:**
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "🚀 *PM Copilot Impact Analysis Complete*"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "fields": [
          {
            "type": "mrkdwn",
            "text": "*Status:*\nSuccess"
          },
          {
            "type": "mrkdwn",
            "text": "*Duration:*\n3.2s"
          }
        ]
      }
    ]
  }'
```

---

### 4.4 Error Notification

**Request:**
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "blocks": [
      {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": "⚠️ PR Creation Failed"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Error:* Branch `feature/profile-card` does not exist\n*Feature:* ProfileCard component\n*User:* @alice"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "_Retrying in 10 seconds..._"
        }
      }
    ]
  }'
```

---

## 5. Postman Action (Deployed Flow)

**Base URL:** `https://flows-action.postman.com/{your-action-id}`

### 5.1 Trigger PM Copilot Flow

**Request:**
```bash
curl -X POST https://flows-action.postman.com/abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add ProfileCard component to /users route",
    "user_id": "@alice"
  }'
```

**Response:**
```json
{
  "success": true,
  "feature": "profile-card",
  "pr_url": "https://github.com/yourusername/youareabsolutelyright/pull/42",
  "impacted_files": [
    "src/components/ProfileCard.tsx",
    "src/pages/users.tsx"
  ],
  "acceptance_criteria": [
    "ProfileCard displays user avatar and name",
    "Component renders on /users route",
    "Snapshot tests cover component"
  ]
}
```

---

### 5.2 Complex Feature Request

**Request:**
```bash
curl -X POST https://flows-action.postman.com/abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Implement OAuth2 login flow with GitHub provider",
    "user_id": "@bob"
  }'
```

**Response:**
```json
{
  "success": true,
  "feature": "oauth2-github",
  "pr_url": "https://github.com/yourusername/youareabsolutelyright/pull/43",
  "impacted_files": [
    "src/auth/oauth.ts",
    "src/config/providers.ts",
    "src/pages/login.tsx"
  ],
  "acceptance_criteria": [
    "OAuth2 flow redirects to GitHub authorization",
    "Access token stored securely after callback",
    "User profile fetched from GitHub API",
    "Login page shows GitHub button",
    "Error handling for failed auth"
  ]
}
```

---

### 5.3 Bug Fix Request

**Request:**
```bash
curl -X POST https://flows-action.postman.com/abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Fix memory leak in dashboard analytics component",
    "user_id": "@charlie"
  }'
```

**Response:**
```json
{
  "success": true,
  "feature": "fix-dashboard-leak",
  "pr_url": "https://github.com/yourusername/youareabsolutelyright/pull/44",
  "impacted_files": [
    "src/components/Dashboard.tsx"
  ],
  "acceptance_criteria": [
    "Analytics subscription cleaned up on unmount",
    "No memory leaks in DevTools profiler",
    "Dashboard still receives analytics updates",
    "Tests verify cleanup is called"
  ]
}
```

---

## 6. Mock Server

**Base URL:** `https://abc123.mock.pstmn.io` (your mock server URL)

### 6.1 Get Sample Code

**Endpoint:** `GET /samples/:component`

**Request:**
```bash
curl https://abc123.mock.pstmn.io/samples/ProfileCard
```

**Response:**
```json
{
  "component": "ProfileCard",
  "code": "import React from 'react';\n\ninterface ProfileCardProps {\n  user: {\n    id: string;\n    name: string;\n    avatar: string;\n  };\n}\n\nexport const ProfileCard: React.FC<ProfileCardProps> = ({ user }) => (\n  <div className=\"profile-card\">\n    <img src={user.avatar} alt={user.name} />\n    <h3>{user.name}</h3>\n  </div>\n);",
  "tests": "describe('ProfileCard', () => {\n  it('renders user name', () => {\n    const user = { id: '1', name: 'Alice', avatar: 'url' };\n    render(<ProfileCard user={user} />);\n    expect(screen.getByText('Alice')).toBeInTheDocument();\n  });\n});"
}
```

---

### 6.2 Get Sample Test Data

**Request:**
```bash
curl https://abc123.mock.pstmn.io/samples/testData
```

**Response:**
```json
{
  "users": [
    {
      "id": "1",
      "name": "Alice Johnson",
      "avatar": "https://i.pravatar.cc/150?img=1"
    },
    {
      "id": "2",
      "name": "Bob Smith",
      "avatar": "https://i.pravatar.cc/150?img=2"
    }
  ]
}
```

---

## 7. Integration Examples

### 7.1 Complete Flow: Slack → Action → All APIs

**Step 1: Slack Slash Command**
```
/impact Add dark mode toggle to settings
```

**Step 2: Postman Action Receives**
```json
{
  "text": "Add dark mode toggle to settings",
  "user_id": "@dana",
  "channel_id": "C123ABC"
}
```

**Step 3: AI Agent Parses**
```json
{
  "feature_name": "dark-mode-toggle",
  "search_keywords": "dark mode theme settings",
  "acceptance_criteria": [
    "Toggle switch in settings page",
    "Dark mode CSS applied globally",
    "Preference persisted in localStorage",
    "Smooth theme transition animation"
  ],
  "target_route": "/settings"
}
```

**Step 4: Ripgrep API Searches**
```json
{
  "files": [
    "src/pages/settings.tsx",
    "src/styles/theme.css"
  ],
  "total": 2
}
```

**Step 5: Claude Generates PR**
```json
{
  "content": [{
    "text": "# PR: Add dark-mode-toggle\n\n## Changes\n..."
  }]
}
```

**Step 6: GitHub Creates PR**
```json
{
  "html_url": "https://github.com/.../pull/45",
  "number": 45
}
```

**Step 7: Slack Notifies**
```
✅ PR Created: dark-mode-toggle
[View PR]
```

**Total Time:** ~5-7 seconds

---

### 7.2 Error Recovery Flow

**Scenario:** Ripgrep API is down

**Step 1-3:** Same as above

**Step 4: Ripgrep API Error**
```json
{
  "error": "ECONNREFUSED"
}
```

**Step 5: Fallback to Mock Server**
```json
{
  "files": ["src/components/Settings.tsx"],
  "total": 1,
  "source": "mock"
}
```

**Step 6-8:** Continue normally

**Result:** Flow completes despite API failure

---

## 8. Testing Checklist

Use these examples to verify your setup:

### Ripgrep API
- [ ] Health check returns 200
- [ ] Search finds existing code
- [ ] Search returns empty for nonexistent code
- [ ] Case-sensitive search works
- [ ] Type filtering works (tsx, js, etc.)

### Claude API
- [ ] Generates PR content
- [ ] Follows ≤30-line constraint
- [ ] Includes acceptance criteria
- [ ] Handles complex features
- [ ] Handles bug fix requests

### GitHub API
- [ ] Lists existing PRs
- [ ] Creates new PR (with valid branch)
- [ ] Returns 422 for invalid branch
- [ ] Returns PR URL

### Slack Webhooks
- [ ] Simple text message works
- [ ] Block Kit message renders correctly
- [ ] Buttons are clickable
- [ ] Messages appear in correct channel

### Postman Action
- [ ] Accepts POST requests
- [ ] Returns structured JSON
- [ ] Completes in <10 seconds
- [ ] Handles errors gracefully

### Mock Server
- [ ] Returns sample code
- [ ] Returns test data
- [ ] Public URL accessible

---

## Resources

- **Ripgrep API Docs:** See `ripgrep-api/README.md`
- **Claude API Docs:** https://docs.claude.com/en/api/messages
- **GitHub API Docs:** https://docs.github.com/en/rest
- **Slack Block Kit:** https://api.slack.com/block-kit
- **Postman Flows:** https://learning.postman.com/docs/postman-flows/

---

**Last Updated:** 2025-10-25
**Maintainer:** PM Copilot Team
