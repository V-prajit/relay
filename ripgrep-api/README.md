# Ripgrep API

HTTP API wrapper for [ripgrep](https://github.com/BurntSushi/ripgrep) code search, used by the PM Copilot Postman Flow.

## Features

- 🔍 **Fast code search** - Powered by ripgrep (used by VS Code)
- 🌐 **RESTful API** - Simple HTTP interface
- 🎯 **Type filtering** - Search by file type (tsx, js, py, etc.)
- 🔧 **Configurable** - Environment-based configuration
- 📊 **Structured output** - JSON responses with file paths and matches

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for most cases)
```

### 3. Start Server

**Development** (with auto-reload):
```bash
npm run dev
```

**Production**:
```bash
npm start
```

Server will run on `http://localhost:3001`

## API Endpoints

### `POST /api/search`

Search codebase for a pattern.

**Request:**
```json
{
  "query": "ProfileCard",
  "path": "src/",
  "type": "tsx",
  "case_sensitive": false
}
```

**Parameters:**
- `query` (required): Search pattern/keyword
- `path` (optional): Directory to search (default: `./`)
- `type` (optional): File type filter (e.g., `tsx`, `js`, `py`)
- `case_sensitive` (optional): Case-sensitive search (default: `false`)

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
        "column": 13,
        "content": "export const ProfileCard = ({ user }) => {",
        "match_text": "ProfileCard"
      }
    ],
    "total": 2
  },
  "query": {
    "pattern": "ProfileCard",
    "path": "src/",
    "type": "tsx",
    "case_sensitive": false
  }
}
```

### `GET /api/types`

Get list of supported file types.

**Response:**
```json
{
  "success": true,
  "types": ["js", "ts", "tsx", "jsx", "py", "rs", "go", "java", ...]
}
```

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-10-25T12:00:00.000Z"
}
```

## Usage with Postman Flows

### 1. Create HTTP Request Block

In your Postman Flow, add an **HTTP Request** block with:

**Method:** POST
**URL:** `{{RIPGREP_API_URL}}/api/search`
**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "query": "{{ai_agent.search_keywords}}",
  "path": "src/",
  "type": "tsx"
}
```

### 2. Process Response

Connect the HTTP block output to a **Template** block or **AI Agent** block:

```javascript
// Access results
workflow.ripgrep_response.data.files        // Array of file paths
workflow.ripgrep_response.data.matches      // Array of match objects
workflow.ripgrep_response.data.total        // Number of matches
```

## Environment Variables

Create a `.env` file (use `.env.example` as template):

```bash
# Server Configuration
PORT=3001
NODE_ENV=development

# CORS Configuration
ALLOWED_ORIGINS=*

# Search Configuration
MAX_SEARCH_RESULTS=50
DEFAULT_SEARCH_PATH=./

# Logging
LOG_LEVEL=info
```

## Testing

### Using curl

```bash
# Search for "ProfileCard" in TypeScript files
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ProfileCard",
    "path": "src/",
    "type": "tsx"
  }'
```

### Using Postman

1. Create a new request
2. Set method to **POST**
3. URL: `http://localhost:3001/api/search`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):
   ```json
   {
     "query": "ProfileCard",
     "path": "src/",
     "type": "tsx"
   }
   ```

## Common File Types

| Type | Extensions |
|------|-----------|
| `js` | .js, .jsx, .mjs, .cjs |
| `ts` | .ts |
| `tsx` | .tsx |
| `py` | .py |
| `rs` | .rs |
| `go` | .go |
| `java` | .java |
| `json` | .json |
| `md` | .md, .markdown |

Get full list: `GET /api/types`

## Error Handling

All errors return:
```json
{
  "success": false,
  "error": "Error message here"
}
```

**Common errors:**
- `400 Bad Request` - Missing or invalid query parameter
- `500 Internal Server Error` - Ripgrep execution failed

## Performance

Ripgrep is extremely fast:
- Searches entire codebases in milliseconds
- Respects `.gitignore` by default
- Optimized for large repositories

**Typical response times:**
- Small repo (< 1000 files): < 50ms
- Medium repo (1000-10000 files): 50-200ms
- Large repo (> 10000 files): 200-500ms

## Troubleshooting

### "Ripgrep not found" error

The `@vscode/ripgrep` package should install the binary automatically. If it fails:

```bash
npm rebuild @vscode/ripgrep
```

### CORS errors from Postman

Set `ALLOWED_ORIGINS=*` in `.env` or add specific origins:

```bash
ALLOWED_ORIGINS=https://flows.postman.com,http://localhost:3000
```

### No matches found

- Check the `path` parameter points to a valid directory
- Verify file types with `GET /api/types`
- Try with `case_sensitive: false`

## License

MIT
