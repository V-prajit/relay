# DEV_C_GUIDE.md

```markdown
# DEV C: Next.js Frontend + UI/UX

**Your Mission:** Build a beautiful, functional web interface that showcases BugRewind's capabilities and integrates with backend + Postman Action

**Time Budget:** 22 hours total
- Hours 0-4: Setup + input form
- Hours 4-8: API integration + results display
- Hours 8-12: Diff viewer + commit timeline
- Hours 12-16: Polish, animations, and loading states
- Hours 16-20: Responsive design + accessibility
- Hours 20-22: Deployment + testing

---

## Hour 0-2: Project Setup

### Step 1: Create Next.js Project

**Run in terminal:**
```bash
# Create frontend directory
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

# Navigate to project
cd frontend

# Install additional dependencies
npm install axios react-diff-viewer-lite lucide-react react-hot-toast @headlessui/react clsx tailwind-merge
```

**During setup, answer:**
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ App Router (not Pages)
- ❌ src/ directory (keep it simple)
- ❌ Turbopack (not needed)
- ✅ Import alias (@/*)

**Expected result:** Fresh Next.js project

---

### Step 2: Configure Environment Variables

**Create `frontend/.env.local`:**
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_POSTMAN_ACTION_URL=https://api.postman.com/actions/YOUR_ID/run
```

**Note:** `NEXT_PUBLIC_` prefix makes variables accessible in browser

---

### Step 3: Set Up Tailwind Config

**Prompt for Claude Code:**
```
Update frontend/tailwind.config.ts with a custom theme:

1. Extend the default theme with:
   - Custom colors:
     {
       primary: {
         50: '#eff6ff',
         100: '#dbeafe',
         500: '#3b82f6',
         600: '#2563eb',
         700: '#1d4ed8',
       },
       accent: {
         500: '#8b5cf6',
         600: '#7c3aed',
       }
     }
   
   - Custom fonts:
     fontFamily: {
       sans: ['Inter', 'system-ui', 'sans-serif'],
       mono: ['JetBrains Mono', 'monospace']
     }
   
   - Custom animations:
     animation: {
       'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
       'fade-in': 'fadeIn 0.5s ease-in-out',
     }
     keyframes: {
       fadeIn: {
         '0%': { opacity: '0', transform: 'translateY(10px)' },
         '100%': { opacity: '1', transform: 'translateY(0)' }
       }
     }

2. Enable dark mode with 'class' strategy

3. Add custom utilities:
   plugins: [
     require('@tailwindcss/typography'),  // if installed
   ]
```

---

### Step 4: Create Utility Functions

**Prompt for Claude Code:**
```
Create frontend/lib/utils.ts with helper functions:

1. Import clsx and tailwind-merge

2. Function: cn(...inputs: ClassValue[]): string
   Purpose: Merge Tailwind classes intelligently
   
   import { type ClassValue, clsx } from 'clsx'
   import { twMerge } from 'tailwind-merge'
   
   export function cn(...inputs: ClassValue[]) {
     return twMerge(clsx(inputs))
   }

3. Function: formatRelativeTime(timestamp: number): string
   Purpose: Convert unix timestamp to "2 hours ago" format
   
   export function formatRelativeTime(timestamp: number): string {
     const now = Date.now()
     const diff = now - timestamp * 1000  // Convert to ms
     
     const seconds = Math.floor(diff / 1000)
     const minutes = Math.floor(seconds / 60)
     const hours = Math.floor(minutes / 60)
     const days = Math.floor(hours / 24)
     
     if (days > 0) return `${days}d ago`
     if (hours > 0) return `${hours}h ago`
     if (minutes > 0) return `${minutes}m ago`
     return 'just now'
   }

4. Function: truncate(text: string, length: number): string
   Purpose: Truncate long text with ellipsis
   
   export function truncate(text: string, length: number): string {
     if (text.length <= length) return text
     return text.slice(0, length) + '...'
   }

5. Function: extractRepoName(url: string): string
   Purpose: Extract "owner/repo" from GitHub URL
   
   export function extractRepoName(url: string): string {
     const match = url.match(/github\.com\/([^\/]+\/[^\/]+)/)
     return match ? match[1].replace('.git', '') : url
   }

6. Function: copyToClipboard(text: string): Promise<void>
   Purpose: Copy text to clipboard with fallback
   
   export async function copyToClipboard(text: string): Promise<void> {
     try {
       await navigator.clipboard.writeText(text)
     } catch {
       // Fallback for older browsers
       const textarea = document.createElement('textarea')
       textarea.value = text
       document.body.appendChild(textarea)
       textarea.select()
       document.execCommand('copy')
       document.body.removeChild(textarea)
     }
   }

Add proper TypeScript types throughout.
```

---

### Step 5: Create TypeScript Types

**Prompt for Claude Code:**
```
Create frontend/types/index.ts with all type definitions:

1. API Request types:

export interface AnalyzeBugRequest {
  repo_url: string
  bug_description: string
  file_path: string
  line_hint?: number
}

2. API Response types:

export interface CommitInfo {
  commit_hash: string
  author: string
  timestamp: number
  message: string
  line_number?: number
}

export interface ClaudeAnalysis {
  root_cause: string
  developer_intent: string
  minimal_patch: string
  confidence: number
}

export interface AnalyzeBugResponse {
  first_bad_commit: string
  commits: CommitInfo[]
  file_path: string
  analysis: ClaudeAnalysis
}

3. Postman Action response:

export interface PostmanActionResponse {
  success: boolean
  agent_decision: {
    action: string
    reasoning: string
    confidence: number
  }
  elastic_search: {
    performed: boolean
    results_count: number
    top_commit: string
  }
  analysis: {
    first_bad_commit: string
    root_cause: string
    developer_intent: string
    confidence: number
    commits_analyzed: number
  }
  pull_request: {
    created: boolean
    url: string
    branch: string
  }
  metadata: {
    timestamp: string
    execution_time_ms: number
    repo: string
    file: string
  }
}

4. UI State types:

export interface AppState {
  loading: boolean
  results: AnalyzeBugResponse | null
  error: string | null
  selectedCommit: string | null
  diff: string | null
}

5. Form types:

export interface BugFormData {
  repoUrl: string
  bugDescription: string
  filePath: string
  lineHint: string
}
```

---

## Hour 2-4: Build Input Form

### Step 6: Create Main Layout

**Prompt for Claude Code:**
```
Create frontend/app/layout.tsx:

A clean, modern layout with:

1. Import:
   - Inter font from next/font/google
   - Toaster from react-hot-toast
   - globals.css

2. Metadata:
   - title: "BugRewind - Git Archaeology for Bugs"
   - description: "AI-powered bug origin finder"
   - Add favicon and og:image

3. Root layout structure:
   <html lang="en" className="scroll-smooth">
     <body className={inter.className}>
       <nav>
         {/* Header with logo and links */}
       </nav>
       
       <main className="min-h-screen">
         {children}
       </main>
       
       <footer>
         {/* Footer with Cal Hacks branding */}
       </footer>
       
       <Toaster position="top-right" />
     </body>
   </html>

4. Nav bar should have:
   - Logo/title: "🔍 BugRewind"
   - Links: About, Docs, GitHub
   - Gradient background

5. Footer should have:
   - "Built for Cal Hacks 12.0"
   - Tech badges (Elastic, Claude, Postman)
   - Team credits

Use modern Tailwind styling with glassmorphism effects.
```

---

### Step 7: Create Hero Section

**Prompt for Claude Code:**
```
Create frontend/components/Hero.tsx:

Purpose: Eye-catching landing section before the form

Component structure:

1. Gradient background (blue to purple)
2. Animated heading:
   "Time Travel Through Your Codebase"
   "Find bugs at their source, not their symptom"
3. Feature badges:
   - 🔍 Git Archaeology
   - 🤖 AI Vision Analysis
   - 🖼️ Visual Context Compression (10-40x token reduction)
   - 🔧 Auto PR Generation
4. "Get Started" CTA that scrolls to form

Styling:
- Use Tailwind gradient backgrounds
- Add subtle animations (fade in, slide up)
- Responsive: full-width on mobile, centered on desktop
- Max width: max-w-6xl

Example code structure:
<section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-pink-500 py-20">
  <div className="max-w-6xl mx-auto px-4">
    <h1 className="text-5xl font-bold text-white animate-fade-in">
      Time Travel Through Your Codebase
    </h1>
    {/* ... more content */}
  </div>
</section>

Export as default.
```

---

### Step 8: Create Bug Analysis Form

**Prompt for Claude Code:**
```
Create frontend/components/BugForm.tsx:

Purpose: Main form for bug submission

Props:
- onSubmit: (data: BugFormData) => void
- loading: boolean

Component features:

1. Form fields:
   - Repo URL (required)
     - Placeholder: "https://github.com/owner/repo"
     - Validation: Must be GitHub URL
     - Show repo name preview below
   
   - Bug Description (required)
     - Textarea, 4 rows
     - Placeholder: "Describe the bug you're investigating..."
     - Character count: show "X/500"
     - Min 20 chars
   
   - File Path (required)
     - Placeholder: "src/auth/middleware.py"
     - Helper text: "Path relative to repo root"
   
   - Line Hint (optional)
     - Number input
     - Placeholder: "45"
     - Helper text: "Leave empty to analyze entire file"

2. Submit button:
   - Disabled when loading or invalid
   - Show spinner when loading
   - Text: "Analyze Bug Origin" or "Analyzing..."

3. Styling:
   - White card with shadow
   - Rounded corners (rounded-xl)
   - Each field has label, input, helper text
   - Error messages in red below fields
   - Focus states with blue ring

4. Validation:
   - Real-time validation on blur
   - Show error messages
   - Disable submit if invalid

5. State management:
   - Use React Hook Form or useState
   - Track form values, errors, touched fields

Example structure:
<form onSubmit={handleSubmit} className="space-y-6 bg-white rounded-xl shadow-lg p-8">
  <div className="space-y-2">
    <label className="text-sm font-medium text-gray-700">
      Repository URL *
    </label>
    <input
      type="url"
      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
      {...register('repoUrl', { required: true })}
    />
    {errors.repoUrl && <p className="text-sm text-red-600">Required</p>}
  </div>
  {/* More fields... */}
  
  <button
    type="submit"
    disabled={loading || !isValid}
    className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
  >
    {loading ? (
      <span className="flex items-center justify-center">
        <Loader className="animate-spin mr-2" />
        Analyzing...
      </span>
    ) : (
      'Analyze Bug Origin'
    )}
  </button>
</form>

Use lucide-react for icons (Loader, Github, FileCode, Hash)

Export as default.
```

---

### Step 9: Connect Form to Backend API

**Prompt for Claude Code:**
```
Create frontend/lib/api.ts:

Purpose: API client for backend communication

1. Import axios

2. Create axios instance:
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
  timeout: 120000,  // 2 minutes (git ops are slow)
  headers: {
    'Content-Type': 'application/json',
  },
})

3. Add request/response interceptors for logging:
api.interceptors.request.use(config => {
  console.log('API Request:', config.method?.toUpperCase(), config.url)
  return config
})

api.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.config.url)
    return response
  },
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

4. API functions:

export async function analyzeBug(data: AnalyzeBugRequest): Promise<AnalyzeBugResponse> {
  const response = await api.post('/api/analyze-bug', data)
  return response.data
}

export async function getCompressionStats(): Promise<{
  total_analyses: number
  avg_compression_ratio: number
  tokens_saved: number
  cost_savings_usd: number
}> {
  const response = await api.get('/api/compression-stats')
  return response.data
}

export async function getCommitDiff(
  repoUrl: string,
  commitHash: string,
  filePath: string
): Promise<string> {
  const response = await api.get('/api/diff', {
    params: { repo_url: repoUrl, commit_hash: commitHash, file_path: filePath }
  })
  return response.data.diff
}

export async function createPR(data: {
  repo_url: string
  branch_name: string
  patch_content: string
  title: string
  description: string
}): Promise<{ pr_url: string }> {
  const response = await api.post('/api/create-pr', data)
  return response.data
}

5. Postman Action function:

export async function callPostmanAction(data: AnalyzeBugRequest): Promise<PostmanActionResponse> {
  const response = await axios.post(
    process.env.NEXT_PUBLIC_POSTMAN_ACTION_URL!,
    data,
    { timeout: 180000 }  // 3 minutes
  )
  return response.data
}

6. Error handling wrapper:

export function handleAPIError(error: any): string {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with error
      return error.response.data?.error || error.response.data?.message || 'Server error'
    } else if (error.request) {
      // No response received
      return 'No response from server. Is the backend running?'
    }
  }
  return error.message || 'Unknown error'
}

Export all functions.
```

---

### Step 10: Update Main Page with Form

**Prompt for Claude Code:**
```
Update frontend/app/page.tsx:

Purpose: Main page with form and results

1. Import:
   - Hero component
   - BugForm component
   - useState, useCallback
   - API functions
   - toast from react-hot-toast
   - Types

2. State management:
'use client'

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<AnalyzeBugResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState<BugFormData | null>(null)

3. Submit handler:
const handleSubmit = async (data: BugFormData) => {
  setLoading(true)
  setError(null)
  setResults(null)
  setFormData(data)
  
  try {
    const response = await analyzeBug({
      repo_url: data.repoUrl,
      bug_description: data.bugDescription,
      file_path: data.filePath,
      line_hint: data.lineHint ? parseInt(data.lineHint) : undefined,
    })
    
    setResults(response)
    toast.success('Analysis complete!')
    
    // Scroll to results
    setTimeout(() => {
      document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  } catch (err) {
    const errorMsg = handleAPIError(err)
    setError(errorMsg)
    toast.error(errorMsg)
  } finally {
    setLoading(false)
  }
}

4. Layout:
return (
  <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
    <Hero />
    
    <div className="max-w-4xl mx-auto px-4 py-12" id="form">
      <BugForm onSubmit={handleSubmit} loading={loading} />
      
      {error && (
        <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}
    </div>
    
    {results && (
      <div id="results" className="max-w-7xl mx-auto px-4 py-12">
        {/* Results components will go here */}
        <pre className="bg-white p-4 rounded-lg overflow-auto">
          {JSON.stringify(results, null, 2)}
        </pre>
      </div>
    )}
  </div>
)

For now, just show raw JSON. We'll build proper result components next.
```

**Test at this point:**
```bash
npm run dev
# Visit http://localhost:3000
# Fill form and submit
# Should see JSON response
```

---

## Hour 4-8: Results Display Components

### Step 11: Create Commit List Component

**Prompt for Claude Code:**
```
Create frontend/components/CommitList.tsx:

Purpose: Display timeline of commits with selection

Props:
- commits: CommitInfo[]
- selectedCommit: string | null
- onSelectCommit: (hash: string) => void
- firstBadCommit: string

Component features:

1. Layout:
   - Vertical list with timeline line on left
   - Each commit is a card
   - Timeline dots connect commits
   - Highlight first_bad_commit in red

2. Commit card shows:
   - Short hash (first 7 chars) - monospace font
   - Commit message (truncated to 60 chars)
   - Author name
   - Relative timestamp ("2 hours ago")
   - "🐛 Bug Origin" badge if first_bad_commit

3. Interaction:
   - Click to select
   - Selected commit has blue border
   - Hover effect

4. Visual design:
   - Timeline line: vertical border-l-2 border-gray-300
   - Timeline dots: absolute circles
   - First bad commit: red dot and border
   - Selected: blue border-2
   - Hover: shadow-md

Example structure:
<div className="space-y-4">
  <h2 className="text-2xl font-bold">Commit History</h2>
  <div className="relative">
    {/* Timeline line */}
    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-300" />
    
    {commits.map((commit, index) => (
      <div key={commit.commit_hash} className="relative pl-12">
        {/* Timeline dot */}
        <div className={cn(
          "absolute left-2.5 w-3 h-3 rounded-full",
          commit.commit_hash === firstBadCommit ? "bg-red-500" : "bg-blue-500"
        )} />
        
        {/* Commit card */}
        <div
          onClick={() => onSelectCommit(commit.commit_hash)}
          className={cn(
            "p-4 bg-white rounded-lg shadow cursor-pointer transition-all",
            "hover:shadow-md",
            selectedCommit === commit.commit_hash && "ring-2 ring-blue-500"
          )}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                  {commit.commit_hash.slice(0, 7)}
                </code>
                {commit.commit_hash === firstBadCommit && (
                  <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">
                    🐛 Bug Origin
                  </span>
                )}
              </div>
              
              <p className="text-sm text-gray-900 mb-1">
                {truncate(commit.message, 60)}
              </p>
              
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span>{commit.author}</span>
                <span>•</span>
                <span>{formatRelativeTime(commit.timestamp)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    ))}
  </div>
</div>

Use lucide-react icons if needed (GitCommit, User, Clock)

Export as default.
```

---

### Step 12: Create Diff Viewer Component

**Prompt for Claude Code:**
```
Create frontend/components/DiffViewer.tsx:

Purpose: Show code diff with syntax highlighting

Props:
- diff: string | null
- loading: boolean
- fileName: string

Component features:

1. Use react-diff-viewer-lite for rendering
2. Parse unified diff format:
   - Extract old/new content
   - Identify added/removed lines
3. Syntax highlighting for code
4. Line numbers
5. Copy button for diff

Implementation:

import { DiffViewer } from 'react-diff-viewer-lite'
import 'react-diff-viewer-lite/dist/index.css'

const DiffViewerComponent = ({ diff, loading, fileName }: Props) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
        <Loader className="animate-spin text-gray-400" size={32} />
      </div>
    )
  }
  
  if (!diff) {
    return (
      <div className="text-center py-12 text-gray-500">
        Select a commit to view diff
      </div>
    )
  }
  
  // Parse diff
  const lines = diff.split('\n')
  const oldCode = lines.filter(l => !l.startsWith('+')).map(l => l.slice(1)).join('\n')
  const newCode = lines.filter(l => !l.startsWith('-')).map(l => l.slice(1)).join('\n')
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{fileName}</h3>
        <button
          onClick={() => copyToClipboard(diff)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Copy Diff
        </button>
      </div>
      
      <div className="border rounded-lg overflow-hidden">
        <DiffViewer
          oldValue={oldCode}
          newValue={newCode}
          splitView={false}
          useDarkTheme={false}
          hideLineNumbers={false}
        />
      </div>
    </div>
  )
}

For MVP: Can also use a simple <pre> with monospace font if react-diff-viewer-lite is buggy:

<pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto text-sm">
  {diff}
</pre>

Export as default.
```

---

### Step 13: Create Analysis Card Component

**Prompt for Claude Code:**
```
Create frontend/components/AnalysisCard.tsx:

Purpose: Display Claude's analysis beautifully

Props:
- analysis: ClaudeAnalysis
- onCreatePR: () => void
- creating: boolean

Component features:

1. Card sections:
   - Root Cause (most prominent)
   - Developer Intent
   - Suggested Fix (code block)
   - Confidence meter

2. Each section:
   - Icon + title
   - Content with good typography
   - Appropriate styling

3. Confidence meter:
   - Progress bar
   - Color based on confidence:
     - > 0.8: green
     - 0.5-0.8: yellow
     - < 0.5: red

4. Create PR button at bottom

Example structure:
<div className="bg-white rounded-xl shadow-lg p-6 space-y-6">
  <h2 className="text-2xl font-bold">AI Analysis</h2>
  
  {/* Root Cause Section */}
  <div className="space-y-2">
    <div className="flex items-center gap-2 text-red-600">
      <AlertCircle size={20} />
      <h3 className="font-semibold">Root Cause</h3>
    </div>
    <p className="text-gray-700 leading-relaxed">
      {analysis.root_cause}
    </p>
  </div>
  
  {/* Developer Intent */}
  <div className="space-y-2">
    <div className="flex items-center gap-2 text-blue-600">
      <User size={20} />
      <h3 className="font-semibold">Developer Intent</h3>
    </div>
    <p className="text-gray-700 leading-relaxed">
      {analysis.developer_intent}
    </p>
  </div>
  
  {/* Suggested Fix */}
  <div className="space-y-2">
    <div className="flex items-center gap-2 text-green-600">
      <Code size={20} />
      <h3 className="font-semibold">Suggested Fix</h3>
    </div>
    <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-auto text-sm">
      {analysis.minimal_patch}
    </pre>
  </div>
  
  {/* Confidence Meter */}
  <div className="space-y-2">
    <div className="flex items-center justify-between">
      <span className="text-sm font-medium">Analysis Confidence</span>
      <span className="text-sm font-bold">
        {Math.round(analysis.confidence * 100)}%
      </span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-3">
      <div
        className={cn(
          "h-3 rounded-full transition-all",
          analysis.confidence > 0.8 ? "bg-green-500" :
          analysis.confidence > 0.5 ? "bg-yellow-500" : "bg-red-500"
        )}
        style={{ width: `${analysis.confidence * 100}%` }}
      />
    </div>
  </div>
  
  {/* Create PR Button */}
  <button
    onClick={onCreatePR}
    disabled={creating}
    className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
  >
    {creating ? (
      <>
        <Loader className="animate-spin" size={20} />
        Creating Pull Request...
      </>
    ) : (
      <>
        <GitPullRequest size={20} />
        Create Pull Request
      </>
    )}
  </button>
</div>

Use lucide-react icons: AlertCircle, User, Code, GitPullRequest, Loader

Export as default.
```

---

### Step 14: Integrate Components into Results View

**Prompt for Claude Code:**
```
Update frontend/app/page.tsx:

Replace the raw JSON display with proper components:

1. Import all result components:
   - CommitList
   - DiffViewer
   - AnalysisCard

2. Add more state:
const [selectedCommit, setSelectedCommit] = useState<string | null>(null)
const [diff, setDiff] = useState<string | null>(null)
const [loadingDiff, setLoadingDiff] = useState(false)
const [creatingPR, setCreatingPR] = useState(false)

3. Fetch diff when commit selected:
useEffect(() => {
  if (!selectedCommit || !formData) return
  
  setLoadingDiff(true)
  getCommitDiff(formData.repoUrl, selectedCommit, formData.filePath)
    .then(setDiff)
    .catch(err => toast.error('Failed to load diff'))
    .finally(() => setLoadingDiff(false))
}, [selectedCommit, formData])

4. Handle PR creation:
const handleCreatePR = async () => {
  if (!results || !formData) return
  
  setCreatingPR(true)
  try {
    const { pr_url } = await createPR({
      repo_url: formData.repoUrl,
      branch_name: `bugrewind-fix-${Date.now()}`,
      patch_content: results.analysis.minimal_patch,
      title: `Fix: ${truncate(results.analysis.root_cause, 60)}`,
      description: `## BugRewind Automated Fix\n\n**Root Cause:**\n${results.analysis.root_cause}\n\n**Developer Intent:**\n${results.analysis.developer_intent}\n\n**First Bad Commit:** ${results.first_bad_commit}`
    })
    
    toast.success('Pull request created!')
    window.open(pr_url, '_blank')
  } catch (err) {
    toast.error(handleAPIError(err))
  } finally {
    setCreatingPR(false)
  }
}

5. Results layout - two column grid:
{results && (
  <div id="results" className="max-w-7xl mx-auto px-4 py-12">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Left column: Commits + Diff */}
      <div className="space-y-6">
        <CommitList
          commits={results.commits}
          selectedCommit={selectedCommit}
          onSelectCommit={setSelectedCommit}
          firstBadCommit={results.first_bad_commit}
        />
        
        <DiffViewer
          diff={diff}
          loading={loadingDiff}
          fileName={results.file_path}
        />
      </div>
      
      {/* Right column: Analysis */}
      <div className="lg:sticky lg:top-8 h-fit">
        <AnalysisCard
          analysis={results.analysis}
          onCreatePR={handleCreatePR}
          creating={creatingPR}
        />
      </div>
    </div>
    
    {/* "Analyze Another Bug" button */}
    <div className="mt-12 text-center">
      <button
        onClick={() => {
          setResults(null)
          setSelectedCommit(null)
          setDiff(null)
          window.scrollTo({ top: 0, behavior: 'smooth' })
        }}
        className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
      >
        Analyze Another Bug
      </button>
    </div>
  </div>
)}

6. Auto-select first commit:
useEffect(() => {
  if (results && results.commits.length > 0) {
    setSelectedCommit(results.first_bad_commit)
  }
}, [results])
```

**Test end-to-end at this point!**

---

## Hour 8-12: Advanced Features

### Step 15: Add Loading Skeleton

**Prompt for Claude Code:**
```
Create frontend/components/LoadingSkeleton.tsx:

Purpose: Show pretty loading state while analyzing

Component:

export default function LoadingSkeleton() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 animate-fade-in">
      <div className="bg-white rounded-xl shadow-lg p-8 space-y-8">
        {/* Header */}
        <div className="space-y-3">
          <div className="h-8 bg-gray-200 rounded w-1/3 animate-pulse" />
          <div className="h-4 bg-gray-200 rounded w-2/3 animate-pulse" />
        </div>
        
        {/* Progress steps */}
        <div className="space-y-4">
          <Step text="Cloning repository..." complete />
          <Step text="Running git blame..." complete />
          <Step text="Analyzing with Claude..." active />
          <Step text="Generating fix suggestion..." />
        </div>
        
        {/* Fun fact */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            💡 <strong>Did you know?</strong> The average bug exists in codebases 
            for 73 days before being fixed. We're finding its origin in seconds!
          </p>
        </div>
      </div>
    </div>
  )
}

function Step({ text, complete, active }: { text: string, complete?: boolean, active?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className={cn(
        "w-6 h-6 rounded-full flex items-center justify-center",
        complete && "bg-green-500",
        active && "bg-blue-500 animate-pulse",
        !complete && !active && "bg-gray-300"
      )}>
        {complete && <Check size={16} className="text-white" />}
        {active && <Loader size={16} className="text-white animate-spin" />}
      </div>
      <span className={cn(
        "text-sm",
        complete && "text-gray-700",
        active && "text-blue-600 font-medium",
        !complete && !active && "text-gray-400"
      )}>
        {text}
      </span>
    </div>
  )
}

Update page.tsx to show this when loading=true
```

---

### Step 16: Add Stats Dashboard

**Prompt for Claude Code:**
```
Create frontend/components/StatsDisplay.tsx:

Purpose: Show quick stats about the analysis

Props:
- results: AnalyzeBugResponse

Component shows:
- Number of commits analyzed
- Time span (oldest to newest commit)
- Number of authors involved
- Confidence score (large)

Layout: 4 stat cards in a grid

<div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
  <StatCard
    icon={<GitCommit />}
    label="Commits Analyzed"
    value={results.commits.length}
    color="blue"
  />
  <StatCard
    icon={<Clock />}
    label="Time Span"
    value={calculateTimeSpan(results.commits)}
    color="purple"
  />
  <StatCard
    icon={<Users />}
    label="Authors Involved"
    value={getUniqueAuthors(results.commits).length}
    color="green"
  />
  <StatCard
    icon={<TrendingUp />}
    label="Confidence"
    value={`${Math.round(results.analysis.confidence * 100)}%`}
    color="orange"
  />
</div>

function StatCard({ icon, label, value, color }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className={`text-${color}-600 mb-2`}>{icon}</div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  )
}

Add this to results section in page.tsx
```

---

### Step 17: Add Search/Filter for Commits

**Prompt for Claude Code:**
```
Add to CommitList component:

1. Search bar at top:
   - Filter commits by message or author
   - Real-time search

2. State:
const [search, setSearch] = useState('')
const filteredCommits = commits.filter(c => 
  c.message.toLowerCase().includes(search.toLowerCase()) ||
  c.author.toLowerCase().includes(search.toLowerCase())
)

3. UI:
<div className="mb-4">
  <input
    type="text"
    placeholder="Search commits..."
    value={search}
    onChange={(e) => setSearch(e.target.value)}
    className="w-full px-4 py-2 border rounded-lg"
  />
</div>

Use filteredCommits instead of commits in map
```

---

## Hour 12-16: Polish, Animations, and Token Savings Display

### The Hackathon Differentiator

While other teams focus on features, you'll showcase **cost savings** from visual context compression. This is what wins hackathons - demonstrating real-world value.

---

### Step 18: Create Token Savings Stats Component

**Prompt for Claude Code:**
```
Create frontend/components/TokenSavingsCard.tsx:

Purpose: Display real-time token savings from visual compression (the killer feature!)

Component:

'use client'

import { useEffect, useState } from 'react'
import { TrendingDown, DollarSign, Zap } from 'lucide-react'
import { getCompressionStats } from '@/lib/api'

export default function TokenSavingsCard() {
  const [stats, setStats] = useState<{
    total_analyses: number
    avg_compression_ratio: number
    tokens_saved: number
    cost_savings_usd: number
  } | null>(null)

  useEffect(() => {
    // Fetch stats on mount and every 10 seconds
    const fetchStats = async () => {
      try {
        const data = await getCompressionStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch compression stats', error)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 10000)
    return () => clearInterval(interval)
  }, [])

  if (!stats) return null

  return (
    <div className="bg-gradient-to-br from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="text-green-600" size={24} />
        <h3 className="font-semibold text-lg">Visual Compression Savings</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-gray-600">Avg Compression</p>
          <p className="text-2xl font-bold text-green-600">
            {stats.avg_compression_ratio.toFixed(1)}x
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-600">Tokens Saved</p>
          <p className="text-2xl font-bold text-blue-600">
            {stats.tokens_saved.toLocaleString()}
          </p>
        </div>

        <div>
          <p className="text-sm text-gray-600">Cost Savings</p>
          <p className="text-2xl font-bold text-purple-600">
            ${stats.cost_savings_usd.toFixed(2)}
          </p>
        </div>
      </div>

      <p className="text-xs text-gray-600 mt-4">
        Powered by DeepSeek-OCR visual context compression
      </p>
    </div>
  )
}

Export as default.
```

**Add to page.tsx** above the results section to showcase your innovation!

---

### Step 19: Add Loading Skeleton Components

**Prompt for Claude Code:**
```
Create frontend/components/LoadingSkeletons.tsx:

Purpose: Professional loading states while analysis runs

Components:

1. CommitListSkeleton - Animated cards for commit list
2. DiffViewerSkeleton - Loading state for diff viewer
3. AnalysisSkeleton - Placeholder for Claude analysis

Implementation:

'use client'

export function CommitListSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="border rounded-lg p-4 animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      ))}
    </div>
  )
}

export function DiffViewerSkeleton() {
  return (
    <div className="border rounded-lg p-6 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-3 bg-gray-200 rounded w-full"></div>
        ))}
      </div>
    </div>
  )
}

export function AnalysisSkeleton() {
  return (
    <div className="border rounded-lg p-6 animate-pulse">
      <div className="h-5 bg-gray-200 rounded w-2/3 mb-4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-4/5"></div>
      </div>
    </div>
  )
}

Use these in page.tsx while loading: {loading ? <CommitListSkeleton /> : <CommitList />}
```

---

### Step 20: Add Smooth Animations

**Prompt for Claude Code:**
```
Update components with enter/exit animations using framer-motion:

npm install framer-motion

In CommitList.tsx, wrap commit items:

import { motion } from 'framer-motion'

{commits.map((commit, i) => (
  <motion.div
    key={commit.commit_hash}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: i * 0.1 }}
  >
    <CommitCard {...commit} />
  </motion.div>
))}

Similarly add to:
- AnalysisCard (fade in from right)
- DiffViewer (fade in from left)
- TokenSavingsCard (scale up)

This creates a polished, professional feel!
```

---

## Hour 16-20: Polish & Responsive Design

**Note:** The Hours 12-16 section above focused on polish and token savings display - the hackathon differentiator! Now let's ensure everything works great on all devices.
      return
    }
    
    // Convert to base64
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target?.result as string
      setPreview(base64)
      onImageSelect(base64, file)
      toast.success('Image uploaded!')
    }
    reader.readAsDataURL(file)
  }
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }
  
  const clearImage = () => {
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }
  
  return (
    <div className="space-y-4">
      {!preview ? (
        <div
          onDragEnter={() => setDragActive(true)}
          onDragLeave={() => setDragActive(false)}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all",
            dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"
          )}
        >
          <Upload className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-600 mb-2">
            Drag & drop error screenshot here
          </p>
          <p className="text-sm text-gray-500">
            or click to browse (PNG, JPG up to 5MB)
          </p>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="hidden"
          />
        </div>
      ) : (
        <div className="relative">
          <img
            src={preview}
            alt="Upload preview"
            className="w-full rounded-lg border"
          />
          <button
            onClick={clearImage}
            className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600"
          >
            <X size={20} />
          </button>
        </div>
      )}
    </div>
  )
}

Export as default.
```

---

### Step 19: Create OCR Analysis Form

**Prompt for Claude Code:**
```
Create frontend/components/OCRForm.tsx:

Purpose: Alternative form using OCR

Component:

export default function OCRForm({ onSubmit, loading }: Props) {
  const [repoUrl, setRepoUrl] = useState('')
  const [description, setDescription] = useState('')
  const [imageData, setImageData] = useState<string | null>(null)
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!imageData) {
      toast.error('Please upload an error screenshot')
      return
    }
    onSubmit({ repoUrl, description, imageData })
  }
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <label className="text-sm font-medium">Repository URL *</label>
        <input
          type="url"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          required
          className="w-full px-4 py-2 border rounded-lg"
        />
      </div>
      
      <div className="space-y-2">
        <label className="text-sm font-medium">Error Screenshot *</label>
        <ImageUpload onImageSelect={(base64) => setImageData(base64)} />
        <p className="text-xs text-gray-500">
          Upload a screenshot of your error message or stack trace
        </p>
      </div>
      
      <div className="space-y-2">
        <label className="text-sm font-medium">Additional Context</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="w-full px-4 py-2 border rounded-lg"
          placeholder="Any additional context about the error..."
        />
      </div>
      
      <button
        type="submit"
        disabled={loading || !imageData}
        className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50"
      >
        {loading ? 'Analyzing Image...' : 'Analyze from Screenshot'}
      </button>
    </form>
  )
}

Export as default.
```

---

### Step 20: Add Tab Switcher for Forms

**Prompt for Claude Code:**
```
Update frontend/app/page.tsx:

Add tabs to switch between manual form and OCR form:

1. Add state:
const [activeTab, setActiveTab] = useState<'manual' | 'ocr'>('manual')

2. Add OCR submit handler:
const handleOCRSubmit = async (data: { repoUrl: string, description: string, imageData: string }) => {
  setLoading(true)
  setError(null)
  setResults(null)
  
  try {
    const response = await analyzeBugFromImage({
      repo_url: data.repoUrl,
      bug_description: data.description || 'Analyze error from screenshot',
      image_data: data.imageData
    })
    
    setResults(response)
    toast.success('OCR analysis complete!')
  } catch (err) {
    const errorMsg = handleAPIError(err)
    setError(errorMsg)
    toast.error(errorMsg)
  } finally {
    setLoading(false)
  }
}

3. Update form section:
<div className="max-w-4xl mx-auto px-4 py-12">
  {/* Tab buttons */}
  <div className="flex gap-2 mb-6 border-b">
    <button
      onClick={() => setActiveTab('manual')}
      className={cn(
        "px-6 py-3 font-medium border-b-2 transition-colors",
        activeTab === 'manual' 
          ? "border-blue-600 text-blue-600" 
          : "border-transparent text-gray-600 hover:text-gray-900"
      )}
    >
      Manual Input
    </button>
    <button
      onClick={() => setActiveTab('ocr')}
      className={cn(
        "px-6 py-3 font-medium border-b-2 transition-colors flex items-center gap-2",
        activeTab === 'ocr' 
          ? "border-purple-600 text-purple-600" 
          : "border-transparent text-gray-600 hover:text-gray-900"
      )}
    >
      <Camera size={20} />
      OCR Upload
      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
        New!
      </span>
    </button>
  </div>
  
  {/* Form content */}
  <div className="bg-white rounded-xl shadow-lg p-8">
    {activeTab === 'manual' ? (
      <BugForm onSubmit={handleSubmit} loading={loading} />
    ) : (
      <OCRForm onSubmit={handleOCRSubmit} loading={loading} />
    )}
  </div>
</div>

This gives users two ways to analyze: manual or screenshot upload!
```

---

## Hour 16-20: Polish & Responsive Design

### Step 21: Make Everything Mobile-Responsive

**Prompt for Claude Code:**
```
Update all components for mobile:

1. In page.tsx results section:
- Change grid from lg:grid-cols-2 to grid-cols-1 lg:grid-cols-2
- Stack vertically on mobile
- Remove sticky positioning on mobile

{results && (
  <div className="max-w-7xl mx-auto px-4 py-12">
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
      {/* Left column */}
      <div className="space-y-6">
        <CommitList {...} />
        <DiffViewer {...} />
      </div>
      
      {/* Right column - not sticky on mobile */}
      <div className="lg:sticky lg:top-8 h-fit">
        <AnalysisCard {...} />
      </div>
    </div>
  </div>
)}

2. In Hero.tsx:
- Reduce heading size on mobile
- Stack feature badges vertically
<h1 className="text-3xl md:text-5xl lg:text-6xl font-bold">

3. In BugForm.tsx:
- Full width inputs on mobile
- Adjust padding

4. In CommitList.tsx:
- Reduce padding on mobile
- Smaller font sizes

5. Test at breakpoints:
- 375px (mobile)
- 768px (tablet)
- 1024px (desktop)
```

---

### Step 22: Add Dark Mode Support (Optional but Cool)

**Prompt for Claude Code:**
```
Add dark mode toggle:

1. Create frontend/components/ThemeToggle.tsx:

'use client'

import { useState, useEffect } from 'react'
import { Moon, Sun } from 'lucide-react'

export default function ThemeToggle() {
  const [dark, setDark] = useState(false)
  
  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [dark])
  
  return (
    <button
      onClick={() => setDark(!dark)}
      className="p-2 rounded-lg bg-gray-200 dark:bg-gray-800"
    >
      {dark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  )
}

2. Add to layout navbar

3. Update components with dark: variants:
className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white"

This is optional - skip if short on time!
```

---

### Step 23: Add Animations

**Prompt for Claude Code:**
```
Make it feel alive with animations:

1. Install framer-motion:
npm install framer-motion

2. Add to CommitList:
import { motion } from 'framer-motion'

{commits.map((commit, index) => (
  <motion.div
    key={commit.commit_hash}
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: index * 0.1 }}
  >
    {/* Commit card content */}
  </motion.div>
))}

3. Add to AnalysisCard:
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.3 }}
>
  {/* Card content */}
</motion.div>

4. Add to results section:
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
>
  {/* Results content */}
</motion.div>

Smooth animations make it feel professional!
```

---

### Step 24: Add Postman Action Integration

**Prompt for Claude Code:**
```
Add "Deep Analysis" button that calls Postman Action:

1. In AnalysisCard.tsx, add second button:

<div className="grid grid-cols-2 gap-4">
  <button
    onClick={onCreatePR}
    disabled={creating}
    className="bg-green-600 text-white py-3 rounded-lg hover:bg-green-700"
  >
    Create PR
  </button>
  
  <button
    onClick={onDeepAnalysis}
    disabled={analyzing}
    className="bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700"
  >
    Deep Analysis
  </button>
</div>

2. In page.tsx, add handler:
const [postmanResults, setPostmanResults] = useState<PostmanActionResponse | null>(null)
const [analyzingDeep, setAnalyzingDeep] = useState(false)

const handleDeepAnalysis = async () => {
  if (!formData) return
  
  setAnalyzingDeep(true)
  try {
    const response = await callPostmanAction({
      repo_url: formData.repoUrl,
      bug_description: formData.bugDescription,
      file_path: formData.filePath,
      line_hint: formData.lineHint ? parseInt(formData.lineHint) : undefined
    })
    
    setPostmanResults(response)
    toast.success('Deep analysis complete!')
  } catch (err) {
    toast.error(handleAPIError(err))
  } finally {
    setAnalyzingDeep(false)
  }
}

3. Show Postman results in modal or expandable section:

{postmanResults && (
  <div className="mt-8 bg-purple-50 border border-purple-200 rounded-lg p-6">
    <h3 className="text-lg font-bold mb-4">Deep Analysis (Postman Flow)</h3>
    
    <div className="space-y-4">
      <div>
        <strong>Agent Decision:</strong>
        <p>{postmanResults.agent_decision.reasoning}</p>
      </div>
      
      <div>
        <strong>Elastic Search:</strong>
        <p>Found {postmanResults.elastic_search.results_count} relevant commits</p>
      </div>
      
      {postmanResults.pull_request.created && (
        <div>
          <strong>Pull Request:</strong>
          <a href={postmanResults.pull_request.url} target="_blank" className="text-blue-600">
            View PR
          </a>
        </div>
      )}
      
      <div className="text-xs text-gray-600">
        Execution time: {postmanResults.metadata.execution_time_ms}ms
      </div>
    </div>
  </div>
)}

This showcases the Postman Flow integration!
```

---

## Hour 20-22: Deployment & Documentation

### Step 25: Deploy to Vercel

**Manual steps:**

1. **Commit everything:**
```bash
git add .
git commit -m "Complete BugRewind frontend"
git push origin main
```

2. **Deploy to Vercel:**
```bash
npm i -g vercel  # If not installed
vercel --prod
```

Follow prompts:
- Link to existing project? No
- Project name: bugrewind
- Framework preset: Next.js
- Build settings: (use defaults)

**OR use Vercel dashboard:**
- Go to https://vercel.com
- Sign in with GitHub
- "Import Project"
- Select your repo
- Deploy

3. **Add environment variables in Vercel:**
- Go to project settings
- Environment Variables section
- Add:
  - `NEXT_PUBLIC_BACKEND_URL` = your production backend URL (or keep ngrok for demo)
  - `NEXT_PUBLIC_POSTMAN_ACTION_URL` = your Postman Action URL

4. **Redeploy after env vars:**
```bash
vercel --prod
```

**Expected result:** Live URL like `https://bugrewind.vercel.app`

---

### Step 26: Create README

**Create frontend/README.md:**

```markdown
# BugRewind Frontend

Modern Next.js web interface for BugRewind git archaeology.

## Features

✨ **Dual Input Modes**
- Manual form with repo URL, file path, and line hint
- OCR-powered screenshot upload for automatic error detection

🎨 **Beautiful UI**
- Responsive design (mobile to desktop)
- Smooth animations with Framer Motion
- Dark mode support
- Real-time loading states

📊 **Rich Results Display**
- Interactive commit timeline
- Side-by-side diff viewer
- AI analysis with confidence scoring
- One-click PR creation

🚀 **Advanced Features**
- Postman Flow integration for deep analysis
- Commit search and filtering
- Error state handling
- Toast notifications

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **HTTP**: Axios
- **Notifications**: React Hot Toast

## Getting Started

### Prerequisites
- Node.js 18+
- Backend running (see backend/README.md)

### Installation

```bash
cd frontend
npm install
```

### Configuration

Create `.env.local`:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_POSTMAN_ACTION_URL=https://api.postman.com/actions/YOUR_ID/run
```

### Development

```bash
npm run dev
```

Visit http://localhost:3000

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page
│   └── globals.css         # Global styles
├── components/
│   ├── Hero.tsx            # Landing section
│   ├── BugForm.tsx         # Manual input form
│   ├── OCRForm.tsx         # OCR upload form
│   ├── ImageUpload.tsx     # Image upload component
│   ├── CommitList.tsx      # Commit timeline
│   ├── DiffViewer.tsx      # Code diff display
│   ├── AnalysisCard.tsx    # AI analysis display
│   ├── LoadingSkeleton.tsx # Loading state
│   └── StatsDisplay.tsx    # Stats dashboard
├── lib/
│   ├── api.ts              # API client
│   └── utils.ts            # Utility functions
└── types/
    └── index.ts            # TypeScript types
```

## Components

### BugForm
Manual input form with validation.

### OCRForm
Screenshot upload with DeepSeek OCR integration.

### CommitList
Interactive timeline showing commit history with:
- Timeline visualization
- Commit selection
- Bug origin highlighting
- Search/filter

### DiffViewer
Code diff display using react-diff-viewer-lite.

### AnalysisCard
Claude's analysis with:
- Root cause explanation
- Developer intent
- Suggested fix (code)
- Confidence meter
- Action buttons (Create PR, Deep Analysis)

## API Integration

The frontend connects to:
1. **Backend API** (FastAPI)
   - `/api/analyze-bug` - Main analysis
   - `/api/analyze-bug-from-image` - OCR analysis
   - `/api/diff` - Get commit diffs
   - `/api/create-pr` - Create pull requests

2. **Postman Action**
   - Deep analysis via Postman Flow orchestration

## Deployment

Deployed on Vercel: https://bugrewind.vercel.app

### Deploy Your Own

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-repo/bugrewind)

## Testing

Manual testing checklist:
- [ ] Form validation works
- [ ] Bug analysis completes successfully
- [ ] OCR upload processes screenshots
- [ ] Commit selection updates diff
- [ ] PR creation opens GitHub
- [ ] Postman deep analysis runs
- [ ] Responsive on mobile
- [ ] Error states display properly

## Screenshots

See `/demo` folder for UI screenshots.

## Known Issues

- Diff viewer may not syntax highlight all languages
- Large repositories (>1000 commits) may timeout
- OCR works best with clear, high-contrast screenshots

## Future Improvements

- [ ] Save analysis history
- [ ] Export reports as PDF
- [ ] Share analysis via link
- [ ] Collaborative commenting
- [ ] Integration with Jira/Linear

## Team

Built by [Your Team] for Cal Hacks 12.0

## License

MIT
```

---

### Step 27: Create Demo Screenshots

**Take screenshots:**

1. **Landing page** (full screen)
   - Shows hero section and form tabs
   - Save as `demo/frontend-landing.png`

2. **Manual form filled out**
   - Show form with sample data
   - Save as `demo/frontend-form.png`

3. **OCR upload**
   - Show image upload interface
   - Save as `demo/frontend-ocr.png`

4. **Results view**
   - Full page with commits, diff, analysis
   - Save as `demo/frontend-results.png`

5. **Mobile view**
   - Responsive layout on phone
   - Save as `demo/frontend-mobile.png`

6. **Analysis card**
   - Close-up of Claude's analysis
   - Save as `demo/frontend-analysis.png`

---

### Step 28: Record Video Demo

**60-second frontend demo:**

```
[0:00-0:10] Landing Page
"Here's BugRewind's frontend. Clean, modern interface built with Next.js."

[0:10-0:25] Manual Form
"You can enter a repo URL, describe the bug, specify the file..."
[Fill form and submit]

[0:25-0:40] Results
"And here are the results. We get a commit timeline, Claude's analysis 
explaining exactly what went wrong, and a suggested fix."
[Click through commits, show diff]

[0:40-0:50] OCR Feature
"The killer feature: upload a screenshot of an error, and OCR automatically 
extracts the file and line number."
[Show OCR tab, upload image]

[0:50-0:60] PR Creation
"One click creates a pull request with the fix. That's the full workflow!"
[Click Create PR, show GitHub opens]
```

Upload to YouTube (unlisted)

---

### Step 29: Integration Testing

**Test full stack:**

1. **Backend running** ✓
2. **Frontend running** ✓
3. **Ngrok exposing backend** ✓

**End-to-end tests:**

```bash
# Test 1: Manual analysis
1. Fill form with real repo
2. Submit
3. Verify results load
4. Select commit
5. View diff
6. Click Create PR
7. Verify PR opens on GitHub

# Test 2: OCR analysis
1. Switch to OCR tab
2. Upload error screenshot
3. Submit
4. Verify analysis works

# Test 3: Postman integration
1. Analyze a bug
2. Click "Deep Analysis"
3. Verify Postman results show

# Test 4: Error handling
1. Enter invalid repo URL
2. Submit
3. Verify error message shows
4. Try again with valid data
```

**Coordinate with Dev B:** Make sure Postman Action calls work!

---

### Step 30: Final Checklist

**By hour 22, verify:**

- [x] Frontend deployed to Vercel
- [x] Manual form works end-to-end
- [x] OCR upload works
- [x] Commit timeline interactive
- [x] Diff viewer shows code changes
- [x] Analysis card displays beautifully
- [x] PR creation works
- [x] Postman Action integration works
- [x] Responsive on mobile
- [x] Loading states smooth
- [x] Error handling graceful
- [x] Toast notifications work
- [x] Dark mode (optional)
- [x] Animations smooth
- [x] README complete
- [x] Screenshots taken
- [x] Video demo recorded
- [x] Environment variables set in Vercel
- [x] Git repo pushed

**Deliverables:**

1. **Live URL**: `https://bugrewind.vercel.app`
2. **GitHub repo**: Link to code
3. **Demo video**: YouTube link
4. **Screenshots**: In `/demo` folder

---

## Emergency Troubleshooting

**If Vercel deployment fails:**
- Check build logs in Vercel dashboard
- Common issues:
  - Missing environment variables
  - TypeScript errors (check `npm run build` locally)
  - Import errors
- Fix locally and redeploy

**If backend connection fails in production:**
- Make sure backend is accessible publicly (not just localhost)
- Options:
  - Keep ngrok running during demo
  - Deploy backend to Railway/Render
  - Update NEXT_PUBLIC_BACKEND_URL in Vercel

**If images don't upload:**
- Check file size limits
- Verify base64 encoding works
- Test with different image formats
- Check browser console for errors

**If diff viewer is buggy:**
- Fall back to simple `<pre>` tag with monospace font
- Still functional, just less pretty

---

## Pro Tips

1. **Use browser dev tools** - React DevTools shows component state
2. **Test in incognito** - Clears cache, shows what judges see
3. **Mobile-first** - Many judges test on phones
4. **Keep it simple** - Working > fancy but broken
5. **Screenshots matter** - Judges often look at images first
6. **Have a backup plan** - If live demo fails, show video

---

## Your Unique Contribution

The **OCR screenshot upload** is your killer feature! No other team will have this. It shows real product thinking - users often see errors but don't know where they came from.

Make sure to:
- Demo this feature prominently
- Explain the DeepSeek OCR integration
- Show before/after (screenshot → auto-filled fields)
- Emphasize the UX improvement

This is what gets you points for innovation!

---

**You've got this! By hour 22 you'll have a production-ready frontend that looks amazing and showcases all of BugRewind's capabilities. This is the face of your project - make it shine! 🌟**

```

