# MCP Workflow: Iterative Design-to-Code Development

## Overview

This document describes how to use the configured MCP servers for maximum productivity in frontend development with continuous visual feedback.

## Configured MCP Servers (7 Essential Tools)

### 1. **bugrewind-backend** (Your Backend)
- **Purpose**: Access impact analysis, hybrid search, co-change detection
- **80/20 Impact**: Core business logic, generates PR context
- **Usage**: Query commit history, get file ownership, analyze impact

### 2. **figma** (Design Source of Truth)
- **Purpose**: Semantic design access (not screenshots)
- **80/20 Impact**: Accurate component generation, design tokens
- **Usage**: Fetch frames, extract styles, get layout data

### 3. **peekaboo** (Visual Feedback Loop)
- **Purpose**: Screenshot + AI analysis for macOS
- **80/20 Impact**: Instant visual feedback on implementation vs design
- **Usage**: Capture UI, compare with Figma, get CSS improvement suggestions

### 4. **filesystem** (Code Access)
- **Purpose**: Read/write project files
- **80/20 Impact**: Direct code manipulation, config updates
- **Usage**: Edit React components, update Tailwind config, read types

### 5. **git** (Version Control)
- **Purpose**: Track changes, create commits
- **80/20 Impact**: Atomic commits, clean history
- **Usage**: Stage changes, commit with context, view diffs

### 6. **github** (Collaboration)
- **Purpose**: PRs, issues, repository management
- **80/20 Impact**: Automated PR creation with impact receipts
- **Usage**: Create PRs from impact analysis, link issues

### 7. **puppeteer** (Testing & Validation)
- **Purpose**: Browser automation, screenshot rendered pages
- **80/20 Impact**: Responsive testing, cross-browser validation
- **Usage**: Test breakpoints, capture states, validate accessibility

## Iterative Development Workflow

### Phase 1: Design Analysis
```
1. User provides Figma URL
   → MCP: figma.get_frame(url)
   → Extract: components, styles, layout

2. Analyze design tokens
   → Colors, spacing, typography
   → Map to Tailwind config

3. Identify components
   → Header, SearchBar, ResultCard, Graph, etc.
   → Plan component hierarchy
```

### Phase 2: Code Generation
```
1. Generate component skeleton
   → MCP: filesystem.write_file("frontend/app/components/SearchBar.tsx")
   → Use Figma data for props, structure

2. Apply styles
   → Convert Figma styles to Tailwind classes
   → Use semantic color tokens

3. Add interactivity
   → MCP: bugrewind-backend.impact.search
   → Wire up backend MCP tools
```

### Phase 3: Visual Validation
```
1. Run dev server
   → npm run dev

2. Capture screenshot
   → MCP: peekaboo.screenshot(window="localhost:3000")

3. Compare with Figma
   → AI analyzes differences
   → Suggests CSS improvements

4. Iterate
   → MCP: filesystem.edit_file(path, old_code, new_code)
   → Repeat screenshot → compare → improve
```

### Phase 4: Testing & Refinement
```
1. Responsive testing
   → MCP: puppeteer.screenshot(viewport="375x667") // iPhone
   → MCP: puppeteer.screenshot(viewport="1920x1080") // Desktop

2. Cross-browser validation
   → Test Chrome, Safari, Firefox
   → Check accessibility tree

3. Performance check
   → Lighthouse audit via puppeteer
   → Bundle size analysis
```

### Phase 5: Commit & PR
```
1. Stage changes
   → MCP: git.add(files)

2. Commit with context
   → MCP: git.commit("Add SearchBar component with hybrid search integration")

3. Create PR
   → MCP: github.create_pr(
       title: "Implement search interface",
       body: impact_analysis + screenshots
     )
```

## Example: Building Search Interface

### Step 1: Get Figma Design
```
@mcp figma.get_frame("https://figma.com/file/abc123/SearchInterface")

Response:
{
  "components": [
    {"name": "SearchBar", "type": "input", "width": 600, "height": 48},
    {"name": "FilterBar", "type": "group", ...},
    {"name": "ResultCard", "type": "card", ...}
  ],
  "styles": {
    "primary": "#2563eb",
    "background": "#ffffff",
    "border-radius": "8px"
  }
}
```

### Step 2: Generate Component
```
@mcp filesystem.write_file("frontend/app/components/SearchBar.tsx")

Content:
import { useCopilotAction } from "@copilotkit/react-core";

export function SearchBar() {
  const { executeAction } = useCopilotAction({
    name: "impact.search",
    // ... (from Figma data)
  });

  return (
    <div className="w-[600px] h-12 rounded-lg border border-gray-200">
      {/* Generated from Figma */}
    </div>
  );
}
```

### Step 3: Visual Validation
```
@mcp peekaboo.screenshot()

AI Analysis:
"The border radius is 6px but Figma specifies 8px.
The input height is 44px but should be 48px.
Suggested fix: Change h-11 to h-12 and rounded-md to rounded-lg"
```

### Step 4: Apply Fix
```
@mcp filesystem.edit_file(
  path: "frontend/app/components/SearchBar.tsx",
  old: "h-11 rounded-md",
  new: "h-12 rounded-lg"
)
```

### Step 5: Verify & Commit
```
@mcp peekaboo.screenshot()
AI: "Perfect match with Figma design ✓"

@mcp git.add(["frontend/app/components/SearchBar.tsx"])
@mcp git.commit("Add SearchBar component matching Figma design")
```

## Deterministic Development Pattern

### Rule 1: Always Start with Figma
- Never guess design specs
- Use `figma.get_frame()` to extract exact values
- Map Figma tokens to Tailwind config

### Rule 2: Validate After Every Change
- Screenshot → Compare → Fix
- Use `peekaboo` for instant feedback
- Iterate until pixel-perfect

### Rule 3: Test Responsively
- Use `puppeteer` for multiple viewports
- Validate mobile, tablet, desktop
- Check dark mode if applicable

### Rule 4: Commit Atomically
- One feature = One commit
- Include screenshots in PR
- Link to Figma frame

### Rule 5: Leverage Backend MCP Tools
- Use `bugrewind-backend` for data
- Wire up search, graph, impact tools
- Don't mock - use real backend

## MCP Tool Combinations

### Combo 1: Design → Code → Validate
```
figma.get_frame()
→ filesystem.write_file()
→ peekaboo.screenshot()
→ (iterate)
```

### Combo 2: Implement Feature → Test → PR
```
filesystem.edit_file()
→ puppeteer.screenshot(multiple viewports)
→ git.commit()
→ github.create_pr()
```

### Combo 3: Debug Visual Issue
```
peekaboo.screenshot(app window)
→ figma.get_frame(reference)
→ AI compares both
→ filesystem.edit_file(fix)
```

### Combo 4: Impact-Driven PR
```
bugrewind-backend.impact.analyze(files)
→ filesystem.edit_file(patch)
→ git.commit()
→ github.create_pr(with impact receipts)
```

## Best Practices

### 1. Use Figma as Single Source of Truth
- Don't eyeball designs
- Always query Figma MCP for exact values
- Update Tailwind config with design tokens

### 2. Screenshot Every Major Change
- Before/after comparisons
- Include in PR descriptions
- Use for visual regression testing

### 3. Keep MCP Context Readable
- Use `useMakeCopilotDocumentReadable()` for context
- Share Figma data across components
- Don't repeat queries

### 4. Automate Validation
- Create scripts using puppeteer MCP
- Run on every build
- Fail CI if screenshots don't match

### 5. Document with Visuals
- Commit messages with screenshot links
- PRs with Figma → Implementation comparisons
- Architecture diagrams via screenshots

## Environment Setup

### Required Environment Variables
```env
# GitHub (for PR creation)
GITHUB_TOKEN=ghp_xxxxx

# Backend (already configured)
ELASTIC_API_KEY=xxxxx
ELASTIC_ENDPOINT=https://xxxxx
```

### Optional (for future)
```env
BRAVE_API_KEY=xxxxx  # If adding web search MCP
```

## Troubleshooting

### Issue: Figma MCP returns error
**Solution**: Check Figma URL, ensure public access or auth token

### Issue: Peekaboo can't capture screenshot
**Solution**: macOS only - grant Screen Recording permission in System Settings

### Issue: Backend MCP server timeout
**Solution**: Check backend/mcp_server.py is running, verify Elasticsearch connection

### Issue: Filesystem MCP access denied
**Solution**: Verify paths in .mcp.json point to correct directories

## Next Steps

1. **Start dev server**: `cd frontend && npm run dev`
2. **Open Claude Desktop**: Load this project
3. **Test MCP tools**: Try `@mcp figma`, `@mcp peekaboo`, etc.
4. **Build first component**: Follow workflow above
5. **Iterate**: Screenshot → Compare → Fix → Commit

## Success Metrics

- **Design accuracy**: 100% match with Figma (pixel-perfect)
- **Development speed**: 2x faster with MCP tools
- **Visual regressions**: Zero (caught by screenshot validation)
- **PR quality**: Impact analysis + visual proof in every PR
- **Code consistency**: Design tokens enforced via Figma MCP
