# PM Copilot Flow Modules

## Overview
Reusable Flow Modules for PM Copilot workflow. These modules are building blocks that can be used independently or chained together in the main workflow.

---

## Module 1: search-code-module

**Purpose:** Search codebase for files related to keywords

**Inputs:**
- `query` (string): Search keywords (e.g., "ProfileCard", "authentication")

**Outputs:**
- `files` (array): List of matching file paths
- `total` (number): Count of files found
- `success` (boolean): True if search succeeded

**Example:**

Input:
```json
{
  "query": "ProfileCard"
}
```

Output:
```json
{
  "files": ["src/components/ProfileCard.tsx", "src/styles/ProfileCard.css"],
  "total": 2,
  "success": true
}
```

**How it works:**
1. Takes search query from input
2. Calls Ripgrep API with search parameters
3. Returns list of matching files with total count

**Usage in main flow:**
Use this module to find all files related to a feature request before checking for conflicts.

---

## Module 2: check-conflicts-module

**Purpose:** Detect if open PRs conflict with target files

**Inputs:**
- `files` (array): Files to check for conflicts (e.g., ["src/auth.ts", "src/login.tsx"])
- `repo_owner` (string): GitHub repository owner (e.g., "myusername")
- `repo_name` (string): Repository name (e.g., "myapp")

**Outputs:**
- `has_conflict` (boolean): True if conflicts detected
- `conflict_count` (number): Number of conflicting PRs found
- `conflicting_prs` (array): List of conflicting PR objects with details

**Example:**

Input:
```json
{
  "files": ["src/auth.ts", "src/login.tsx"],
  "repo_owner": "johndoe",
  "repo_name": "my-app"
}
```

Output:
```json
{
  "has_conflict": true,
  "conflict_count": 2,
  "conflicting_prs": [
    {
      "number": 123,
      "title": "Fix OAuth bug",
      "user": {"login": "alice"},
      "changed_files": 3
    }
  ]
}
```

**How it works:**
1. Fetches all open PRs from GitHub API
2. Filters PRs that have changed files (potential conflicts)
3. Returns conflict analysis with PR details

**Usage in main flow:**
Call this after searching for files to determine if the new PR will conflict with existing work.

---

## Module 3: generate-pr-module

**Purpose:** Use Claude AI to generate PR content

**Inputs:**
- `feature_name` (string): Name of the feature to implement
- `files` (array): List of files that will be modified
- `acceptance_criteria` (array): Requirements/acceptance criteria

**Outputs:**
- `pr_title` (string): Generated PR title
- `pr_body` (string): Generated PR description
- `code_changes` (string): Suggested code changes (≤30 lines)

**Example:**

Input:
```json
{
  "feature_name": "Dark mode toggle",
  "files": ["src/components/Settings.tsx", "src/styles/theme.ts"],
  "acceptance_criteria": [
    "Add toggle button in settings",
    "Save preference to localStorage",
    "Apply theme on page load"
  ]
}
```

Output:
```json
{
  "pr_title": "feat: Add dark mode toggle to settings",
  "pr_body": "This PR adds a dark mode toggle button to the settings page. The user's preference is saved to localStorage and applied on page load.\n\n## Changes\n- Added DarkModeToggle component\n- Updated theme context\n- Added localStorage persistence\n\n## Acceptance Criteria\n- ✅ Add toggle button in settings\n- ✅ Save preference to localStorage\n- ✅ Apply theme on page load",
  "code_changes": "// DarkModeToggle.tsx\nexport const DarkModeToggle = () => {\n  const [isDark, setIsDark] = useState(false);\n  // ... implementation\n}"
}
```

**How it works:**
1. Constructs prompt for Claude API with feature details
2. Sends request to Claude API
3. Parses response to extract title, description, and code
4. Returns structured PR content

**Usage in main flow:**
Call this after conflict detection to generate the actual PR content using AI.

---

## Module 4: create-pr-module

**Purpose:** Create the actual GitHub Pull Request

**Inputs:**
- `title` (string): PR title
- `body` (string): PR description/body
- `branch` (string): Branch name (e.g., "feature/dark-mode-2025-01-15-abc123")
- `repo_owner` (string): GitHub repository owner
- `repo_name` (string): Repository name

**Outputs:**
- `pr_url` (string): URL to the created PR
- `pr_number` (number): PR number (e.g., 123)
- `success` (boolean): True if PR created successfully

**Example:**

Input:
```json
{
  "title": "feat: Add dark mode toggle",
  "body": "This PR adds dark mode functionality...",
  "branch": "feature/dark-mode-2025-01-15-abc123",
  "repo_owner": "johndoe",
  "repo_name": "my-app"
}
```

Output:
```json
{
  "pr_url": "https://github.com/johndoe/my-app/pull/123",
  "pr_number": 123,
  "success": true
}
```

**How it works:**
1. Takes PR content from previous module
2. Calls GitHub API to create pull request
3. Returns PR URL and number for reference

**Usage in main flow:**
Call this after generating PR content to actually create the PR on GitHub.

---

## Module 5: notify-team-module

**Purpose:** Send Slack notification about the created PR

**Inputs:**
- `message` (string): Main notification message
- `pr_url` (string): Link to the GitHub PR
- `webhook_url` (string): Slack webhook URL

**Outputs:**
- `success` (boolean): True if notification sent
- `timestamp` (string): When notification was sent

**Example:**

Input:
```json
{
  "message": "✅ PR created: Dark mode toggle feature",
  "pr_url": "https://github.com/johndoe/my-app/pull/123",
  "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

Output:
```json
{
  "success": true,
  "timestamp": "2025-01-15T14:30:00Z"
}
```

**How it works:**
1. Takes message and PR URL
2. Formats as Slack Block Kit message with clickable button
3. Sends to Slack webhook
4. Returns success status

**Usage in main flow:**
Call this as the final step to notify the team that the PR has been created.

---

## Module Integration Flow

Here's how these modules work together in the main PM Copilot flow:

```
1. PM makes request ("Add dark mode toggle")
   ↓
2. search-code-module: Find related files
   ↓
3. check-conflicts-module: Check for PR conflicts
   ↓
4. generate-pr-module: Use Claude to generate PR
   ↓
5. create-pr-module: Create PR on GitHub
   ↓
6. notify-team-module: Send Slack notification
```

## Testing

Each module should be tested independently before integration:

1. Create a test flow for each module
2. Provide sample inputs
3. Verify outputs match expected format
4. Check error handling

## Error Handling

All modules should handle errors gracefully:
- Invalid inputs → Return error with clear message
- API failures → Return success: false with error details
- Timeouts → Retry with exponential backoff

## Environment Variables Required

Make sure these are set in your Postman environment:
- `RIPGREP_API_URL`: URL for local Ripgrep API
- `GITHUB_TOKEN`: GitHub personal access token
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `SLACK_WEBHOOK_URL`: Slack webhook URL

## File Locations

Exported modules should be saved to:
```
postman/modules/
├── search-code-module.json
├── check-conflicts-module.json
├── generate-pr-module.json
├── create-pr-module.json
└── notify-team-module.json
```

## Support

If you encounter issues:
1. Test the module in isolation first
2. Check environment variables are set correctly
3. Verify API endpoints are accessible
4. Review Postman Console for detailed error messages

---

**Created by DEV 2 for PM Copilot Hackathon**
