# DEV 2: Postman Desktop Step-by-Step Guide

**Your Mission:** Create 5 reusable Flow Modules in Postman Desktop

**Time:** 2-3 hours total

---

## Prerequisites Checklist

Before you start, make sure you have:

- [ ] Postman Desktop installed (v11.42.3 or higher)
- [ ] Access to the PM Copilot workspace
- [ ] Environment variables set up:
  - [ ] `RIPGREP_API_URL` (e.g., http://localhost:8080)
  - [ ] `GITHUB_TOKEN` (from GitHub Settings → Developer settings → Personal access tokens)
  - [ ] `CLAUDE_API_KEY` (from console.anthropic.com)
  - [ ] `SLACK_WEBHOOK_URL` (from api.slack.com/apps)

---

## PART 1: CREATE MODULE 1 - Search Code Module (15 minutes)

### Step 1: Open Postman and Create New Flow

1. Open **Postman Desktop**
2. Click on **"Flows"** tab in the left sidebar
3. Click **"New Flow"** button (top right, or center if no flows exist)
4. Name it: `search-code-module`
5. Click **"Create"**

### Step 2: Add Input Block

1. Look at the left sidebar - you'll see "Blocks" panel
2. Find and drag **"Input"** block onto the canvas
3. Click on the Input block to configure it
4. Click **"Add property"** button
5. Configure:
   - **Name:** `query`
   - **Type:** String (dropdown)
   - **Description:** "Search keywords"
   - **Required:** ✅ (check the box)
6. Click outside the block to save

### Step 3: Add HTTP Request Block

1. Drag **"HTTP Request"** block from the left sidebar
2. Place it to the right of the Input block
3. Connect blocks: Click the dot on the right edge of Input block, drag to the left edge of HTTP Request block
4. Click the HTTP Request block to configure:
   - **Method:** POST (dropdown)
   - **URL:** `{{RIPGREP_API_URL}}/api/search`
   - **Headers:** Click "Add Header"
     - Key: `Content-Type`
     - Value: `application/json`
   - **Body:** Select "raw" and "JSON" format
   - Paste this JSON:
     ```json
     {
       "query": "{{query}}",
       "path": "src/",
       "type": "tsx",
       "case_sensitive": false
     }
     ```
5. Name this block: Click the pencil icon at top, rename to "Search API"

### Step 4: Add Output Block

1. Drag **"Output"** block from sidebar
2. Place it to the right of the HTTP Request block
3. Connect HTTP Request → Output
4. Click Output block to configure
5. Click "Add property" for each output:

   **Property 1:**
   - Name: `files`
   - Value: `{{Search API.body.data.files}}`

   **Property 2:**
   - Name: `total`
   - Value: `{{Search API.body.data.total}}`

   **Property 3:**
   - Name: `success`
   - Value: `{{Search API.body.success}}`

### Step 5: Save as Module

1. Click the three dots (⋯) menu in the top right
2. Select **"Save as Module"** (NOT just "Save")
3. Confirm the save

### Step 6: Export Module

1. Click the three dots (⋯) menu again
2. Select **"Export"**
3. Save to: `postman/modules/search-code-module.json`

✅ **MODULE 1 COMPLETE!**

---

## PART 2: CREATE MODULE 2 - Check Conflicts Module (15 minutes)

### Step 1: Create New Flow

1. Go back to Flows list (click "Flows" in left sidebar)
2. Click **"New Flow"**
3. Name: `check-conflicts-module`
4. Click **"Create"**

### Step 2: Add Input Blocks (3 inputs needed)

1. Drag **"Input"** block to canvas
2. Click it and add 3 properties:

   **Property 1:**
   - Name: `files`
   - Type: Array
   - Description: "Files to check for conflicts"
   - Required: ✅

   **Property 2:**
   - Name: `repo_owner`
   - Type: String
   - Description: "GitHub repository owner"
   - Required: ✅

   **Property 3:**
   - Name: `repo_name`
   - Type: String
   - Description: "Repository name"
   - Required: ✅

### Step 3: Add HTTP Request Block (Get Open PRs)

1. Drag **"HTTP Request"** block
2. Connect Input → HTTP Request
3. Configure:
   - **Method:** GET
   - **URL:** `https://api.github.com/repos/{{repo_owner}}/{{repo_name}}/pulls`
   - **Headers:** Add these 3 headers:
     - `Authorization`: `Bearer {{GITHUB_TOKEN}}`
     - `Accept`: `application/vnd.github+json`
     - `X-GitHub-Api-Version`: `2022-11-28`
4. Rename to: "Get Open PRs"

### Step 4: Add Evaluate Block

1. Drag **"Evaluate"** block from sidebar
2. Connect "Get Open PRs" → Evaluate
3. Click Evaluate block
4. In the code editor, paste this JavaScript:

```javascript
// Get data from previous blocks
const openPRs = data['Get Open PRs'].body || [];
const targetFiles = data.files || [];

// Simple conflict detection: if PR has changed files, it's a potential conflict
const conflicts = openPRs.filter(pr => {
  return pr.changed_files > 0;
}).slice(0, 5); // Limit to first 5 PRs

// Return conflict analysis
return {
  has_conflict: conflicts.length > 0,
  conflict_count: conflicts.length,
  conflicting_prs: conflicts
};
```

5. Rename to: "Analyze Conflicts"

### Step 5: Add Output Block

1. Drag **"Output"** block
2. Connect Evaluate → Output
3. Add 3 properties:

   **Property 1:**
   - Name: `has_conflict`
   - Value: `{{Analyze Conflicts.has_conflict}}`

   **Property 2:**
   - Name: `conflict_count`
   - Value: `{{Analyze Conflicts.conflict_count}}`

   **Property 3:**
   - Name: `conflicting_prs`
   - Value: `{{Analyze Conflicts.conflicting_prs}}`

### Step 6: Save and Export

1. Click ⋯ → **"Save as Module"**
2. Click ⋯ → **"Export"**
3. Save to: `postman/modules/check-conflicts-module.json`

✅ **MODULE 2 COMPLETE!**

---

## PART 3: CREATE MODULE 3 - Generate PR Content Module (20 minutes)

### Step 1: Create New Flow

1. Flows → New Flow
2. Name: `generate-pr-module`
3. Create

### Step 2: Add Input Block (3 inputs)

Add these 3 properties to Input block:

1. **Property 1:**
   - Name: `feature_name`
   - Type: String
   - Description: "Name of the feature"
   - Required: ✅

2. **Property 2:**
   - Name: `files`
   - Type: Array
   - Description: "List of files to modify"
   - Required: ✅

3. **Property 3:**
   - Name: `acceptance_criteria`
   - Type: Array
   - Description: "Requirements for the feature"
   - Required: ✅

### Step 3: Add HTTP Request Block (Claude API)

1. Drag HTTP Request block
2. Connect Input → HTTP Request
3. Configure:
   - **Method:** POST
   - **URL:** `https://api.anthropic.com/v1/messages`
   - **Headers:** Add these:
     - `x-api-key`: `{{CLAUDE_API_KEY}}`
     - `anthropic-version`: `2023-06-01`
     - `content-type`: `application/json`
   - **Body:** Select raw JSON, paste:

```json
{
  "model": "claude-sonnet-4.5-20250929",
  "max_tokens": 4000,
  "messages": [{
    "role": "user",
    "content": "Generate a ≤30-line PR for: {{feature_name}}\n\nFiles to modify: {{files}}\n\nAcceptance Criteria: {{acceptance_criteria}}\n\nInclude:\n1. PR title (start with 'feat:', 'fix:', or 'refactor:')\n2. PR description\n3. Code changes (≤30 lines)\n4. How it meets acceptance criteria\n\nFormat as markdown."
  }]
}
```

4. Rename to: "Claude API"

### Step 4: Add Select Block

1. Drag **"Select"** block (if available) OR use Evaluate block
2. Connect Claude API → Select
3. Configure:
   - **Path:** `content[0].text`
   - This extracts the text from Claude's response

**IF Select block doesn't exist**, use **Evaluate block** with this code:
```javascript
const response = data['Claude API'].body;
return response.content[0].text;
```

4. Rename to: "Extract Text"

### Step 5: Add Evaluate Block (Parse Response)

1. Drag **"Evaluate"** block
2. Connect Extract Text → Evaluate
3. Paste this code:

```javascript
// Get Claude's response text
const content = data['Extract Text'] || data['Claude API'].body.content[0].text;

// Simple parsing - extract title and body
const lines = content.split('\n');
const titleLine = lines.find(l => l.toLowerCase().includes('title') || l.includes('feat:') || l.includes('fix:'));

// Extract code if present (between triple backticks)
const codeMatch = content.match(/```[\s\S]*?```/);
const code = codeMatch ? codeMatch[0] : '';

return {
  pr_title: titleLine ? titleLine.replace(/[#*]/g, '').trim() : 'feat: ' + data.feature_name,
  pr_body: content.substring(0, 500),
  code_changes: code || 'Code changes to be implemented'
};
```

4. Rename to: "Parse PR Content"

### Step 6: Add Output Block

1. Drag Output block
2. Connect Parse PR Content → Output
3. Add properties:
   - `pr_title`: `{{Parse PR Content.pr_title}}`
   - `pr_body`: `{{Parse PR Content.pr_body}}`
   - `code_changes`: `{{Parse PR Content.code_changes}}`

### Step 7: Save and Export

1. Save as Module
2. Export to: `postman/modules/generate-pr-module.json`

✅ **MODULE 3 COMPLETE!**

---

## PART 4: CREATE MODULE 4 - Create GitHub PR Module (20 minutes)

### Step 1: Create New Flow

1. New Flow → `create-pr-module`

### Step 2: Add Input Block (5 inputs)

Add these properties:

1. `title` (String, required)
2. `body` (String, required)
3. `branch` (String, required)
4. `repo_owner` (String, required)
5. `repo_name` (String, required)

### Step 3: Add HTTP Request Block (Create PR)

1. Drag HTTP Request
2. Connect Input → HTTP Request
3. Configure:
   - **Method:** POST
   - **URL:** `https://api.github.com/repos/{{repo_owner}}/{{repo_name}}/pulls`
   - **Headers:**
     - `Authorization`: `Bearer {{GITHUB_TOKEN}}`
     - `Accept`: `application/vnd.github+json`
     - `X-GitHub-Api-Version`: `2022-11-28`
     - `Content-Type`: `application/json`
   - **Body:**

```json
{
  "title": "{{title}}",
  "body": "{{body}}",
  "head": "{{branch}}",
  "base": "main"
}
```

4. Rename to: "Create PR"

### Step 4: Add Tests (Optional but Recommended)

1. Click on "Create PR" block
2. Find "Tests" tab or section
3. Add this test script:

```javascript
pm.test("PR created successfully", function() {
  pm.response.to.have.status(201);
  const json = pm.response.json();
  pm.expect(json.html_url).to.be.a('string');
  pm.expect(json.number).to.be.a('number');
});
```

### Step 5: Add Output Block

1. Drag Output block
2. Add properties:
   - `pr_url`: `{{Create PR.body.html_url}}`
   - `pr_number`: `{{Create PR.body.number}}`
   - `success`: `true`

### Step 6: Save and Export

1. Save as Module
2. Export to: `postman/modules/create-pr-module.json`

✅ **MODULE 4 COMPLETE!**

---

## PART 5: CREATE MODULE 5 - Notify Team Module (15 minutes)

### Step 1: Create New Flow

1. New Flow → `notify-team-module`

### Step 2: Add Input Block (3 inputs)

1. `message` (String, required) - Main notification text
2. `pr_url` (String, required) - Link to PR
3. `webhook_url` (String, required) - Slack webhook URL

### Step 3: Add HTTP Request Block (Send Slack)

1. Drag HTTP Request
2. Configure:
   - **Method:** POST
   - **URL:** `{{webhook_url}}`
   - **Headers:**
     - `Content-Type`: `application/json`
   - **Body:**

```json
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "{{message}}"
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
          "url": "{{pr_url}}",
          "style": "primary"
        }
      ]
    }
  ]
}
```

3. Rename to: "Send Slack"

### Step 4: Add Evaluate Block (Get Timestamp)

1. Drag Evaluate block
2. Connect Send Slack → Evaluate
3. Code:

```javascript
return {
  success: true,
  timestamp: new Date().toISOString()
};
```

4. Rename to: "Add Timestamp"

### Step 5: Add Output Block

1. Drag Output block
2. Add properties:
   - `success`: `{{Add Timestamp.success}}`
   - `timestamp`: `{{Add Timestamp.timestamp}}`

### Step 6: Save and Export

1. Save as Module
2. Export to: `postman/modules/notify-team-module.json`

✅ **MODULE 5 COMPLETE!**

---

## PART 6: TEST YOUR MODULES (30 minutes)

For each module, create a simple test flow:

### How to Test a Module

1. Create New Flow (name it `test-[module-name]`)
2. Add **"Flow Module"** block from sidebar
3. Click the Flow Module block
4. Select your module from dropdown
5. Fill in test inputs
6. Add **Output** block to see results
7. Click **"Run"** button (top right)
8. Check results in Output

### Test Cases

**Test Module 1 (Search Code):**
```json
Input: {"query": "ProfileCard"}
Expected: {"files": [...], "total": X, "success": true}
```

**Test Module 2 (Check Conflicts):**
```json
Input: {
  "files": ["src/auth.ts"],
  "repo_owner": "your-github-username",
  "repo_name": "your-repo-name"
}
Expected: {"has_conflict": true/false, "conflict_count": X, "conflicting_prs": [...]}
```

**Test Module 3 (Generate PR):**
```json
Input: {
  "feature_name": "Dark mode toggle",
  "files": ["src/components/Settings.tsx"],
  "acceptance_criteria": ["Add toggle", "Save preference"]
}
Expected: {"pr_title": "...", "pr_body": "...", "code_changes": "..."}
```

**Test Module 4 (Create PR):**
⚠️ **WARNING:** This will actually create a PR on GitHub! Use a test repo.
```json
Input: {
  "title": "test: Test PR",
  "body": "This is a test",
  "branch": "test-branch-123",
  "repo_owner": "your-username",
  "repo_name": "test-repo"
}
Expected: {"pr_url": "https://...", "pr_number": 123, "success": true}
```

**Test Module 5 (Notify Team):**
```json
Input: {
  "message": "✅ Test notification",
  "pr_url": "https://github.com/test/test/pull/1",
  "webhook_url": "{{SLACK_WEBHOOK_URL}}"
}
Expected: {"success": true, "timestamp": "2025-..."}
```

---

## TROUBLESHOOTING

### "Can't find variable {{VARIABLE_NAME}}"
- Check environment is selected (dropdown at top right)
- Go to Environments → Select your environment
- Verify variable exists and has a value

### "HTTP block returns 401 Unauthorized"
- Check API key format in environment
- For GitHub: Should be `Bearer ghp_xxxxx`
- For Claude: Should be `sk-ant-xxxxx`
- Verify API key is still valid

### "Module doesn't appear in dropdown"
- Make sure you clicked "Save as Module" (not just Save)
- Restart Postman Desktop
- Check Flows → Modules section (left sidebar)

### "Tests are failing"
- Run module manually first
- Check Postman Console (View → Show Postman Console)
- Look for error messages in response

---

## CHECKLIST: You're Done When...

- [ ] All 5 modules created in Postman Desktop
- [ ] All 5 modules saved as modules (not just flows)
- [ ] All 5 modules exported to `postman/modules/` directory
- [ ] Each module tested individually
- [ ] docs/FLOW_MODULES.md created (already done!)
- [ ] Test flows created for each module
- [ ] No errors in Postman Console

---

## Next Steps

Once you complete this:
1. Let DEV 1 know modules are ready for integration
2. Share module JSON files location
3. Help test the integrated main flow

**Great work! You've completed DEV 2's tasks! 🎉**
