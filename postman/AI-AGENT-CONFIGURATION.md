# AI Agent Configuration for PM Copilot

This document explains how to configure the AI Agent block in Postman Flows to implement smart conflict detection and autonomous PR creation.

## Overview

The AI Agent orchestrates the entire workflow autonomously by calling Flow Modules as tools. This eliminates the need for manual loops, decision blocks, and evaluate blocks.

---

## Step 1: Import Flow Modules

Before configuring the AI Agent, import all 6 flow modules:

1. **In Postman Desktop** → Go to "Collections"
2. Click "Import" → Choose all module JSON files from `postman/modules/`
3. **Important**: For each collection, create a Flow Module:
   - Open the collection → Click "..." → "Create Flow Module"
   - This creates a reusable module with a snapshot

### Modules to Import:
- `ripgrep-search-module.json`
- `get-open-prs-module.json`
- `get-pr-files-module.json`
- `claude-generate-pr-module.json`
- `create-github-pr-module.json`
- `send-slack-notification-module.json`

---

## Step 2: Create Main Flow

1. **Create New Flow**: "PM-Copilot-Main-v2"
2. **Add Start Block**
   - Type: "Request-triggered Action"
   - Expected input schema:
     ```json
     {
       "text": "Add ProfileCard to /users",
       "user_id": "@engineer"
     }
     ```

3. **Add AI Agent Block**
   - Connect to Start block
   - Name: "PM Copilot Agent"

4. **Add Output Block**
   - Connect to AI Agent success output
   - Returns final JSON result

---

## Step 3: Configure AI Agent - Add Tools

In the AI Agent block settings:

1. Click **"Add Tools"**
2. Select all 6 flow modules you created:
   - ☑️ Ripgrep Search Module
   - ☑️ Get Open PRs Module
   - ☑️ Get PR Files Module
   - ☑️ Claude Generate PR Module
   - ☑️ Create GitHub PR Module
   - ☑️ Send Slack Notification Module

3. **Tool Configuration** (auto-populated by AI Agent):
   - The AI Agent will automatically generate input parameters based on the module's schema
   - It can populate these from variables or generate them based on context

---

## Step 4: Configure AI Agent - System Prompt

Paste this enhanced system prompt into the AI Agent configuration:

```
You are a PM Copilot AI that transforms vague feature requests into actionable GitHub PRs with smart conflict detection.

## INPUT
User Request: {{Start.text}}
User ID: {{Start.user_id}}

## YOUR WORKFLOW

### 1. PARSE INTENT
Extract from the user's request:
- feature_name: Short name (e.g., "profile-card", "dark-mode")
- search_keywords: Keywords to search codebase (e.g., "ProfileCard", "Settings theme")
- acceptance_criteria: 3-5 specific, testable bullet points
- target_route: Route/component being modified (if applicable)

### 2. SEARCH CODEBASE
Call the **Ripgrep Search Module** with:
- query: search_keywords
- path: "src/"
- type: "tsx" (or appropriate file type)
- case_sensitive: false

Store the results:
- impacted_files: List of file paths
- is_new_feature: Boolean (true if no files found)
- total_files: Count

### 3. CONFLICT DETECTION
Call the **Get Open PRs Module** to fetch current open PRs (state=open, per_page=10)

For EACH open PR (up to 10):
  a) Call the **Get PR Files Module** with pr_number
  b) Get list of changed files in that PR
  c) Calculate overlap:
     - overlapping_files = intersection(impacted_files, pr_changed_files)
     - conflict_score = (overlapping_files.length / impacted_files.length) * 100
  d) Store conflict info:
     - pr_number
     - pr_title
     - pr_author
     - overlapping_files (array of file paths)
     - conflict_score (0-100)

Sort conflicts by score (highest first)
Set has_conflict = true if any conflict_score > 0

### 4. GENERATE PR CONTENT
Call the **Claude Generate PR Module** with:
- feature_request: {{Start.text}}
- impacted_files: JSON array of files from step 2
- is_new_feature: Boolean from step 2
- conflict_info: Summary of conflicts (if any)
  Example: "Conflicts with PR #42 (3 overlapping files: Settings.tsx, theme.ts)"
- feature_name: From step 1

This generates:
- pr_title
- pr_description (markdown formatted)
- branch_name (auto-generated with timestamp + GUID)

### 5. CREATE PULL REQUEST
Call the **Create GitHub PR Module** with:
- pr_title: From step 4
- pr_description: From step 4
- branch_name: From step 4

Store the response:
- pr_url
- pr_number

### 6. NOTIFY TEAM
Call the **Send Slack Notification Module** with:
- feature_name: From step 1
- pr_number: From step 5
- pr_url: From step 5
- impacted_files: From step 2
- has_conflict: Boolean from step 3
- conflict_score: Highest score from step 3
- conflict_details: Description of conflicts
- reasoning_trace: Array of your decision steps

For reasoning_trace, include:
- "Parsed intent: {feature_name}"
- "Searched codebase: found {total_files} files"
- "Scanned {open_prs_count} open PRs"
- "Detected {conflicts_count} potential conflicts" (if any)
- "Highest conflict risk: {conflict_score}%" (if > 0)
- "Generated PR content with Claude"
- "Created GitHub PR #{pr_number}"
- "Sent notification to Slack"

## OUTPUT FORMAT

Return this JSON structure:
```json
{
  "success": true,
  "feature_name": "profile-card",
  "pr_url": "https://github.com/owner/repo/pull/43",
  "pr_number": 43,
  "impacted_files": ["src/components/ProfileCard.tsx", "src/pages/users.tsx"],
  "total_files": 2,
  "is_new_feature": false,
  "conflict_detected": false,
  "conflict_score": 0,
  "conflicting_prs": [],
  "acceptance_criteria": [
    "ProfileCard displays user avatar and name",
    "Route /users renders ProfileCard list",
    "Component has TypeScript types"
  ],
  "reasoning_trace": [
    "Parsed intent: profile-card",
    "Searched codebase: found 2 files",
    "Scanned 2 open PRs",
    "No conflicts detected",
    "Generated PR content with Claude",
    "Created GitHub PR #43",
    "Sent notification to Slack"
  ]
}
```

## CONFLICT HANDLING LOGIC

If conflict_score > 50%:
  - Add strong warning to Slack notification
  - Include link to conflicting PR
  - Suggest "@mention the PR owner for coordination"

If conflict_score 20-50%:
  - Add moderate warning
  - List overlapping files

If conflict_score < 20%:
  - No warning needed (minor overlap)

## ERROR HANDLING

If any tool call fails:
1. Log the error in reasoning_trace
2. Try to continue with remaining steps if possible
3. If critical failure (e.g., Ripgrep fails), return error JSON:
   ```json
   {
     "success": false,
     "error": "Description of what failed",
     "step_failed": "search_codebase",
     "reasoning_trace": [...]
   }
   ```

## IMPORTANT NOTES

- Always call tools in sequence (don't skip steps)
- Store intermediate results as you go
- Be thorough in conflict detection (check all open PRs)
- Provide detailed reasoning_trace for transparency
- Generate unique branch names to avoid collisions
- Consider context when calculating conflict scores (core files = higher risk)

## EXAMPLES

### Example 1: New Feature (No Conflicts)
Input: "Add OAuth login support"
- Ripgrep finds 0 files → is_new_feature: true
- No open PRs touching auth files
- Claude generates new file structure
- No conflicts
- Creates PR, sends success notification

### Example 2: Existing Feature with Conflict
Input: "Update dark mode toggle in settings"
- Ripgrep finds: Settings.tsx, theme.ts
- Open PR #42 also modifies Settings.tsx
- Conflict score: 50% (1 of 2 files overlap)
- Creates PR with conflict warning
- Slack notification includes warning + link to PR #42

---

```

---

## Step 5: Test the AI Agent

### Test Input 1: New Feature
```json
{
  "text": "Add OAuth authentication support",
  "user_id": "@alice"
}
```

Expected behavior:
- Searches for "OAuth" keywords
- Finds no existing files
- Detects as new feature
- Generates file structure
- Creates PR
- No conflicts (assuming no open auth PRs)

### Test Input 2: Existing Feature with Potential Conflict
```json
{
  "text": "Update Settings page dark mode toggle",
  "user_id": "@bob"
}
```

Expected behavior:
- Searches for "Settings dark mode"
- Finds Settings.tsx, theme.ts
- Checks open PRs
- If PR #42 touches Settings.tsx → conflict detected
- Creates PR with warning
- Slack shows conflict alert

---

## Step 6: Deploy as Action

Once tested:

1. Click **"Deploy"** in Postman Flow
2. Enable **"Public URL"**
3. Copy the Action URL (e.g., `https://flows-action.postman.com/abc123`)
4. Configure Slack slash command:
   - Command: `/impact`
   - Request URL: Your Postman Action URL
   - Description: "Generate PR from PM spec"

---

## Step 7: Monitor & Debug

### View Agent Decisions
- Go to **Flow Execution History**
- Click on a run → See "AI Agent Reasoning"
- Shows which tools were called and why

### Common Issues

**Issue**: "Tool not found"
- **Fix**: Ensure flow modules have snapshots created

**Issue**: "Variable not found: {{Start.text}}"
- **Fix**: Check Start block is properly connected and has correct input schema

**Issue**: "Conflict detection not working"
- **Fix**: Verify GitHub token has `repo` scope and can read PRs

---

## Advanced Configuration

### Custom Conflict Logic

If you want more sophisticated conflict detection, modify the prompt to consider:

1. **File Importance Weighting**
   - Core files (e.g., `index.tsx`, `App.tsx`) = 2x weight
   - Config files (e.g., `.env`, `package.json`) = 3x weight
   - Test files = 0.5x weight

2. **Time-Based Decay**
   - PRs older than 7 days = reduce conflict score by 20%
   - PRs with recent activity (< 24 hours) = increase by 10%

3. **Author Consideration**
   - Same author as requester = reduce score by 30%
   - Different team = increase by 20%

Add this logic to the AI Agent prompt in the "CONFLICT DETECTION" section.

---

## Troubleshooting

### Agent Not Calling Tools

**Symptom**: AI Agent generates text response but doesn't call modules

**Causes**:
1. Tools not registered properly
2. Module doesn't have snapshot
3. Prompt doesn't explicitly instruct to "Call the [Tool Name] Module"

**Fix**:
- Re-check tool configuration
- Recreate module snapshots
- Use explicit "Call the **Module Name**" in prompt

### Conflicts Not Detected

**Symptom**: Always shows "No conflicts"

**Debug**:
1. Check if Get Open PRs returns data (test manually)
2. Verify GitHub token permissions
3. Add console logging to see what data AI receives

### Slow Performance

**Symptom**: Flow takes >30 seconds

**Optimizations**:
1. Reduce per_page for Get Open PRs (default 10 is good)
2. Skip Get PR Files for PRs with 0 changed_files
3. Use caching for repeated searches

---

## Next Steps

Once your AI Agent is working:

1. ✅ Add pre-request scripts for dynamic branch names (already in modules)
2. ✅ Enhance Slack notifications with Block Kit formatting (already configured)
3. ⏭️ Build Dashboard to visualize conflicts (see `dashboard-api/` docs)
4. ⏭️ Add Calendar + Slack availability routing (requires additional APIs)
5. ⏭️ Register on Agentverse for ASI:One bonus points

---

## Summary

This AI Agent-driven architecture is:

✅ **Simpler** - No manual loops or decision blocks
✅ **Smarter** - AI makes contextual decisions
✅ **More Maintainable** - Just update the prompt, not complex logic
✅ **Transparent** - Reasoning trace shows every decision
✅ **Hackathon-Ready** - Demonstrates advanced Postman AI features

**Total Flow Complexity**: 3 blocks (Start → AI Agent → Output) + 6 reusable modules
**Lines of Manual Code**: ~0 (all logic in AI prompt)
**Judge-Clickable Demo**: Full reasoning trace visible in Postman Analytics

---

**Questions?** See the full documentation in `/docs/` or check Postman's AI Agent docs:
https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/
