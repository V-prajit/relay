# Handling New Features in Postman Flow

## Problem Statement

When a PM requests a completely new feature (e.g., "add oauth"), the RIPGREP API returns no existing files. This used to break the flow because:

1. RIPGREP returned: `files: ["No existing files found - may be a new feature"]` (string message instead of empty array)
2. Claude API expected actual file paths
3. The flow failed at the Claude PR generation step

## Solution

### Backend Fix (Ripgrep API)

The Ripgrep API now returns a structured response:

```json
{
  "success": true,
  "data": {
    "files": [],  // Empty array, not error message
    "matches": [],
    "total": 0,
    "is_new_feature": true,  // NEW: Flag indicating no files found
    "message": "No existing files found - may be a new feature. Claude should create new files and suggest a file structure."
  },
  "query": {
    "pattern": "oauth",
    "path": "./",
    "type": "all",
    "case_sensitive": false
  }
}
```

### Postman Flow Configuration

To handle new features in your Postman Flow, update the **Claude API HTTP block** to use conditional logic:

#### Step 1: Add a Select Block After RIPGREP API

Add a **Select** block to extract the `is_new_feature` flag:

```
Input: RIPGREP API.body.data.is_new_feature
Output Variable: is_new_feature
```

#### Step 2: Update Claude API Prompt Dynamically

In the **Claude API HTTP Request** block, use this dynamic prompt structure:

**For Existing Features** (when `is_new_feature = false`):
```json
{
  "model": "claude-sonnet-4.5-20250929",
  "max_tokens": 4000,
  "messages": [
    {
      "role": "user",
      "content": "You are a senior engineer. Generate a ≤30-line PR patch for: {{AI_Agent.feature_name}}

Impacted files:
{{#each RIPGREP_API.body.data.files}}
- {{this}}
{{/each}}

Use TypeScript and React 19.

Provide:
1. PR title
2. PR description with changes to each file
3. Code patches for each file
4. Acceptance criteria (3-5 bullets)"
    }
  ]
}
```

**For New Features** (when `is_new_feature = true`):
```json
{
  "model": "claude-sonnet-4.5-20250929",
  "max_tokens": 4000,
  "messages": [
    {
      "role": "user",
      "content": "You are a senior engineer. This is a NEW FEATURE with no existing code.

Feature request: {{AI_Agent.feature_name}}

Since no existing files were found, you should:
1. Suggest a file structure (which files to create)
2. Provide implementation for each file (≤30 lines total)
3. Follow TypeScript and React 19 best practices
4. Include necessary imports and types

Provide:
1. PR title
2. List of new files to create
3. Code for each new file
4. Acceptance criteria (3-5 bullets)
5. Integration instructions (how to wire up the new feature)"
    }
  ]
}
```

#### Step 3: Conditional HTTP Request (Alternative Approach)

If you want to use separate requests for new vs. existing features:

1. Add a **Decision Block** after RIPGREP API:
   - Condition: `{{is_new_feature}} == true`
   - If True → Route to "Claude API (New Feature)" HTTP block
   - If False → Route to "Claude API (Existing)" HTTP block

2. Create two separate Claude API blocks with different prompts

### Flow Diagram

```
Start (Slack Webhook)
    ↓
AI Agent (Parse Intent)
    ↓
RIPGREP API
    ↓
Select Block (Extract is_new_feature flag)
    ↓
Decision Block (Check is_new_feature)
    ├─ True  → Claude API (New Feature Prompt)
    └─ False → Claude API (Existing Feature Prompt)
    ↓
GitHub API (Create PR)
    ↓
Slack Webhook (Notify)
```

## Example Scenarios

### Scenario 1: New Feature ("add oauth")

**RIPGREP Response:**
```json
{
  "data": {
    "files": [],
    "is_new_feature": true,
    "message": "No existing files found..."
  }
}
```

**Claude Prompt:**
```
This is a NEW FEATURE with no existing code.
Feature request: Add OAuth authentication
...
```

**Expected Output:**
- PR title: "Add OAuth authentication"
- New files: `src/auth/OAuthProvider.tsx`, `src/hooks/useOAuth.ts`
- Code for each file
- Integration instructions

### Scenario 2: Existing Feature ("update ProfileCard")

**RIPGREP Response:**
```json
{
  "data": {
    "files": ["src/components/ProfileCard.tsx"],
    "is_new_feature": false,
    "message": "Found existing files..."
  }
}
```

**Claude Prompt:**
```
Generate a ≤30-line PR patch for: Update ProfileCard
Impacted files:
- src/components/ProfileCard.tsx
...
```

**Expected Output:**
- PR title: "Update ProfileCard component"
- Changes to existing file
- Acceptance criteria

## Testing

Test both scenarios in Postman:

### Test 1: New Feature
```bash
# Input to Flow
{
  "text": "add oauth",
  "user_id": "@alice"
}

# Expected: PR created with new file structure
```

### Test 2: Existing Feature
```bash
# Input to Flow
{
  "text": "update ProfileCard to show email",
  "user_id": "@alice"
}

# Expected: PR created with patch to existing file
```

## Troubleshooting

**Issue:** Claude API still fails for new features

**Check:**
1. RIPGREP API returns `is_new_feature: true` ✓
2. Decision block routes to correct Claude prompt ✓
3. Claude prompt doesn't reference `{{files}}` (which is empty) ✓

**Issue:** GitHub PR fails for new features

**Reason:** Branch doesn't exist yet

**Solution:** Add a GitHub API block before PR creation:
```
POST /repos/{owner}/{repo}/git/refs
{
  "ref": "refs/heads/feature/{{feature_name}}",
  "sha": "{main_branch_sha}"
}
```

## Best Practices

1. **Always check `is_new_feature` flag** before using `files` array
2. **Provide different prompts** for new vs. existing features
3. **Include file structure suggestions** for new features
4. **Add integration instructions** when creating new files
5. **Test with both scenarios** before deploying

## API Changes Summary

| Field | Old Behavior | New Behavior |
|-------|--------------|--------------|
| `files` | `["No existing files..."]` (error string) | `[]` (empty array) |
| `is_new_feature` | N/A | `true` or `false` |
| `message` | N/A | Human-readable context |

## Migration Guide

If you have existing Postman Flows:

1. **Update Ripgrep API** to latest version (includes `is_new_feature` field)
2. **Add Decision Block** after RIPGREP API call
3. **Create two Claude prompts** (or use conditional logic)
4. **Test thoroughly** with both new and existing feature requests
5. **Update Slack notifications** to indicate whether it's a new or existing feature

## Resources

- [Postman Decision Blocks](https://learning.postman.com/docs/postman-flows/reference/blocks/decision/)
- [Postman Conditional Logic](https://learning.postman.com/docs/postman-flows/build-flows/conditional-logic/)
- [Claude API Messages](https://docs.anthropic.com/en/api/messages)
