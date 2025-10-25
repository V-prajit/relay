# Frontend MCP Integration Plan: Best-in-Class PM Copilot UI

## Overview

Build a Next.js frontend with MCP (Model Context Protocol) integration that provides an intelligent, context-aware interface for the PM Copilot backend. This plan leverages cutting-edge MCP tools and patterns from 2025.

## Architecture: Agentless MCP Client

```
Next.js Frontend (React 19)
    ↓
MCP Client (CopilotKit/Custom)
    ↓
Backend MCP Server (stdio/SSE)
    ↓
Elasticsearch + FastAPI
```

**Key Concept**: The frontend acts as an MCP client that connects directly to our backend MCP server, enabling AI-powered features without managing agent state.

## Recommended MCP Tools Stack

### Core MCP Integration

1. **CopilotKit** (Primary Framework)
   - Built-in MCP support
   - React hooks for chat, suggestions, and actions
   - SSE (Server-Sent Events) streaming
   - Component-level AI integration

2. **Vercel AI SDK with MCP Adapter**
   - Alternative/complementary to CopilotKit
   - Native Next.js 15/16 support
   - Route handlers for `/api/completion`
   - Streaming text generation

3. **Custom MCP Client** (Fallback)
   - Direct stdio/SSE connection to backend
   - Full control over protocol
   - No external dependencies

### UI Component Libraries with MCP Support

1. **Chakra UI MCP Server**
   - AI-assisted component selection
   - Documentation integration
   - Theme generation

2. **Shadcn/UI** (Recommended)
   - Tailwind-based components
   - Copy-paste friendly
   - No MCP server needed (manual)

3. **v0 by Vercel**
   - AI-generated UI components
   - Direct integration with Next.js
   - Prompt-to-component workflow

### Development Tools

1. **Cursor IDE**
   - MCP-native code editor
   - Context-aware suggestions
   - Can connect to our backend MCP server

2. **GitHub Copilot + MCP Extensions**
   - VS Code integration
   - MCP tool awareness

## Frontend Features & MCP Tools Mapping

### Feature 1: Intelligent Search Interface

**UI Components:**
- Search bar with autocomplete
- Hybrid search results (BM25 + kNN + ELSER)
- Commit cards with relevance scores
- File change diff viewer

**MCP Tools Used:**
- `impact.search` - Hybrid retrieval
- `copilotkit.useCoAgent` - Streaming search suggestions
- Real-time query refinement

**Implementation:**
```tsx
import { CopilotKit } from "@copilotkit/react-core";
import { useCopilotAction } from "@copilotkit/react-core";

function SearchInterface() {
  const { executeAction } = useCopilotAction({
    name: "impact.search",
    description: "Search commits using hybrid retrieval",
    parameters: [
      { name: "query", type: "string" },
      { name: "repo_id", type: "string" }
    ],
    handler: async ({ query, repo_id }) => {
      // Calls backend MCP server
      const results = await fetch('/api/mcp/search', {
        method: 'POST',
        body: JSON.stringify({ query, repo_id })
      });
      return results.json();
    }
  });

  return (
    <CopilotTextarea
      placeholder="Describe the bug or feature..."
      onSubmit={(query) => executeAction({ query })}
    />
  );
}
```

### Feature 2: Visual Co-Change Graph

**UI Components:**
- Interactive graph visualization (D3.js or React Flow)
- Node details on hover
- File path highlighting
- Significance score indicators

**MCP Tools Used:**
- `impact.graph` - Co-change network exploration
- `react-flow` - Graph rendering
- `copilotkit.useCoAgent` - Graph interpretation

**Implementation:**
```tsx
import ReactFlow from 'reactflow';
import { useCopilotReadable } from "@copilotkit/react-core";

function CoChangeGraph({ seedFiles }) {
  const [graphData, setGraphData] = useState(null);

  useCopilotReadable({
    description: "Current co-change graph visualization",
    value: graphData
  });

  useEffect(() => {
    // Call impact.graph via MCP
    fetchGraphData(seedFiles).then(setGraphData);
  }, [seedFiles]);

  return (
    <ReactFlow
      nodes={graphData?.vertices}
      edges={graphData?.connections}
    />
  );
}
```

### Feature 3: AI-Powered Impact Analysis Panel

**UI Components:**
- File ownership cards
- Risk score visualization
- Test coverage indicators
- Related files list with scores

**MCP Tools Used:**
- `impact.analyze` - File impact analysis
- `copilotkit.useCopilotChat` - Conversational Q&A about impact
- AI-generated explanations

**Implementation:**
```tsx
import { useCopilotChat } from "@copilotkit/react-ui";

function ImpactPanel({ filePath }) {
  const { messages, sendMessage } = useCopilotChat();

  // Auto-trigger impact analysis
  useEffect(() => {
    sendMessage(`Analyze impact for ${filePath}`);
  }, [filePath]);

  return (
    <div className="impact-panel">
      <ChatMessages messages={messages} />
      <ImpactVisualization data={latestImpact} />
    </div>
  );
}
```

### Feature 4: Smart PR Creation Wizard

**UI Components:**
- Multi-step form
- AI-suggested branch names
- Auto-generated PR descriptions
- Impact summary preview

**MCP Tools Used:**
- `copilotkit.useMakeCopilotDocumentReadable` - Context sharing
- Backend `/api/create-pr` endpoint
- AI prompt engineering for descriptions

**Implementation:**
```tsx
import { useMakeCopilotDocumentReadable } from "@copilotkit/react-core";

function PRWizard({ impactData, commits }) {
  useMakeCopilotDocumentReadable({
    id: "impact-context",
    description: "Impact analysis for PR creation",
    contents: JSON.stringify(impactData)
  });

  const generatePRDescription = async () => {
    // AI generates description using impact context
    const description = await copilot.generate({
      prompt: "Create a PR description based on impact analysis",
      context: ["impact-context"]
    });
    return description;
  };

  return <PRForm onSubmit={createPR} />;
}
```

## Implementation Phases

### Phase 1: MCP Client Setup (4-6 hours)

**Goal:** Connect Next.js frontend to backend MCP server

**Tasks:**
1. Install CopilotKit and Vercel AI SDK
   ```bash
   npm install @copilotkit/react-core @copilotkit/react-ui ai
   ```

2. Create MCP proxy route in Next.js
   ```ts
   // app/api/mcp/route.ts
   import { CopilotRuntime } from "@copilotkit/runtime";
   import { ServerSentEvents } from "@copilotkit/runtime";

   export async function POST(req: Request) {
     const runtime = new CopilotRuntime({
       mcpServers: [{
         name: "bugrewind",
         command: "python",
         args: ["../backend/mcp_server.py"]
       }]
     });

     return runtime.handle(req);
   }
   ```

3. Wrap app with CopilotKit provider
   ```tsx
   // app/layout.tsx
   import { CopilotKit } from "@copilotkit/react-core";

   export default function RootLayout({ children }) {
     return (
       <CopilotKit runtimeUrl="/api/mcp">
         {children}
       </CopilotKit>
     );
   }
   ```

4. Test connection with simple chat interface

**Deliverables:**
- Working MCP connection
- Simple chat UI
- Tool calls verified

### Phase 2: Search & Results UI (6-8 hours)

**Goal:** Build intelligent search interface with hybrid results

**Tasks:**
1. Create search bar component
   - Autocomplete with AI suggestions
   - Query refinement hints
   - Repository selector

2. Build results grid
   - Commit cards with scores
   - Relevance indicators (BM25/kNN/ELSER)
   - Aggregations sidebar (top files, authors)

3. Implement diff viewer
   - Syntax highlighting (react-syntax-highlighter)
   - Side-by-side/unified views
   - File tree navigation

4. Add filtering & sorting
   - Time range slider
   - Author filter
   - Score threshold

**Deliverables:**
- Full search interface
- Responsive design
- Real-time updates

### Phase 3: Graph Visualization (5-7 hours)

**Goal:** Interactive co-change network explorer

**Tasks:**
1. Integrate React Flow or D3.js
   - Node positioning (force-directed layout)
   - Edge weights (line thickness)
   - Color coding (significance scores)

2. Add interactivity
   - Click to expand nodes
   - Hover for details
   - Pan/zoom controls

3. Build file detail panel
   - Ownership info
   - Recent commits
   - Quick actions (view code, analyze impact)

4. AI-powered insights
   - "Why are these files related?"
   - Unexpected connections highlighting
   - Risk warnings

**Deliverables:**
- Graph visualization
- AI explanations
- Export to PNG/SVG

### Phase 4: Impact Analysis Dashboard (5-7 hours)

**Goal:** Comprehensive impact view for any file

**Tasks:**
1. Create impact dashboard layout
   - File header with metadata
   - Ownership cards (top-3 contributors)
   - Co-change matrix
   - Test dependencies list

2. Risk visualization
   - Churn chart (commit frequency)
   - Risk score gauge
   - Flake density (future)

3. AI chat sidebar
   - Ask questions about impact
   - Get explanations for scores
   - Suggest reviewers

4. Integration with search
   - Click file in search → impact panel
   - Back navigation
   - History breadcrumbs

**Deliverables:**
- Impact dashboard
- AI chat integration
- Risk metrics

### Phase 5: PR Creation Flow (4-6 hours)

**Goal:** AI-assisted PR generation with impact context

**Tasks:**
1. Build multi-step wizard
   - Step 1: File selection
   - Step 2: Patch input/generation
   - Step 3: Impact review
   - Step 4: PR details

2. AI-powered features
   - Auto-generate branch names
   - Suggest PR title/description
   - Include impact receipts
   - Tag reviewers (code owners)

3. GitHub integration
   - OAuth login
   - Repository picker
   - Branch selection
   - Live PR preview

4. Success flow
   - PR created confirmation
   - Link to GitHub
   - Slack notification (future)

**Deliverables:**
- PR wizard
- GitHub integration
- Impact receipts

### Phase 6: Polish & Advanced Features (6-8 hours)

**Goal:** Production-ready UI with delightful UX

**Tasks:**
1. Design system
   - Consistent theming (Tailwind)
   - Component library (Shadcn/UI)
   - Dark mode toggle
   - Responsive breakpoints

2. Performance optimization
   - React Server Components
   - Streaming SSR
   - Image optimization
   - Code splitting

3. Advanced MCP features
   - Multi-agent orchestration
   - Tool chaining (search → graph → impact)
   - Context persistence
   - Conversation history

4. Accessibility
   - ARIA labels
   - Keyboard navigation
   - Screen reader support
   - High contrast mode

**Deliverables:**
- Polished UI
- Fast performance
- Accessible

## MCP Sub-Agents Strategy

### Agent 1: Search Refiner

**Purpose:** Improve user queries for better results

**Implementation:**
```tsx
const searchRefinerAgent = {
  name: "search_refiner",
  description: "Refines user queries for hybrid search",
  tools: ["impact.search"],
  systemPrompt: `
    You help refine vague PM queries into precise search terms.
    Consider: file paths, author names, commit messages, time ranges.
  `
};
```

**Use Case:**
- User types: "login bug"
- Agent suggests: "authentication error in auth/login.py last 3 months"

### Agent 2: Impact Explainer

**Purpose:** Explain co-change relationships and risk scores

**Implementation:**
```tsx
const impactExplainerAgent = {
  name: "impact_explainer",
  description: "Explains why files are related",
  tools: ["impact.graph", "impact.analyze"],
  systemPrompt: `
    Explain co-change relationships in plain English.
    Focus on: why files change together, who owns them, risk factors.
  `
};
```

**Use Case:**
- User clicks on graph connection
- Agent explains: "login.py and session.py change together because both handle user authentication state. Jane owns both files."

### Agent 3: PR Reviewer

**Purpose:** Review impact before creating PR

**Implementation:**
```tsx
const prReviewerAgent = {
  name: "pr_reviewer",
  description: "Reviews PR impact and suggests improvements",
  tools: ["impact.analyze"],
  systemPrompt: `
    Review PR impact set and warn about risks.
    Check: test coverage, code ownership, recent churn.
  `
};
```

**Use Case:**
- User creates PR
- Agent warns: "This file has 5 commits in last week (high churn). Consider adding Jane as reviewer (top contributor)."

## Additional MCP Tools to Build

### Tool 1: Code Ownership Lookup (Already exists)

```python
# backend/mcp_server.py (already implemented)
@server.call_tool()
async def owner_lookup(file_path: str, repo_id: str):
    """Get code ownership info for a file"""
    return files_indexer.get_impact_set(file_path, repo_id)
```

### Tool 2: Commit Timeline Generator (New)

**Purpose:** Generate timeline visualization data

```python
@server.call_tool()
async def commit_timeline(file_path: str, repo_id: str, days: int = 90):
    """Get commit timeline for a file"""
    # Query Elasticsearch for commits touching file
    # Return timeline data for visualization
    pass
```

**Frontend Usage:**
```tsx
<CommitTimeline
  filePath="auth/login.py"
  days={90}
  mcpTool="commit_timeline"
/>
```

### Tool 3: Test Coverage Analyzer (New)

**Purpose:** Infer test coverage from commit history

```python
@server.call_tool()
async def test_coverage(file_path: str, repo_id: str):
    """Analyze test coverage via co-change"""
    # Find test files that change with target file
    # Return coverage confidence score
    pass
```

### Tool 4: Reviewer Suggester (New)

**Purpose:** Suggest PR reviewers based on ownership + recency

```python
@server.call_tool()
async def suggest_reviewers(files: list[str], repo_id: str):
    """Suggest best reviewers for files"""
    # Combine ownership + recent activity
    # Return ranked list of reviewers
    pass
```

### Tool 5: Risk Scorer (New)

**Purpose:** Compute overall risk for a change

```python
@server.call_tool()
async def risk_score(files: list[str], repo_id: str):
    """Compute risk score for a change set"""
    # Factors: churn, ownership distribution, test coverage
    # Return 0-100 risk score
    pass
```

## Tech Stack Summary

### Frontend Core
- **Framework**: Next.js 16 (App Router, RSC)
- **React**: 19.2.0
- **TypeScript**: 5.x
- **Styling**: Tailwind CSS v4

### MCP Integration
- **Primary**: CopilotKit (React hooks, SSE streaming)
- **Alternative**: Vercel AI SDK with MCP Adapter
- **Backend**: Custom stdio MCP server (already built)

### UI Components
- **Base**: Shadcn/UI (Radix primitives + Tailwind)
- **Graph**: React Flow or D3.js
- **Diff**: react-diff-view or Monaco Editor
- **Charts**: Recharts or Tremor

### State Management
- **Global**: Zustand or Jotai (lightweight)
- **Server**: React Server Components + Server Actions
- **MCP State**: CopilotKit context API

## Success Metrics

- **MCP Tool Latency**: <500ms per tool call
- **UI Responsiveness**: 60fps interactions
- **Search Results**: <2s for hybrid search
- **Graph Rendering**: <1s for 100 nodes
- **Lighthouse Score**: 95+ across all metrics
- **Accessibility**: WCAG 2.1 AA compliant

## Next Steps

1. **Choose MCP Client Library**: CopilotKit (recommended) vs custom
2. **Setup Next.js Project**: Initialize with MCP proxy route
3. **Implement Phase 1**: Test MCP connection with simple chat
4. **Design System**: Choose Shadcn/UI components
5. **Build Search UI**: Implement Phase 2
6. **Iterate**: Add graph, impact, PR features

## Resources

- **CopilotKit Docs**: https://docs.copilotkit.ai/
- **Vercel AI SDK**: https://sdk.vercel.ai/docs
- **MCP Specification**: https://modelcontextprotocol.io/
- **React Flow**: https://reactflow.dev/
- **Shadcn/UI**: https://ui.shadcn.com/

## Example MCP-Powered UX

### Scenario: PM wants to add ProfileCard to /users route

1. **User types**: "Add ProfileCard component to /users page"

2. **Search Refiner Agent activates**:
   - Query: "ProfileCard /users route component added"
   - Filters: commits touching `pages/users` or `app/users`

3. **Results shown**:
   - 3 commits about user profile features
   - Aggregation: `/app/users/page.tsx` changed 5 times

4. **User clicks graph icon**:
   - Impact Explainer Agent shows co-change network
   - Highlights: `components/ProfileCard.tsx`, `app/users/page.tsx`, `lib/api/users.ts`

5. **User clicks "Create PR"**:
   - PR Reviewer Agent warns: "High churn on users/page.tsx (8 commits last month)"
   - Suggests reviewers: Jane (owner), Bob (recent contributor)
   - Auto-generates description with impact receipts

6. **PR created**:
   - Link to GitHub
   - Impact summary in description
   - Reviewers tagged
   - Tests listed

**Result**: PM goes from vague idea to actionable PR in <2 minutes, with full audit trail.
