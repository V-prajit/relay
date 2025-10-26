# CI/CD Setup for PM Copilot

## Overview

PM Copilot uses GitHub Actions for continuous integration and delivery, with automated health monitoring every 30 minutes. Newman (Postman's CLI) runs our test collections, and results are reported to Slack and GitHub.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions Workflow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Triggers:                                                       │
│  • Push to main/develop                                          │
│  • Pull requests                                                 │
│  • Every 30 minutes (cron)                                       │
│  • Manual trigger                                                │
│                                                                   │
│  Jobs:                                                            │
│  1. Health Check → Newman → Reports → Slack/GitHub               │
│  2. Performance Test → Measure response times                    │
│  3. Deploy Monitor → Update Postman Monitor config               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## GitHub Actions Workflow

### Location
`.github/workflows/pm-copilot-monitor.yml`

### What It Does

1. **Health Checks (Every 30 minutes)**
   - Runs PM-Copilot-Health-Check collection
   - Tests endpoint availability
   - Validates response times (< 3 seconds)
   - Checks all API dependencies

2. **Performance Testing (On push)**
   - Runs collection 5 times
   - Measures average response times
   - Generates performance trends

3. **Automated Reporting**
   - HTML reports with test results
   - Slack notifications on failures
   - GitHub issues for scheduled failures
   - PR comments with test summaries

### Workflow Triggers

| Trigger | When | What Happens |
|---------|------|--------------|
| Push | Code pushed to main/develop | Full test suite + performance tests |
| Pull Request | PR opened/updated | Health checks + PR comment |
| Schedule | Every 30 minutes | Health checks + alerts on failure |
| Manual | Workflow dispatch | Full test suite on demand |

## Setting Up CI/CD

### 1. Configure GitHub Secrets

Navigate to: **Repository → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `ACTION_URL` | Your Postman Action URL | `https://flows-action.postman.com/xxxxx` |
| `SLACK_WEBHOOK_URL` | Slack webhook for alerts | `https://hooks.slack.com/services/xxx` |
| `POSTMAN_API_KEY` | (Optional) For monitor deployment | `PMAK-xxxxx` |

### 2. Configure GitHub Variables

Add these variables (can be public):

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `ACTION_URL` | Fallback if secret not set | `https://flows-action.postman.com/xxxxx` |

### 3. Create Slack Webhook

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create new app → From scratch
3. Add **Incoming Webhooks** feature
4. Activate and add new webhook
5. Select channel (#pm-copilot-alerts)
6. Copy webhook URL to GitHub secrets

### 4. Test the Workflow

#### Manual Trigger
1. Go to **Actions** tab in GitHub
2. Select "PM Copilot Health Monitor"
3. Click "Run workflow"
4. Select branch and run

#### Push Trigger
```bash
git push origin main
```

#### View Results
- **Actions tab**: See workflow runs
- **Artifacts**: Download HTML reports
- **Slack**: Check for notifications
- **PR comments**: Automatic test summaries

## Newman CLI

### Local Installation

```bash
# Install Newman globally
npm install -g newman

# Install reporters
npm install -g newman-reporter-htmlextra
npm install -g newman-reporter-json-summary

# Verify installation
newman --version
```

### Running Tests Locally

```bash
# Basic run
newman run postman/collections/pm-copilot-health-check.json \
  --environment postman/environments/dev.json

# With HTML report
newman run postman/collections/pm-copilot-health-check.json \
  --environment postman/environments/dev.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export ./report.html

# With specific variables
newman run postman/collections/pm-copilot-health-check.json \
  --env-var "ACTION_URL=http://localhost:3000" \
  --env-var "SLACK_WEBHOOK_URL=https://hooks.slack.com/xxx"
```

### Newman in CI/CD

The GitHub workflow automatically:
1. Installs Newman and reporters
2. Runs collections with production environment
3. Generates HTML and JSON reports
4. Uploads artifacts for 30 days

## Monitoring Dashboard

### Accessing Reports

1. **Latest Report**: Go to Actions → Latest run → Artifacts
2. **Historical Reports**: Each run keeps reports for 30 days
3. **Performance Trends**: Check workflow summaries

### Report Contents

- **Test Results**: Pass/fail for each test
- **Response Times**: Per-request timings
- **Error Details**: Stack traces and failures
- **Charts**: Visual test summaries

## Slack Notifications

### Success Message
```
✅ PM Copilot health check PASSED
• Tests: 15/15
• Success Rate: 100%
• View Details (link)
```

### Failure Alert
```
🚨 PM Copilot Health Check Failed
Test Results:
• Failed: 3/15
• Success Rate: 80%
• Run: #42

[View Workflow] button
```

### Configuration

Slack webhooks are configured in:
- GitHub Secrets (production)
- Postman environment variables (for collection tests)

## Postman Monitor Integration

### Setting Up Monitor

1. **In Postman Desktop**:
   - Select collection
   - Click **Monitors** → **Create Monitor**
   - Configure:
     - Name: PM Copilot Health
     - Collection: PM-Copilot-Health-Check
     - Environment: Production
     - Schedule: Every 5 minutes

2. **Monitor Settings**:
   - Email notifications: ON
   - Alert on: 2 consecutive failures
   - Regions: Multiple (for global monitoring)

### Monitor vs GitHub Actions

| Feature | Postman Monitor | GitHub Actions |
|---------|----------------|----------------|
| Frequency | Every 5 minutes | Every 30 minutes |
| Location | Postman Cloud | GitHub runners |
| Reports | Postman dashboard | GitHub artifacts |
| Alerts | Email + webhooks | Slack + GitHub issues |
| Cost | Postman plan limits | GitHub Actions minutes |

## Troubleshooting

### Common Issues

#### "Newman command not found"

**Solution:**
```bash
# In workflow, ensure Node.js is set up first
- uses: actions/setup-node@v4
  with:
    node-version: '18'

# Then install Newman
- run: npm install -g newman
```

#### "Environment file not found"

**Solution:**
- Check file path: `postman/environments/production.json`
- Ensure file is committed to repository
- Use `--env-var` for secrets instead of hardcoding

#### "Slack notification not sending"

**Solution:**
1. Verify webhook URL in secrets
2. Test webhook manually:
   ```bash
   curl -X POST $WEBHOOK_URL -d '{"text": "test"}'
   ```
3. Check workflow logs for curl errors

#### "Workflow timeout"

**Solution:**
- Add timeout to workflow:
  ```yaml
  timeout-minutes: 10
  ```
- Check if Action endpoint is responding
- Review Newman timeout settings

#### "Artifacts not uploading"

**Solution:**
- Ensure reports directory exists
- Check artifact path matches actual files
- Verify upload action version (use v4)

### Debug Mode

Enable debug logging:

```yaml
env:
  ACTIONS_RUNNER_DEBUG: true
  ACTIONS_STEP_DEBUG: true
```

Or for specific run:
1. Go to Actions → Re-run jobs
2. Check "Enable debug logging"

## Performance Optimization

### Workflow Speed

- **Cache dependencies**: Node modules cached
- **Parallel jobs**: Health and performance tests can run parallel
- **Conditional steps**: Skip unnecessary steps
- **Artifact retention**: 30 days for reports, 7 for JSON

### Newman Performance

- **Iteration data**: Use CSV for large datasets
- **Timeout settings**: Set reasonable timeouts
- **Parallel collections**: Run multiple collections concurrently
- **Reporter selection**: Use only needed reporters

## Security Best Practices

1. **Never commit secrets**: Use GitHub Secrets
2. **Rotate API keys**: Regular key rotation
3. **Limit webhook scope**: Channel-specific webhooks
4. **Review permissions**: Minimal GitHub token scope
5. **Audit logs**: Monitor workflow runs

## Maintenance

### Weekly Tasks
- Review failure trends
- Check artifact storage usage
- Update Newman version if needed

### Monthly Tasks
- Rotate API keys and webhooks
- Review and optimize test coverage
- Clean up old artifacts
- Update documentation

### Quarterly Tasks
- Performance baseline review
- Dependency updates
- Security audit
- Cost analysis (Actions minutes)

## Integration with Other Tools

### Datadog/New Relic
```yaml
- name: Send metrics to Datadog
  run: |
    curl -X POST "https://api.datadoghq.com/api/v1/series" \
      -H "DD-API-KEY: ${{ secrets.DD_API_KEY }}" \
      -d "{...metrics...}"
```

### PagerDuty
```yaml
- name: Trigger PagerDuty incident
  if: failure()
  run: |
    curl -X POST "https://events.pagerduty.com/v2/enqueue" \
      -H "Authorization: Token token=${{ secrets.PAGERDUTY_TOKEN }}" \
      -d "{...incident details...}"
```

### Jira
```yaml
- name: Create Jira ticket
  uses: atlassian/gajira-create@v3
  with:
    project: PM
    issuetype: Bug
    summary: PM Copilot Health Check Failed
```

## Cost Management

### GitHub Actions Usage

- **Free tier**: 2,000 minutes/month (private repos)
- **Our usage**: ~30 min/day = 900 min/month
- **Optimization**: Use schedule only for production

### Postman Monitor Usage

- **Free tier**: 1,000 monitor runs/month
- **Our usage**: 288 runs/day (every 5 min) = 8,640/month
- **Recommendation**: Use paid plan or reduce frequency

## Support

- **GitHub Issues**: Report CI/CD problems
- **Slack Channel**: #pm-copilot-ci-cd
- **Documentation**: This file + GitHub Actions docs
- **Logs**: Available for 90 days in GitHub

---

Last Updated: January 2025
Version: 1.0.0