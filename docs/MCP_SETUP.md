# MCP Server Setup for PM Copilot

## What is MCP?

Model Context Protocol (MCP) lets AI assistants like Claude Desktop discover and call your service as a tool. This enables Claude to directly interact with PM Copilot to transform PM specifications into GitHub PRs.

## Quick Start

### Prerequisites
- Claude Desktop installed
- Your PM Copilot Action URL from Postman Flows
- Optional: API keys for enhanced features

### 1. Get Your Action URL

1. Open Postman Desktop
2. Navigate to your PM Copilot Flow
3. Click **Deploy** → **Action**
4. Copy the generated URL (format: `https://flows-action.postman.com/xxxxx`)

### 2. Configure Claude Desktop

1. **Open Claude Desktop Settings**
   - Click Settings → MCP Servers
   - Click "Add MCP Server"

2. **Add PM Copilot Configuration**
   ```json
   {
     "name": "PM Copilot",
     "url": "YOUR_ACTION_URL_HERE",
     "description": "Transform PM specs into GitHub PRs"
   }
   ```

3. **Restart Claude Desktop** to load the new MCP server

### 3. Test the Integration

In Claude Desktop, try these commands:

```
"Use PM Copilot to create a PR for adding OAuth authentication"

"Check if there are conflicts for updating the login page"

"Find an available frontend engineer for a new feature"
```

## Available Tools

PM Copilot exposes three main tools through MCP:

### 1. create_pr_from_spec
Transform natural language specifications into GitHub PRs.

**Example:**
```json
{
  "text": "Add dark mode toggle to settings",
  "user_id": "@alice"
}
```

### 2. check_pr_conflicts
Check for conflicts with existing pull requests.

**Example:**
```json
{
  "feature_name": "dark mode",
  "target_files": ["Settings.tsx", "theme.css"]
}
```

### 3. get_team_availability
Find available engineers based on skill requirements.

**Example:**
```json
{
  "skill_required": "frontend"
}
```

## Manual Testing with curl

Test your PM Copilot endpoint directly:

```bash
# Basic feature request
curl -X POST https://your-action-url.com \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add dark mode toggle to settings",
    "user_id": "@alice"
  }'

# Check conflicts
curl -X POST https://your-action-url.com/conflicts \
  -H "Content-Type: application/json" \
  -d '{
    "feature_name": "dark mode",
    "target_files": ["Settings.tsx"]
  }'

# Get team availability
curl -X POST https://your-action-url.com/availability \
  -H "Content-Type: application/json" \
  -d '{
    "skill_required": "frontend"
  }'
```

## Expected Responses

### Successful PR Creation
```json
{
  "success": true,
  "pr_url": "https://github.com/owner/repo/pull/123",
  "pr_number": 123,
  "impacted_files": ["Settings.tsx", "theme.css"],
  "conflicts_detected": 0,
  "assigned_engineer": "@bob",
  "acceptance_criteria": [
    "Toggle switch in settings",
    "Theme persists across sessions",
    "All components respect theme"
  ]
}
```

### Conflict Detection Response
```json
{
  "success": true,
  "conflicts_found": true,
  "conflicting_prs": [
    {
      "pr_number": 99,
      "title": "Refactor settings page",
      "files": ["Settings.tsx"]
    }
  ],
  "recommendation": "Wait for PR #99 to merge first"
}
```

## Health Check Monitoring

PM Copilot includes a health endpoint for monitoring:

```bash
curl -X GET https://your-action-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 86400,
  "last_request": "2025-01-15T12:00:00Z"
}
```

## Troubleshooting

### "Connection refused" Error
- **Check Action URL**: Ensure the URL is correct and includes protocol (https://)
- **Verify Deployment**: Check Postman Flow is deployed as Action
- **Test Manually**: Use curl to test the endpoint directly

### "Timeout" Error
- **Increase Timeout**: MCP server config includes 30-second timeout
- **Check Flow Performance**: Review Postman Flow Analytics for bottlenecks
- **Optimize API Calls**: Ensure parallel API calls where possible

### "MCP not found" in Claude
- **Restart Required**: Always restart Claude Desktop after adding MCP servers
- **Check Config Format**: Ensure JSON is valid (use jsonlint.com)
- **Verify URL Format**: Must be full URL with https://

### "Authentication failed"
- **API Keys**: Check all required API keys are set in Postman environment
- **Token Format**: GitHub needs "Bearer" prefix, Claude needs "x-api-key" header
- **Webhook URLs**: Slack webhooks don't need auth but must be valid

## Advanced Configuration

### Custom Authentication

If your PM Copilot requires authentication:

```json
{
  "name": "PM Copilot",
  "url": "YOUR_ACTION_URL",
  "headers": {
    "X-API-Key": "your-api-key-here"
  }
}
```

### Rate Limiting

PM Copilot includes built-in rate limiting:
- 60 requests per minute
- Burst allowance: 10 requests
- Configurable in `mcp-server-config.json`

### Timeout Settings

Default timeout: 30 seconds
Configurable per-tool basis in the MCP config

## Integration with Other Tools

### Slack Integration
PM Copilot sends notifications to Slack channels. Configure webhooks in Postman environment:
- `SLACK_WEBHOOK_PM`: PM notification channel
- `SLACK_WEBHOOK_ENG`: Engineering notification channel

### GitHub Integration
Requires GitHub Personal Access Token with `repo` scope:
- Set `GITHUB_TOKEN` in Postman environment
- Configure `REPO_OWNER` and `REPO_NAME`

### Calendar Integration
Optional Google Calendar integration for engineer availability:
- Set `GOOGLE_CALENDAR_API_KEY` in environment
- Configure calendar IDs for team members

## Best Practices

1. **Test Locally First**: Always test with curl before MCP integration
2. **Monitor Health**: Set up health check monitoring (see CI/CD setup)
3. **Log Requests**: Enable Postman Flow Analytics for debugging
4. **Version Control**: Track MCP config changes in git
5. **Documentation**: Keep this doc updated with any custom configurations

## Support

- **GitHub Issues**: [github.com/yourusername/pm-copilot/issues](https://github.com/yourusername/pm-copilot/issues)
- **Slack Channel**: #pm-copilot-support
- **Email**: support@pmcopilot.tech

---

Last Updated: January 2025
Version: 1.0.0