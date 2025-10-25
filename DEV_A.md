DEV_A_GUIDE.md
markdown# DEV A: Git + Backend Core + OCR Integration

**Your Mission:** Build the FastAPI backend with git archaeology, Claude analysis, and DeepSeek OCR for document scanning

**Time Budget:** 22 hours total
- Hours 0-5: Setup + Git utilities
- Hours 5-10: Claude integration + analysis
- Hours 10-15: DeepSeek OCR integration
- Hours 15-18: GitHub PR creation
- Hours 18-22: Testing + polish

---

## Hour 0-2: Project Setup & Structure

### Step 1: Create Backend Structure

**Run in terminal:**
````bash
mkdir backend && cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Copy requirements.txt (from above) into backend/
pip install -r requirements.txt

# Create structure
mkdir -p app/{routes,services,utils,models}
touch app/__init__.py
touch app/{routes,services,utils,models}/__init__.py
touch app/main.py
touch .env
````

**Expected result:** Virtual env activated, all packages installed

---

### Step 2: Create FastAPI Server

**Prompt for Claude Code:**
````
Create app/main.py with a FastAPI application that:

1. Import necessary modules:
   - FastAPI, CORSMiddleware from fastapi
   - uvicorn
   - load_dotenv from dotenv
   - os

2. Initialize FastAPI app with:
   - title: "BugRewind API"
   - version: "1.0.0"
   - description: "Git archaeology for bug origins"

3. Configure CORS middleware:
   - allow_origins: ["*"]
   - allow_credentials: True
   - allow_methods: ["*"]
   - allow_headers: ["*"]

4. Add health check endpoint:
   @app.get("/health")
   Returns: {"status": "healthy", "version": "1.0.0"}

5. Include routers (we'll create these later):
   - from app.routes import analyze
   - app.include_router(analyze.router, prefix="/api")

6. Add startup event:
   - Load environment variables
   - Create CLONE_DIR if it doesn't exist
   - Log "Server started on port {PORT}"

7. Main execution block:
   if __name__ == "__main__":
       uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)

Use proper Python typing hints everywhere.
````

**Save to:** `app/main.py`

**Test:**
````bash
python app/main.py
# Should see: "Server started on port 8000"
# Visit http://localhost:8000/health
````

---

### Step 3: Create Pydantic Models

**Prompt for Claude Code:**
````
Create app/models/requests.py with Pydantic models:

1. AnalyzeBugRequest:
   - repo_url: str
   - bug_description: str
   - file_path: str
   - line_hint: Optional[int] = None

2. CreatePRRequest:
   - repo_url: str
   - branch_name: str
   - patch_content: str
   - title: str
   - description: str

3. OCRAnalyzeRequest:
   - image_data: str  # base64 encoded
   - bug_description: str

Use Field() for validation:
- repo_url must start with "https://github.com"
- bug_description min length 10 chars
- file_path must not be empty

Add example values in Field(example=...) for API docs.

Also create app/models/responses.py:

1. CommitInfo:
   - commit_hash: str
   - author: str
   - timestamp: int
   - message: str
   - line_number: Optional[int]

2. ClaudeAnalysis:
   - root_cause: str
   - developer_intent: str
   - minimal_patch: str
   - confidence: float

3. AnalyzeBugResponse:
   - first_bad_commit: str
   - commits: List[CommitInfo]
   - file_path: str
   - analysis: ClaudeAnalysis

4. CreatePRResponse:
   - success: bool
   - pr_url: str
   - branch_name: str
````

**Expected result:** Type-safe models for all API endpoints

---

## Hour 2-5: Git Utilities

### Step 4: Git Blame Implementation

**Prompt for Claude Code:**
````
Create app/utils/git_ops.py with git operations using GitPython:

1. Import:
   - git (from GitPython)
   - os, pathlib
   - datetime
   - typing (List, Dict, Optional, Tuple)

2. Function: run_git_blame(repo_path: str, file_path: str) -> List[Dict]:
   
   Purpose: Run git blame on a file and parse line-by-line attribution
   
   Implementation:
   - Use git.Repo(repo_path)
   - Run: repo.git.blame('-w', '--line-porcelain', file_path)
   - Parse the porcelain output:
     - Extract commit hash (40 char hex)
     - Extract author name (line starting with "author ")
     - Extract timestamp (line starting with "author-time ")
     - Extract line content (line after "filename")
   
   - Return list of dicts:
     {
       "line_number": int,
       "commit_hash": str,
       "author": str,
       "timestamp": int (unix),
       "content": str
     }
   
   Error handling:
   - Raise FileNotFoundError if file doesn't exist
   - Raise ValueError if not a git repo
   - Raise Exception with clear message for other git errors
   
   Add detailed docstring and type hints.

3. Add helper function: parse_porcelain_line(lines: List[str]) -> Dict
   To parse the complex porcelain format properly
````

**Save to:** `app/utils/git_ops.py`

**Test:**
````python
# Add at bottom for testing:
if __name__ == "__main__":
    result = run_git_blame("/path/to/test/repo", "test.py")
    print(result[0])  # Should show first line's blame info
````

---

### Step 5: Git Log for Line History

**Prompt for Claude Code:**
````
In app/utils/git_ops.py, add function:

get_line_history(
    repo_path: str, 
    file_path: str, 
    start_line: int, 
    end_line: int
) -> List[Dict]:

Purpose: Get all commits that modified a line range

Implementation:
- Use GitPython: repo.git.log('-L', f'{start_line},{end_line}:{file_path}', '--pretty=format:%H|%an|%at|%s')
- Parse output (pipe-delimited)
- Return list of dicts:
  {
    "commit_hash": str,
    "author": str,
    "timestamp": int,
    "message": str
  }
- Sort by timestamp descending (newest first)

Handle edge cases:
- Empty history (file recently added)
- Line range out of bounds
- File has been renamed

Add comprehensive error handling and logging.
````

---

### Step 6: Safe Repo Cloning

**Prompt for Claude Code:**
````
In app/utils/git_ops.py, add function:

clone_repo(repo_url: str) -> Dict[str, Any]:

Purpose: Safely clone a repo to temp directory with cleanup

Implementation:
- Generate unique ID: use uuid.uuid4().hex[:8]
- Create clone path: os.path.join(os.getenv("CLONE_DIR"), f"repo-{unique_id}")
- Clone with GitPython:
  git.Repo.clone_from(
    repo_url,
    clone_path,
    depth=1,  # shallow clone
    single_branch=True,
    timeout=60
  )

- Return dict:
  {
    "repo_path": str,
    "unique_id": str,
    "cleanup": callable  # function to delete repo
  }

Cleanup function:
- Use shutil.rmtree(clone_path, ignore_errors=True)
- Log deletion

Error handling:
- Timeout after 60 seconds
- Invalid URL
- Network errors
- Disk space errors

Add context manager support:
@contextmanager
def clone_repo_context(repo_url: str):
    repo_info = clone_repo(repo_url)
    try:
        yield repo_info
    finally:
        repo_info["cleanup"]()
````

---

### Step 7: Get Commit Diff

**Prompt for Claude Code:**
````
In app/utils/git_ops.py, add function:

get_commit_diff(
    repo_path: str, 
    commit_hash: str, 
    file_path: Optional[str] = None
) -> str:

Purpose: Get the diff for a specific commit

Implementation:
- Use repo.git.show(commit_hash, file_path or '')
- If file_path provided, only show that file's diff
- Truncate to 5000 characters if longer
- Add "[... truncated for brevity]" if truncated

Return: str (unified diff format)

Error handling:
- Invalid commit hash
- Commit doesn't exist
- File not in commit
````

---

### Step 8: Find Earliest Commit (Heuristic)

**Prompt for Claude Code:**
````
In app/utils/git_ops.py, add function:

find_first_bad_commit(
    repo_path: str,
    file_path: str,
    line_hint: Optional[int] = None
) -> str:

Purpose: Find the earliest commit that touched the suspicious area

Implementation:
1. If line_hint provided:
   - Run git blame on that specific line
   - Get the commit hash for that line
   - Return it

2. If no line_hint:
   - Run git blame on entire file
   - Get all unique commits
   - Return the earliest one (by timestamp)

3. Add confidence scoring:
   - Return tuple: (commit_hash, confidence_score)
   - confidence = 1.0 if line_hint, 0.7 if file-wide search

Return: str (commit hash)

This is a simple heuristic - we can make it smarter later.
````

**Test all functions:**
````python
if __name__ == "__main__":
    with clone_repo_context("https://github.com/torvalds/linux") as repo_info:
        commits = get_line_history(repo_info["repo_path"], "README", 1, 10)
        print(f"Found {len(commits)} commits")
        
        diff = get_commit_diff(repo_info["repo_path"], commits[0]["commit_hash"])
        print(f"Diff length: {len(diff)}")
````

---

## Hour 5-10: Claude Integration

### Step 9: Claude Service

**Prompt for Claude Code:**
Create app/services/claude_service.py:

Import:

httpx (for async HTTP)
os
json
typing


Class: ClaudeService
init(self):

Store API key from env
Set base URL: "https://api.anthropic.com/v1/messages"
Create httpx.AsyncClient with timeout=60


Method: analyze_commit(
self,
commit_hash: str,
commit_message: str,
file_diff: str,
bug_description: str,
file_path: str
) -> Dict[str, Any]:
Purpose: Send commit context to Claude for analysis
Implementation:

Build prompt:
'''
You are analyzing a git commit that may have introduced a bug.
Bug Report: {bug_description}
Commit Information:

Hash: {commit_hash}
Message: {commit_message}
File: {file_path}

Diff:



diff     {file_diff}
````
     
     Analyze this commit and provide:
     1. Root cause: Why this change caused the bug
     2. Developer intent: What the developer was trying to accomplish
     3. Minimal patch: A unified diff to fix the issue
     4. Confidence: Your confidence level (0.0-1.0)
     
     Return ONLY a JSON object with these exact keys:
     {
       "root_cause": "explanation",
       "developer_intent": "what they tried to do",
       "minimal_patch": "unified diff format",
       "confidence": 0.85
     }
     
     DO NOT include markdown code fences or any text outside the JSON.
     '''
   
   - Make API call:
     headers = {
       "x-api-key": self.api_key,
       "anthropic-version": "2023-06-01",
       "content-type": "application/json"
     }
     
     body = {
       "model": "claude-sonnet-4-20250514",
       "max_tokens": 2000,
       "messages": [{"role": "user", "content": prompt}]
     }
   
   - Parse response:
     - Extract content[0].text
     - Strip markdown code fences (```json ... ```)
     - Parse as JSON
     - Validate required keys exist
   
   - Return parsed dict
   
   Error handling:
   - Rate limit (429) -> wait and retry once
   - Network errors -> return error dict
   - JSON parse errors -> log raw response and return error dict

4. Add singleton pattern:
   _instance = None
   
   @classmethod
   def get_instance(cls):
       if cls._instance is None:
           cls._instance = cls()
       return cls._instance
````

---

### Step 10: Create Analyze Endpoint

**Prompt for Claude Code:**
````
Create app/routes/analyze.py:

1. Import:
   - FastAPI (APIRouter, HTTPException, BackgroundTasks)
   - Models from app.models.requests and responses
   - Git ops from app.utils.git_ops
   - ClaudeService from app.services.claude_service

2. Create router:
   router = APIRouter(tags=["analyze"])

3. POST /analyze-bug endpoint:

@router.post("/analyze-bug", response_model=AnalyzeBugResponse)
async def analyze_bug(request: AnalyzeBugRequest, background_tasks: BackgroundTasks):
    """
    Analyze a bug by tracing it back to its origin commit.
    
    Process:
    1. Clone the repository
    2. Run git blame to find which commit introduced the suspicious code
    3. Get commit history and diff
    4. Send to Claude for analysis
    5. Return structured results
    """
    
    Implementation:
    
    1. Validate repo URL (must be GitHub)
    
    2. Clone repo using clone_repo_context():
       with clone_repo_context(request.repo_url) as repo_info:
    
    3. Find first bad commit:
       commit_hash = find_first_bad_commit(
           repo_info["repo_path"],
           request.file_path,
           request.line_hint
       )
    
    4. Get commit history:
       if request.line_hint:
           commits = get_line_history(
               repo_info["repo_path"],
               request.file_path,
               request.line_hint,
               request.line_hint
           )
       else:
           # Get all commits for file
           commits = get_file_history(repo_info["repo_path"], request.file_path)
    
    5. Get diff for first_bad_commit:
       diff = get_commit_diff(
           repo_info["repo_path"],
           commit_hash,
           request.file_path
       )
    
    6. Get commit message from commits list
    
    7. Call Claude:
       claude = ClaudeService.get_instance()
       analysis = await claude.analyze_commit(
           commit_hash,
           commit_message,
           diff,
           request.bug_description,
           request.file_path
       )
    
    8. Format commits for response:
       commit_infos = [
           CommitInfo(
               commit_hash=c["commit_hash"],
               author=c["author"],
               timestamp=c["timestamp"],
               message=c["message"]
           )
           for c in commits[:10]  # Limit to 10 most recent
       ]
    
    9. Return response:
       return AnalyzeBugResponse(
           first_bad_commit=commit_hash,
           commits=commit_infos,
           file_path=request.file_path,
           analysis=ClaudeAnalysis(**analysis)
       )
    
    Error handling:
    - Catch all exceptions
    - Return HTTPException with appropriate status codes:
      - 400: Invalid input
      - 404: File not found
      - 500: Internal errors
    - Log full error details
    - Include helpful error messages for frontend

Add logging at each step for debugging.
````

---

### Step 11: Add Helper Endpoint for Diff

**Prompt for Claude Code:**
````
In app/routes/analyze.py, add GET endpoint:

@router.get("/diff")
async def get_diff(
    repo_url: str,
    commit_hash: str,
    file_path: Optional[str] = None
):
    """
    Get the diff for a specific commit.
    Used by frontend to show diffs on demand.
    """
    
    Implementation:
    1. Clone repo (or check cache - we'll add caching later)
    2. Call get_commit_diff()
    3. Return {"diff": diff_string}
    
    Error handling same as above.
````

---

### Step 12: Test Analyze Endpoint

**Manual test:**
````bash
# Start server
python app/main.py

# In another terminal:
curl -X POST http://localhost:8000/api/analyze-bug \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/SOME_SMALL_REPO",
    "bug_description": "Authentication fails with 401 error",
    "file_path": "auth.py",
    "line_hint": 45
  }'
````

**Expected:** JSON response with commits and Claude analysis

---

## Hour 10-15: DeepSeek OCR Integration

### Step 13: DeepSeek OCR Service

**Prompt for Claude Code:**
````
Create app/services/deepseek_service.py:

Purpose: Extract text from images (screenshots of code/logs) and analyze

1. Import:
   - httpx
   - base64
   - PIL (Image)
   - io
   - os

2. Class: DeepSeekOCRService

   __init__(self):
   - Store API key from env
   - Base URL for DeepSeek OCR API
   - httpx.AsyncClient

3. Method: extract_text_from_image(
       self,
       image_data: str  # base64 encoded
   ) -> str:
   
   Purpose: Extract text from image using DeepSeek OCR
   
   Implementation:
   - Decode base64 to bytes
   - Validate it's an image (use PIL)
   - Send to DeepSeek OCR API:
     headers = {
       "Authorization": f"Bearer {self.api_key}",
       "Content-Type": "application/json"
     }
     
     body = {
       "image": image_data,
       "language": "en",
       "features": ["text_detection", "code_recognition"]
     }
   
   - Parse response and extract text
   - Return plain text string
   
   Error handling:
   - Invalid image format
   - API errors
   - Empty results

4. Method: analyze_error_screenshot(
       self,
       image_data: str,
       bug_description: str
   ) -> Dict[str, Any]:
   
   Purpose: Extract error from screenshot and analyze with Claude
   
   Implementation:
   - Extract text from image
   - Identify error messages/stack traces
   - Send to Claude with prompt:
     '''
     Error screenshot text extracted:
     {extracted_text}
     
     User bug description:
     {bug_description}
     
     Identify:
     1. The main error message
     2. File and line number if visible
     3. Likely cause based on stack trace
     4. Suggested file/line to investigate
     
     Return JSON:
     {
       "error_message": "...",
       "file_path": "...",
       "line_hint": 123,
       "suggested_search": "keywords to search for"
     }
     '''
   
   - Return parsed analysis
   
   This gives us file_path and line_hint automatically!

5. Add singleton pattern like ClaudeService
````

---

### Step 14: OCR Analyze Endpoint

**Prompt for Claude Code:**
````
In app/routes/analyze.py, add POST endpoint:

@router.post("/analyze-bug-from-image")
async def analyze_bug_from_image(request: OCRAnalyzeRequest):
    """
    Analyze a bug from a screenshot of an error.
    
    Process:
    1. Extract text from image using DeepSeek OCR
    2. Parse error message and stack trace
    3. Identify file and line number
    4. Automatically call analyze_bug with extracted info
    """
    
    Implementation:
    
    1. Call DeepSeekOCRService:
       ocr = DeepSeekOCRService.get_instance()
       analysis = await ocr.analyze_error_screenshot(
           request.image_data,
           request.bug_description
       )
    
    2. If we got file_path and line_hint, automatically analyze:
       if analysis.get("file_path"):
           # Call our existing analyze_bug logic
           bug_request = AnalyzeBugRequest(
               repo_url=request.repo_url,  # User must still provide
               bug_description=request.bug_description,
               file_path=analysis["file_path"],
               line_hint=analysis.get("line_hint")
           )
           return await analyze_bug(bug_request)
    
    3. Otherwise return the OCR analysis for user to refine:
       return {
           "ocr_result": analysis,
           "message": "Please provide file_path manually"
       }
    
    This is the "magic" feature - upload error screenshot, get automatic analysis!
````

---

### Step 15: Test OCR Integration

**Create test script:**
````python
# test_ocr.py
import base64
import httpx

# Take a screenshot of an error in your terminal/browser
# Save as error.png

with open("error.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = httpx.post(
    "http://localhost:8000/api/analyze-bug-from-image",
    json={
        "image_data": image_data,
        "bug_description": "Got this error and don't know where it's from"
    }
)

print(response.json())
````

---

## Hour 15-18: GitHub PR Creation

### Step 16: GitHub Service

**Prompt for Claude Code:**
````
Create app/services/github_service.py:

1. Import:
   - github (PyGithub)
   - os
   - re

2. Class: GitHubService

   __init__(self):
   - Store token from env
   - Create Github instance: github.Github(self.token)

3. Method: parse_repo_url(repo_url: str) -> Tuple[str, str]:
   - Extract owner and repo from URL
   - "https://github.com/owner/repo" -> ("owner", "repo")
   - Handle .git suffix
   - Validate format

4. Method: create_pull_request(
       self,
       repo_url: str,
       branch_name: str,
       patch_content: str,
       title: str,
       description: str
   ) -> str:
   
   Purpose: Create a PR with the suggested fix
   
   Implementation:
   - Parse owner/repo from URL
   - Get repo: self.github.get_repo(f"{owner}/{repo}")
   - Get default branch: repo.default_branch
   - Get latest commit on default branch
   - Create new branch from default:
     ref = f"refs/heads/{branch_name}"
     repo.create_git_ref(ref, default_sha)
   
   - For MVP: Just create branch and empty PR
     (Applying patch is complex - we can fake it)
   
   - Create PR:
     pr = repo.create_pull(
       title=title,
       body=description,
       head=branch_name,
       base=repo.default_branch
     )
   
   - Return PR HTML URL
   
   Error handling:
   - Invalid repo (404)
   - No permission (403)
   - Branch already exists

5. Add singleton pattern
````

---

### Step 17: Create PR Endpoint

**Prompt for Claude Code:**
````
In app/routes/analyze.py, add POST endpoint:

@router.post("/create-pr", response_model=CreatePRResponse)
async def create_pr(request: CreatePRRequest):
    """
    Create a pull request with the suggested fix.
    """
    
    Implementation:
    
    1. Validate inputs
    
    2. Call GitHubService:
       gh = GitHubService.get_instance()
       pr_url = gh.create_pull_request(
           request.repo_url,
           request.branch_name,
           request.patch_content,
           request.title,
           request.description
       )
    
    3. Return response:
       return CreatePRResponse(
           success=True,
           pr_url=pr_url,
           branch_name=request.branch_name
       )
    
    Error handling:
    - Catch GitHub API errors
    - Return helpful error messages
````

---

### Step 18: Add Caching (Performance)

**Prompt for Claude Code:**
````
Create app/utils/cache.py:

Simple in-memory cache for cloned repos to avoid re-cloning

1. Import:
   - time
   - typing

2. Class: RepoCache

   Structure:
   - _cache: Dict[str, Dict]
     Key: repo_url
     Value: {
       "repo_path": str,
       "timestamp": float,
       "cleanup": callable
     }
   
   - TTL: 3600 seconds (1 hour)

3. Methods:
   - get(repo_url: str) -> Optional[Dict]
     Check if repo in cache and not expired
   
   - set(repo_url: str, repo_info: Dict)
     Add to cache with current timestamp
   
   - cleanup_expired()
     Remove entries older than TTL
   
   - clear()
     Remove all entries

4. Update clone_repo() in git_ops.py:
   - Check cache first
   - If hit, return cached repo_path
   - If miss, clone and add to cache
````

---

## Hour 18-22: Testing & Polish

### Step 19: Add Logging

**Prompt for Claude Code:**
````
Create app/utils/logger.py:

Set up proper logging for debugging

1. Import logging, sys

2. Configure:
   - Format: "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
   - Level: DEBUG if env var DEBUG=true, else INFO
   - Output: Both file (logs/app.log) and console

3. Export get_logger(name: str) function

4. Update all files to use:
   logger = get_logger(__name__)
   logger.info("Cloning repo...")
   logger.error("Failed to clone", exc_info=True)
````

---

### Step 20: Add Comprehensive Error Messages

**Prompt for Claude Code:**
````
Update app/routes/analyze.py:

Improve error handling to be super helpful for users:

1. Wrap main logic in try/except
2. Catch specific exceptions:
   - git.exc.GitCommandError -> "Git operation failed: {details}"
   - FileNotFoundError -> "File '{file_path}' not found in repo"
   - httpx.HTTPError -> "API call failed: {service_name}"
   - json.JSONDecodeError -> "Failed to parse response"
   - Exception -> "Unexpected error: {message}"

3. Return error responses with:
   - "error": error message
   - "suggestion": what user should do
   - "details": technical details (in debug mode)

Example:
{
  "error": "File 'auth.py' not found in repository",
  "suggestion": "Check the file path - try 'src/auth.py' or use OCR to auto-detect",
  "status": 404
}
````

---

### Step 21: Create Demo Data Script

**Prompt for Claude Code:**
````
Create scripts/create_demo_bug.py:

Purpose: Create a demo repo with a known bug for testing

1. Create temp repo with git
2. Add initial files (auth.py with working code)
3. Commit: "Initial auth system"
4. Make refactor that introduces bug (remove null check)
5. Commit: "Refactor auth for clarity"
6. Add more commits on top
7. Push to your GitHub (or just keep local)

This gives you a controlled test case.
````

---

### Step 22: Write Integration Tests

**Prompt for Claude Code:**
````
Create tests/test_analyze.py:

Using pytest:

1. Test clone_repo():
   - Valid URL
   - Invalid URL
   - Network timeout

2. Test run_git_blame():
   - Valid file
   - Non-existent file
   - Binary file

3. Test analyze_bug endpoint:
   - Valid request
   - Missing fields
   - Invalid repo

4. Test OCR endpoint:
   - Valid image
   - Invalid base64
   - Empty image

Run with: pytest tests/ -v
````

---

### Step 23: API Documentation

**Prompt for Claude Code:**
````
Update app/main.py:

Add comprehensive API documentation for FastAPI auto-docs:

1. Update all endpoint docstrings with:
   - Description
   - Parameters explanation
   - Example request
   - Example response

2. Add OpenAPI tags and metadata

3. Visit http://localhost:8000/docs to see beautiful Swagger UI

4. Test all endpoints through the UI
````

---

### Step 24: Performance Optimization

**Prompt for Claude Code:**
````
Optimizations to add:

1. In git_ops.py:
   - Add @lru_cache to frequently called functions
   - Limit diff size before sending to Claude
   - Use shallow clones (depth=1)

2. In claude_service.py:
   - Add request timeout (30s)
   - Implement retry logic (max 2 retries)
   - Cache Claude responses for identical inputs

3. In main.py:
   - Add rate limiting (slowapi)
   - Add request size limits
   - Add GZIP compression middleware

4. Background cleanup:
   - Scheduled task to cleanup old clones
   - Cleanup cache every hour
````

---

### Step 25: Create Comprehensive README

**Create backend/README.md:**
````markdown
# BugRewind Backend

Python FastAPI backend for git archaeology and bug analysis.

## Features
- 🔍 Git blame analysis
- 🤖 Claude-powered root cause analysis
- 📸 DeepSeek OCR for error screenshots
- 🔧 Automatic PR creation
- ⚡ Caching for performance

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in API keys
python app/main.py
```

## API Endpoints

### POST /api/analyze-bug
Analyze a bug from description

Request:
```json
{
  "repo_url": "https://github.com/user/repo",
  "bug_description": "Auth fails with 401",
  "file_path": "src/auth.py",
  "line_hint": 45
}
```

Response: [example]

### POST /api/analyze-bug-from-image
Analyze from error screenshot

Request:
```json
{
  "image_data": "base64_encoded_image",
  "bug_description": "Got this error"
}
```

### POST /api/create-pr
Create PR with fix

[etc...]

## Architecture
[Diagram of flow]

## Development

Run tests:
```bash
pytest tests/ -v
```

Run with auto-reload:
```bash
uvicorn app.main:app --reload
```

## Deployment
[Deployment instructions]
````

---

**DEV A FINAL CHECKLIST:**

By hour 22, you should have:
- [x] FastAPI server running
- [x] Git operations (blame, log, diff)
- [x] Safe repo cloning with cleanup
- [x] Claude integration for analysis
- [x] DeepSeek OCR for screenshots (UNIQUE FEATURE!)
- [x] GitHub PR creation
- [x] Caching for performance
- [x] Comprehensive error handling
- [x] Logging for debugging
- [x] API documentation
- [x] Tests
- [x] README

**Your unique contribution:** The OCR feature lets users upload error screenshots and automatically extract file/line info - this is a killer feature!

Test everything end-to-end before declaring done.
