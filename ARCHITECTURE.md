# Relay Architecture

Technical documentation of Relay's system design, data flow, and implementation patterns.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Postman Flow Structure](#postman-flow-structure)
4. [Data Flow](#data-flow)
5. [Slack Integration](#slack-integration)
6. [Ripgrep API](#ripgrep-api)
7. [GitHub Integration](#github-integration)
8. [Error Handling](#error-handling)
9. [Performance Considerations](#performance-considerations)

---

## System Overview

Relay is built on a serverless, event-driven architecture that processes Slack slash commands through a Postman Flow orchestration layer. The system is designed to handle Slack's 3-second webhook timeout requirement while performing potentially long-running operations in the background.

### Key Design Principles

- **Asynchronous by default**: Immediate acknowledgment with background processing
- **Stateless execution**: Each request is independent and self-contained
- **Idempotent operations**: Safe to retry failed requests
- **Fail-fast validation**: Catch errors early before expensive operations
- **Modular composition**: Reusable Flow Modules for common operations

### Architecture Diagram

```
┌─────────────┐
│   Slack     │
│  /relay cmd │
└──────┬──────┘
       │ HTTP POST (form-encoded)
       │
┌──────▼─────────────────────────────────────┐
│    Postman Action (Deployed Flow)          │
│                                             │
│  ┌───────┐   ┌──────────┐   ┌──────────┐  │
│  │Request│──▶│ Evaluate │──▶│ Validate │  │
│  └───────┘   └──────────┘   └────┬─────┘  │
│                                   │         │
│                              ┌────▼────┐    │
│                              │  Fork   │    │
│                              └────┬────┘    │
│                    ┌──────────────┴──────────────┐
│                    │                             │
│             ┌──────▼─────┐            ┌─────────▼────────┐
│             │  Response  │            │     Module        │
│             │  (202 OK)  │            │  (Background)     │
│             └────────────┘            └──────┬───────────┘
│                                              │
└──────────────────────────────────────────────┼────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────┐
                    │                          │                  │
             ┌──────▼────────┐     ┌──────────▼─────┐   ┌────────▼─────────┐
             │  Ripgrep API  │     │  GitHub API     │   │  Slack Webhook   │
             │  (Code Search)│     │  (Create Issue) │   │  (Notification)  │
             └───────────────┘     └─────────────────┘   └──────────────────┘
```

---

## Component Architecture

### 1. Postman Flows (Orchestration Layer)

Postman Flows serves as the orchestration engine, coordinating between multiple services without requiring a traditional backend server.

**Key Components**:
- **Request Block**: Entry point for webhooks
- **Evaluate Block**: Data transformation using TypeScript
- **Validate Block**: JSON Schema validation
- **Fork Pattern**: Parallel execution paths
- **HTTP Request Blocks**: External API calls
- **Flow Modules**: Reusable sub-workflows

**Why Postman Flows**:
- Serverless execution (no infrastructure management)
- Built-in observability (run logs, analytics)
- Native async support (60-minute execution limit)
- Visual debugging and testing
- Version control with snapshots

### 2. Ripgrep API (Code Search Service)

Node.js/Express wrapper around ripgrep CLI for fast code search.

**Technology Stack**:
- Node.js 18+
- Express.js (REST API)
- Ripgrep CLI (native binary)
- CORS enabled for Postman access

**API Endpoints**:
- `GET /api/health` - Health check
- `POST /api/search` - Execute search query

**Search Features**:
- Pattern matching with regex support
- File type filtering
- Case-sensitive/insensitive search
- Glob pattern support
- New feature detection (returns `is_new_feature: true` when no files found)

### 3. GitHub REST API (Issue Management)

Direct integration with GitHub's REST API for issue creation.

**Operations**:
- Create issues with structured content
- Add labels and assignees
- Link related issues
- Search existing issues

**Authentication**: Personal Access Token with `repo` scope stored in Postman Action Configuration as a Secret.

### 4. Slack (User Interface)

**Slash Command**:
- Command: `/relay`
- Format: `/relay <feature description>`
- Payload type: `application/x-www-form-urlencoded`
- Timeout: 3 seconds (hard limit)

**Incoming Webhook**:
- Notification channel: Configurable
- Format: Block Kit structured messages
- Content: Issue link, reasoning trace, impacted files

---

## Postman Flow Structure

### Main Action Flow

The deployed Action follows this block sequence:

```
Request
  │
  ├─ Body →  Evaluate (flatten arrays)
  │            │
  │            ├─ Result → Validate (check required fields)
  │                         │
  │                         ├─ Pass → Fork
  │                         │         ├─ Path 1 → Response (202 Accepted)
  │                         │         │
  │                         │         └─ Path 2 → Module (background work)
  │                         │
  │                         └─ Fail → (error path, not implemented)
  │
  ├─ Headers → (unused in current implementation)
  └─ Params → (unused in current implementation)
```

### Critical Implementation Details

#### 1. Evaluate Block (Array Flattening)

**Problem**: Slack sends form-encoded data with all values as single-element arrays:

```json
{
  "text": ["add dark mode"],
  "user_id": ["U123"],
  "command": ["/relay"]
}
```

**Solution**: TypeScript transformation in Evaluate block:

```typescript
const flatten = (obj: Record<string, any>) =>
  Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [k, Array.isArray(v) ? v[0] : v])
  );

flatten(data);
```

**Output**:

```json
{
  "text": "add dark mode",
  "user_id": "U123",
  "command": "/relay"
}
```

#### 2. Validate Block (Schema Enforcement)

**Schema**:

```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": ["text"]
}
```

**Purpose**:
- Ensure `text` field is present and non-empty
- Fail fast before expensive API calls
- Provide clear error messages for debugging

#### 3. Fork Pattern (Async Execution)

**Design Rationale**: Slack's 3-second timeout requires immediate response while background work can take 15-60 seconds.

**Implementation**:
- **Pass Port**: Connects to both Response and Module blocks
- **Response Block**: Returns 202 Accepted with JSON body:
  ```json
  {
    "success": true,
    "message": "Workflow triggered"
  }
  ```
- **Module Block**: Executes long-running workflow in background

**Execution Limits**:
- Synchronous path: 30 seconds
- Background path (via Fork): 60 minutes

### Flow Module Structure

The background workflow is encapsulated in a reusable Flow Module: "Search using RIPGREP API and process AI responses"

**Module Inputs**:
- `text` (string): Feature request description
- `github_token` (string): GitHub PAT from Action Configuration

**Module Flow**:

```
Start
  │
  ├─ text → HTTP Request (Ripgrep API)
  │           │
  │           ├─ body.data.files → HTTP Request (GitHub - Get Open PRs)
  │           │                      │
  │           └─ body.data.is_new_feature → HTTP Request (Generate Content)
  │                                           │
  │                                           ├─ pr_title → HTTP Request (GitHub - Create Issue)
  │                                           │                │
  │                                           └─ pr_description → HTTP Request (Slack Webhook)
  │
  └─ github_token → HTTP Request.variables.github_token (for all GitHub calls)
```

**Key Pattern**: Module inputs are data ports. To use them as variables in HTTP Request blocks, they must be wired to the **Variables** input section of each HTTP Request block.

---

## Data Flow

### 1. Slack → Postman Flow

**Request Format** (`application/x-www-form-urlencoded`):

```
text=fix+mobile+login&user_id=U123&command=/relay&...
```

**Parsed by Postman** (arrays):

```json
{
  "text": ["fix mobile login"],
  "user_id": ["U123"],
  "command": ["/relay"],
  "token": ["xoxb-..."],
  "trigger_id": ["123.456.789"],
  "response_url": ["https://hooks.slack.com/..."]
}
```

**After Evaluate** (flattened):

```json
{
  "text": "fix mobile login",
  "user_id": "U123",
  "command": "/relay"
}
```

### 2. Postman Flow → Ripgrep API

**Request**:

```http
POST https://pm-copilot-ripgrep-api.ondigitalocean.app/api/search
Content-Type: application/json

{
  "query": "fix mobile login"
}
```

**Response** (files found):

```json
{
  "success": true,
  "data": {
    "files": [
      "/tmp/ripgrep-repo-cache/./frontend/app/login.tsx",
      "/tmp/ripgrep-repo-cache/./frontend/components/MobileNav.tsx"
    ],
    "total": 2,
    "is_new_feature": false,
    "message": "Found existing files that may be related to this feature."
  }
}
```

**Response** (no files found):

```json
{
  "success": true,
  "data": {
    "files": [],
    "total": 0,
    "is_new_feature": true,
    "message": "No existing files found - may be a new feature requiring new implementation."
  }
}
```

### 3. Postman Flow → GitHub API (Create Issue)

**Request**:

```http
POST https://api.github.com/repos/V-prajit/postman-api-toolkit/issues
Authorization: Bearer ghp_***
Content-Type: application/json

{
  "title": "fix: Resolve unresponsive mobile login",
  "body": "## Summary\n\nThis issue addresses...\n\n## Impacted Files\n\n- `frontend/app/login.tsx`\n- `frontend/components/MobileNav.tsx`\n\n## Acceptance Criteria\n\n- [ ] Login button responds on mobile\n- [ ] Mobile navigation is accessible\n- [ ] Changes are tested on iOS and Android"
}
```

**Response**:

```json
{
  "id": 123456789,
  "number": 42,
  "title": "fix: Resolve unresponsive mobile login",
  "html_url": "https://github.com/V-prajit/postman-api-toolkit/issues/42",
  "state": "open",
  "created_at": "2025-10-29T17:30:00Z"
}
```

### 4. Postman Flow → Slack Webhook (Notification)

**Request**:

```http
POST https://hooks.slack.com/services/T***/***/***
Content-Type: application/json

{
  "text": "GitHub issue created: #42",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*GitHub Issue Created:* <https://github.com/V-prajit/postman-api-toolkit/issues/42|#42 - fix: Resolve unresponsive mobile login>"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Impacted Files:*\n• frontend/app/login.tsx\n• frontend/components/MobileNav.tsx"
      }
    }
  ]
}
```

---

## Slack Integration

### Setup Requirements

1. **Create Slack App**:
   - Visit https://api.slack.com/apps
   - Create new app from scratch
   - Select workspace

2. **Configure Slash Command**:
   - Navigate to "Slash Commands"
   - Create command: `/relay`
   - Request URL: Postman Action URL
   - Short description: "Create GitHub issue from feature request"
   - Usage hint: `<feature description>`

3. **Configure Incoming Webhook**:
   - Navigate to "Incoming Webhooks"
   - Activate webhooks
   - Add webhook to desired channel
   - Copy webhook URL to Postman environment

4. **Important Settings**:
   - **Socket Mode**: Must be DISABLED (blocks Request URL field)
   - **Event Subscriptions**: Not required for this implementation
   - **Interactivity**: Optional (for button clicks in future)

### Form-Encoded Data Handling

**Slack's Payload Format**: All values are sent as arrays, even single values. This is standard behavior for `application/x-www-form-urlencoded` when processing forms.

**Common Fields**:
- `token`: Verification token
- `team_id`: Workspace identifier
- `team_domain`: Workspace URL slug
- `channel_id`: Where command was invoked
- `channel_name`: Channel display name
- `user_id`: User who invoked command
- `user_name`: Username
- `command`: The slash command used (`/relay`)
- `text`: Everything after the command
- `response_url`: URL for delayed responses
- `trigger_id`: For opening modals

### Timeout Handling

Slack requires responses within 3 seconds. Relay handles this with the Fork pattern:

1. **Immediate Response** (Path 1): Returns 202 Accepted within milliseconds
2. **Background Work** (Path 2): Can take up to 60 minutes
3. **Follow-up Notification**: Sent via webhook after background work completes

---

## Ripgrep API

### Architecture

**Technology**: Node.js/Express wrapper around ripgrep CLI binary.

**Deployment**: DigitalOcean App Platform with automatic scaling.

### API Specification

#### POST /api/search

**Request Body**:

```json
{
  "query": "ProfileCard",
  "path": "src/",
  "type": "tsx",
  "case_sensitive": false,
  "max_results": 50
}
```

**Response** (success):

```json
{
  "success": true,
  "data": {
    "files": ["./src/components/ProfileCard.tsx"],
    "total": 1,
    "is_new_feature": false,
    "message": "Found existing files that may be related to this feature.",
    "query": "ProfileCard",
    "execution_time_ms": 45
  }
}
```

**Response** (no results):

```json
{
  "success": true,
  "data": {
    "files": [],
    "total": 0,
    "is_new_feature": true,
    "message": "No existing files found - may be a new feature requiring new implementation.",
    "query": "OAuth",
    "execution_time_ms": 32
  }
}
```

**Error Response**:

```json
{
  "success": false,
  "error": "Invalid query parameter",
  "message": "Query must be a non-empty string"
}
```

### Implementation Details

**Search Process**:

1. Receive request with query parameters
2. Clone/update target repository to `/tmp/ripgrep-repo-cache`
3. Execute ripgrep with appropriate flags:
   ```bash
   rg --files-with-matches --max-count 50 --type tsx "ProfileCard" src/
   ```
4. Parse output and detect if results are empty
5. Set `is_new_feature` flag based on result count
6. Return structured JSON response

**Performance Characteristics**:
- Average response time: 30-50ms for cached repos
- Cold start (first search): 500-1000ms
- Scales horizontally on DigitalOcean

**Environment Variables**:
```bash
PORT=3001
CLONE_DIR=/tmp/ripgrep-repo-cache
REPO_OWNER=V-prajit
REPO_NAME=postman-api-toolkit
ALLOWED_ORIGINS=*
MAX_SEARCH_RESULTS=50
```

---

## GitHub Integration

### Authentication

**Method**: Personal Access Token (classic)

**Required Scopes**:
- `repo`: Full control of private repositories
- `read:org` (optional): For organization repositories

**Storage**: Postman Action Configuration with Secret type. Retrieved via Get Configuration block in Action flow.

### API Operations

#### Create Issue

**Endpoint**: `POST /repos/{owner}/{repo}/issues`

**Request**:

```json
{
  "title": "feat: Add dark mode toggle",
  "body": "Issue description with markdown",
  "labels": ["feature", "frontend"],
  "assignees": ["username"]
}
```

**Common Errors**:
- **401 Unauthorized**: Invalid or expired token
- **403 Forbidden**: Token lacks required scopes
- **404 Not Found**: Repository doesn't exist or no access
- **422 Unprocessable Entity**: Invalid JSON or missing required fields

#### Get Open Pull Requests

**Endpoint**: `GET /repos/{owner}/{repo}/pulls?state=open`

**Purpose**: Check for conflicts with existing work.

**Response**:

```json
[
  {
    "number": 42,
    "title": "Update login component",
    "head": {"ref": "feature/login-update"},
    "files_url": "https://api.github.com/repos/.../pulls/42/files"
  }
]
```

### JSON Payload Construction

**Critical Pattern**: When constructing JSON payloads in HTTP Request blocks, variable interpolation must follow these rules:

**Strings** - WITH quotes:
```json
{
  "title": "{{pr_title}}"
}
```

**Arrays/Objects** - WITHOUT quotes:
```json
{
  "labels": {{labels_array}}
}
```

**Common Error**: Unescaped newlines in interpolated strings break JSON parsing. If the `pr_description` contains newlines, they must be escaped or the entire payload must be constructed in an Evaluate block using `JSON.stringify()`.

---

## Error Handling

### Validation Errors

**Validate Block Failures**:
- Returns structured error with `instancePath` and `message`
- Flow execution stops at Validate block
- No 202 response sent to Slack
- User sees "Command failed" in Slack

**Example Error**:

```json
{
  "data": {"text": ["hello"]},
  "errors": [{
    "instancePath": "/text",
    "schemaPath": "#/properties/text/type",
    "keyword": "type",
    "message": "must be string"
  }]
}
```

### HTTP Request Failures

**4xx Errors** (Client errors):
- 401: Check authentication tokens
- 403: Verify scopes and permissions
- 422: Review JSON payload structure
- 429: Rate limit exceeded

**5xx Errors** (Server errors):
- 500: Service temporarily unavailable
- 503: Service overloaded

**Handling Strategy**:
- Log error details in Postman Flow console
- Continue execution to notify user of failure
- Send Slack message with error information

### Retry Logic

**Current Implementation**: No automatic retries. Failed requests require manual re-invocation.

**Future Enhancement**: Add retry blocks with exponential backoff for transient failures.

---

## Performance Considerations

### Bottlenecks

1. **Ripgrep API**: Cold start latency on DigitalOcean (500-1000ms first request)
2. **GitHub API**: Rate limits (5000 requests/hour for authenticated requests)
3. **Postman Flow**: 60-minute maximum execution time for background work

### Optimization Strategies

**Ripgrep API**:
- Keep repository clones cached in `/tmp`
- Use incremental `git fetch` instead of full clones
- Implement CDN caching for frequently accessed repos

**Postman Flow**:
- Minimize sequential HTTP requests (parallelize where possible)
- Use Select blocks to extract only needed data (reduce payload size)
- Avoid unnecessary Evaluate blocks

**GitHub API**:
- Batch operations when possible
- Cache frequently accessed data (PR lists, repo metadata)
- Monitor rate limit headers and implement backoff

### Scalability

**Current Limits**:
- Ripgrep API: Single DigitalOcean droplet (vertical scaling only)
- Postman Actions: Serverless, scales automatically
- GitHub API: 5000 requests/hour (soft limit)

**Scaling Strategies**:
- Add load balancer for Ripgrep API
- Implement request queuing for high-volume scenarios
- Use GitHub Apps (higher rate limits than PATs)

---

## Security Considerations

### Secrets Management

**GitHub Token**:
- Stored in Postman Action Configuration as Secret type
- Never logged or exposed in responses
- Scoped to minimum required permissions

**Slack Token**:
- Webhook URLs are public but signed
- Verification tokens should be checked (not yet implemented)

### Data Privacy

**Sensitive Data**:
- User IDs and email addresses from Slack
- Repository contents via Ripgrep
- GitHub issue content

**Mitigation**:
- No data persisted beyond execution
- Logs exclude sensitive fields
- Use environment variables for all credentials

### Attack Vectors

**Command Injection**: Ripgrep API uses parameterized queries, not shell concatenation.

**SSRF**: Ripgrep API restricts search to configured repository only.

**Rate Limiting**: No built-in rate limiting on Action (Postman's infrastructure handles this).

---

## Deployment Architecture

### Production Components

1. **Postman Action**:
   - Hosted on Postman cloud infrastructure
   - Auto-scaling, globally distributed
   - HTTPS by default

2. **Ripgrep API**:
   - DigitalOcean App Platform
   - Auto-scaling (1-3 instances)
   - HTTPS with automatic cert renewal

3. **Slack App**:
   - Managed by Slack
   - Webhooks delivered globally

4. **GitHub**:
   - SaaS, no infrastructure required

### Monitoring

**Postman Analytics**:
- Action run history
- Success/failure rates
- Execution duration
- Block-level timing

**DigitalOcean Metrics**:
- CPU/memory usage
- Request count
- Response time

**Slack**:
- Command usage statistics (via Slack analytics)

---

## Future Architecture Enhancements

See [ROADMAP.md](./ROADMAP.md) for detailed plans.

**Planned Improvements**:
- Replace Ripgrep with Elasticsearch for semantic code search
- Add DeepSeek OCR for expanded context window
- Implement conflict detection with co-change analysis
- Build analytics dashboard for reasoning traces
- Add CI/CD integration for automated PR creation

---

## References

- [Postman Flows Documentation](https://learning.postman.com/docs/postman-flows/)
- [Slack API Documentation](https://api.slack.com/)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [Ripgrep Documentation](https://github.com/BurntSushi/ripgrep)
