# DEV 2: Testing Checklist

Use this checklist to verify each module works correctly before marking your work complete.

---

## Pre-Testing Setup

- [ ] Postman Desktop is open
- [ ] Environment is selected (check top-right dropdown)
- [ ] All environment variables are set:
  - [ ] `RIPGREP_API_URL` = http://localhost:8080 (or your URL)
  - [ ] `GITHUB_TOKEN` = your GitHub personal access token
  - [ ] `CLAUDE_API_KEY` = your Anthropic API key
  - [ ] `SLACK_WEBHOOK_URL` = your Slack webhook URL
- [ ] Ripgrep API is running (if testing Module 1)

---

## MODULE 1: search-code-module

### Creation Checklist
- [ ] Flow created with name "search-code-module"
- [ ] Input block added with property: `query` (string, required)
- [ ] HTTP Request block configured:
  - [ ] Method: POST
  - [ ] URL: `{{RIPGREP_API_URL}}/api/search`
  - [ ] Header: Content-Type: application/json
  - [ ] Body contains: query, path, type, case_sensitive fields
- [ ] Output block with 3 properties: files, total, success
- [ ] Blocks are connected: Input → HTTP → Output
- [ ] Saved as Module (not just saved as flow)
- [ ] Exported to: `postman/modules/search-code-module.json`

### Testing
- [ ] Created test flow: "test-search-code-module"
- [ ] Added Flow Module block, selected search-code-module
- [ ] Test input: `{"query": "ProfileCard"}`
- [ ] Clicked Run button
- [ ] **Result:** Output shows array of files ✅
- [ ] **Result:** Output shows total count ✅
- [ ] **Result:** Output shows success: true ✅
- [ ] No errors in Postman Console

### Expected Output Format
```json
{
  "files": ["src/components/ProfileCard.tsx", ...],
  "total": 2,
  "success": true
}
```

---

## MODULE 2: check-conflicts-module

### Creation Checklist
- [ ] Flow created: "check-conflicts-module"
- [ ] Input block with 3 properties:
  - [ ] `files` (array, required)
  - [ ] `repo_owner` (string, required)
  - [ ] `repo_name` (string, required)
- [ ] HTTP Request block:
  - [ ] Method: GET
  - [ ] URL: `https://api.github.com/repos/{{repo_owner}}/{{repo_name}}/pulls`
  - [ ] Headers: Authorization (Bearer), Accept, X-GitHub-Api-Version
- [ ] Evaluate block with conflict detection logic
- [ ] Output block with: has_conflict, conflict_count, conflicting_prs
- [ ] Saved as Module
- [ ] Exported to: `postman/modules/check-conflicts-module.json`

### Testing
- [ ] Created test flow: "test-check-conflicts-module"
- [ ] Test input:
  ```json
  {
    "files": ["src/auth.ts"],
    "repo_owner": "YOUR_GITHUB_USERNAME",
    "repo_name": "YOUR_REPO_NAME"
  }
  ```
  **⚠️ Replace with your actual GitHub username and repo!**
- [ ] Clicked Run
- [ ] **Result:** Output shows has_conflict (true or false) ✅
- [ ] **Result:** Output shows conflict_count (number) ✅
- [ ] **Result:** Output shows conflicting_prs (array) ✅
- [ ] If repo has open PRs, conflicting_prs should list them

### Expected Output Format
```json
{
  "has_conflict": true,
  "conflict_count": 2,
  "conflicting_prs": [
    {
      "number": 123,
      "title": "Fix bug",
      "user": {"login": "username"},
      "changed_files": 5
    }
  ]
}
```

---

## MODULE 3: generate-pr-module

### Creation Checklist
- [ ] Flow created: "generate-pr-module"
- [ ] Input block with 3 properties:
  - [ ] `feature_name` (string, required)
  - [ ] `files` (array, required)
  - [ ] `acceptance_criteria` (array, required)
- [ ] HTTP Request block (Claude API):
  - [ ] Method: POST
  - [ ] URL: `https://api.anthropic.com/v1/messages`
  - [ ] Headers: x-api-key, anthropic-version, content-type
  - [ ] Body: Contains model, max_tokens, messages with prompt
- [ ] Select or Evaluate block to extract text
- [ ] Evaluate block to parse PR content
- [ ] Output block: pr_title, pr_body, code_changes
- [ ] Saved as Module
- [ ] Exported to: `postman/modules/generate-pr-module.json`

### Testing
- [ ] Created test flow: "test-generate-pr-module"
- [ ] Test input:
  ```json
  {
    "feature_name": "Dark mode toggle",
    "files": ["src/components/Settings.tsx"],
    "acceptance_criteria": ["Add toggle button", "Save to localStorage"]
  }
  ```
- [ ] Clicked Run
- [ ] ⏱️ This takes ~5-10 seconds (Claude API call)
- [ ] **Result:** Output shows pr_title (string starting with feat:/fix:) ✅
- [ ] **Result:** Output shows pr_body (longer description) ✅
- [ ] **Result:** Output shows code_changes ✅
- [ ] Check Postman Console - should see Claude API response

### Expected Output Format
```json
{
  "pr_title": "feat: Add dark mode toggle to settings",
  "pr_body": "This PR adds a dark mode toggle...",
  "code_changes": "// Code here..."
}
```

**Common Issues:**
- If Claude returns error 401: Check `CLAUDE_API_KEY` is correct
- If timeout: Increase timeout in HTTP block settings to 30 seconds
- If empty response: Check max_tokens is set to 4000

---

## MODULE 4: create-pr-module

### Creation Checklist
- [ ] Flow created: "create-pr-module"
- [ ] Input block with 5 properties:
  - [ ] `title` (string, required)
  - [ ] `body` (string, required)
  - [ ] `branch` (string, required)
  - [ ] `repo_owner` (string, required)
  - [ ] `repo_name` (string, required)
- [ ] HTTP Request block:
  - [ ] Method: POST
  - [ ] URL: `https://api.github.com/repos/{{repo_owner}}/{{repo_name}}/pulls`
  - [ ] Headers: Authorization, Accept, X-GitHub-Api-Version, Content-Type
  - [ ] Body: title, body, head (branch), base (main)
- [ ] Output block: pr_url, pr_number, success
- [ ] Saved as Module
- [ ] Exported to: `postman/modules/create-pr-module.json`

### Testing

**⚠️ WARNING: This test will CREATE AN ACTUAL PR on GitHub!**

**Before testing:**
- [ ] Use a test repository (not production!)
- [ ] Create a test branch first:
  ```bash
  git checkout -b test-pm-copilot-123
  git push -u origin test-pm-copilot-123
  ```
- [ ] Or use an existing branch

**Test Steps:**
- [ ] Created test flow: "test-create-pr-module"
- [ ] Test input:
  ```json
  {
    "title": "test: PM Copilot test PR",
    "body": "This is a test PR created by PM Copilot module. Please ignore or close.",
    "branch": "test-pm-copilot-123",
    "repo_owner": "YOUR_GITHUB_USERNAME",
    "repo_name": "YOUR_TEST_REPO"
  }
  ```
- [ ] Clicked Run
- [ ] **Result:** Output shows pr_url ✅
- [ ] **Result:** Output shows pr_number ✅
- [ ] **Result:** Output shows success: true ✅
- [ ] Visited pr_url in browser - PR exists on GitHub ✅

### Expected Output Format
```json
{
  "pr_url": "https://github.com/username/repo/pull/123",
  "pr_number": 123,
  "success": true
}
```

**Common Issues:**
- Error 422 "No commits between main and branch": Branch must have different commits than main
- Error 404: Check repo_owner and repo_name are correct
- Error 403: Check GITHUB_TOKEN has repo permissions

---

## MODULE 5: notify-team-module

### Creation Checklist
- [ ] Flow created: "notify-team-module"
- [ ] Input block with 3 properties:
  - [ ] `message` (string, required)
  - [ ] `pr_url` (string, required)
  - [ ] `webhook_url` (string, required)
- [ ] HTTP Request block:
  - [ ] Method: POST
  - [ ] URL: `{{webhook_url}}`
  - [ ] Header: Content-Type: application/json
  - [ ] Body: Slack Block Kit format with section and button
- [ ] Evaluate block to add timestamp
- [ ] Output block: success, timestamp
- [ ] Saved as Module
- [ ] Exported to: `postman/modules/notify-team-module.json`

### Testing

**⚠️ This will send a REAL message to your Slack channel!**

- [ ] Created test flow: "test-notify-team-module"
- [ ] Test input:
  ```json
  {
    "message": "✅ Test notification from PM Copilot",
    "pr_url": "https://github.com/test/test/pull/1",
    "webhook_url": "{{SLACK_WEBHOOK_URL}}"
  }
  ```
- [ ] Clicked Run
- [ ] **Result:** Output shows success: true ✅
- [ ] **Result:** Output shows timestamp ✅
- [ ] Checked Slack - message appeared in channel ✅
- [ ] Clicked "View PR" button - opens correct URL ✅

### Expected Output Format
```json
{
  "success": true,
  "timestamp": "2025-01-15T14:30:00.000Z"
}
```

**Common Issues:**
- Error 404: Slack webhook URL might be invalid
- Message not appearing: Check which channel the webhook points to
- Button not working: Check pr_url is a valid URL

---

## FINAL VERIFICATION

### All Modules Created
- [ ] search-code-module ✅
- [ ] check-conflicts-module ✅
- [ ] generate-pr-module ✅
- [ ] create-pr-module ✅
- [ ] notify-team-module ✅

### All Files Exported
Check that `postman/modules/` directory contains:
- [ ] search-code-module.json (file exists)
- [ ] check-conflicts-module.json (file exists)
- [ ] generate-pr-module.json (file exists)
- [ ] create-pr-module.json (file exists)
- [ ] notify-team-module.json (file exists)

### File Size Check
- [ ] Each JSON file is > 1 KB (not empty)
- [ ] Files contain valid JSON (open in text editor)
- [ ] No API keys visible in the files (should use {{VARIABLE}})

### Documentation Complete
- [ ] docs/FLOW_MODULES.md exists ✅ (already created)
- [ ] postman/modules/README.md exists ✅ (already created)

### Test Flows Created
- [ ] test-search-code-module
- [ ] test-check-conflicts-module
- [ ] test-generate-pr-module
- [ ] test-create-pr-module
- [ ] test-notify-team-module

**Optional:** Export test flows for reference:
- Helps DEV 1 understand how to use modules
- Helps you debug if something breaks later

---

## HANDOFF TO DEV 1

Once all checklist items are complete, send this message to DEV 1:

```
@dev1 Modules are ready for integration! 🎉

✅ All 5 Flow Modules created and tested
✅ Exported to: postman/modules/*.json
✅ Documentation: docs/FLOW_MODULES.md

Modules available:
1. search-code-module - Search files in codebase
2. check-conflicts-module - Detect PR conflicts
3. generate-pr-module - Generate PR with Claude
4. create-pr-module - Create GitHub PR
5. notify-team-module - Send Slack notification

All tested individually and working. Ready for you to integrate into main flow!

Test flows are in workspace if you want to see examples.
```

---

## Time Tracking

Record your actual time:
- [ ] Module 1 creation: ___ minutes (expected: 15)
- [ ] Module 2 creation: ___ minutes (expected: 15)
- [ ] Module 3 creation: ___ minutes (expected: 20)
- [ ] Module 4 creation: ___ minutes (expected: 20)
- [ ] Module 5 creation: ___ minutes (expected: 15)
- [ ] Testing all modules: ___ minutes (expected: 30)
- [ ] Documentation: ___ minutes (expected: 30)

**Total time:** ___ minutes (expected: 145 min = 2.4 hours)

---

## Troubleshooting Resources

If you get stuck:

1. **Postman Console:** View → Show Postman Console (see detailed errors)
2. **Postman Docs:** learning.postman.com/docs/flows/
3. **Team Slack:** Ask in #pm-copilot-dev channel
4. **This Guide:** docs/DEV2_POSTMAN_GUIDE.md (step-by-step instructions)

---

**You're done when all items in FINAL VERIFICATION are checked! 🚀**
