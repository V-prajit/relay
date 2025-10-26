# Flow Modules - Export Examples

This directory contains the exported Flow Module JSON files.

## Expected Files

After completing DEV 2 tasks, you should have:

- [ ] `search-code-module.json` (15 minutes)
- [ ] `check-conflicts-module.json` (15 minutes)
- [ ] `generate-pr-module.json` (20 minutes)
- [ ] `create-pr-module.json` (20 minutes)
- [ ] `notify-team-module.json` (15 minutes)

## How to Export

1. Open your Flow in Postman Desktop
2. Click the three dots (⋯) menu in top right
3. Select "Export"
4. Save to this directory

## File Structure

Each exported JSON file should contain:
- Flow configuration
- Block definitions (Input, HTTP, Evaluate, Output)
- Connections between blocks
- Variable references

## Verification

To verify your exports are correct:

1. **File Size:** Each should be 5-50 KB (depending on complexity)
2. **Valid JSON:** Open in text editor, should be properly formatted
3. **Contains Blocks:** Search for "blocks" or "nodes" in the JSON
4. **No Secrets:** Make sure no actual API keys are in the files (should use {{VARIABLE_NAME}})

## Import Test

To test if your exports work:

1. Create a new workspace in Postman
2. Go to Flows → Import
3. Select one of your JSON files
4. Verify the flow imports correctly
5. Check all blocks are present and connected

## Troubleshooting

**"File is empty or corrupt"**
- Re-export the flow
- Make sure you're using Postman Desktop v11.42+

**"Module doesn't import"**
- Check JSON is valid (use jsonlint.com)
- Make sure it was saved as Module, not Flow

**"Variables not working after import"**
- Import the environment JSON separately
- Set environment variables in new workspace

---

## Module Summaries

### 1. search-code-module
**Input:** `query` (string)
**Output:** `files` (array), `total` (number), `success` (boolean)
**Purpose:** Search codebase for files

### 2. check-conflicts-module
**Input:** `files` (array), `repo_owner` (string), `repo_name` (string)
**Output:** `has_conflict` (boolean), `conflict_count` (number), `conflicting_prs` (array)
**Purpose:** Check for PR conflicts

### 3. generate-pr-module
**Input:** `feature_name` (string), `files` (array), `acceptance_criteria` (array)
**Output:** `pr_title` (string), `pr_body` (string), `code_changes` (string)
**Purpose:** Generate PR content with Claude AI

### 4. create-pr-module
**Input:** `title`, `body`, `branch`, `repo_owner`, `repo_name` (all strings)
**Output:** `pr_url` (string), `pr_number` (number), `success` (boolean)
**Purpose:** Create GitHub pull request

### 5. notify-team-module
**Input:** `message`, `pr_url`, `webhook_url` (all strings)
**Output:** `success` (boolean), `timestamp` (string)
**Purpose:** Send Slack notification

---

**Note:** These modules will be integrated into the main PM Copilot flow by DEV 1.
