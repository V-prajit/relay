# Relay (PM Copilot)

Relay turns a Slack message describing a feature or bug into a GitHub issue with impacted files and acceptance criteria, using a Postman Flow as the orchestration layer instead of a hand-rolled backend.

**Status**: Hackathon project (built October 25-29, 2025 for an MLH hackathon). Not actively maintained since; treat as a reference implementation rather than a running service.

![Relay / PM Copilot high-level diagram](./architecture-diagram.jpg)

*Diagram from the original repo. It shows the marketing-level view (PM to Slack to Postman AI Agents to GitHub/Snowflake); the diagrams below in this README show the actual block-level wiring found in the code.*

---

## Problem

Turning a one-line feature request into a GitHub issue that an engineer can actually start on takes manual work: someone has to figure out which files are relevant, write acceptance criteria, and decide if it's a new feature or a change to existing code. That triage happens over Slack threads and meetings before any code gets written.

## What it does

A `/relay <description>` Slack command:

1. Gets acknowledged within Slack's 3-second webhook timeout.
2. Triggers a Postman Flow that searches the target repo with ripgrep to find files related to the request.
3. Sends the request text and search results to an LLM step (Postman's AI Agent block, or a Snowflake Cortex-backed backend endpoint, depending on which flow variant is deployed - see [Known limitations](#known-limitations)) to draft a title, description, and acceptance criteria.
4. Posts the result back to Slack, and (per the reusable `create-github-pr-module.json` Flow Module) can create the corresponding GitHub issue/PR.
5. Optionally logs the run to a small analytics service that feeds a Next.js dashboard.

## Status line detail

Built by a 3-person team in roughly 5 days. Git history stops October 29, 2025 (`final upload`), and the DigitalOcean deployment referenced in the docs no longer responds (verified while writing this README - see Known limitations). Read this as a snapshot of a hackathon build, not a maintained product.

---

## Architecture

```mermaid
flowchart LR
    PM["PM / requester"] -->|"/relay <text>"| SlackApp["Slack workspace"]

    SlackApp -->|"slash command webhook"| Action["Postman Action\n(deployed Flow - see note below on\nARCHITECTURE.md's documented design\nvs. the exported flow JSON)"]
    SlackApp -.->|"Socket Mode, local-dev alternative"| Listener["slack-listener\n(Node, @slack/bolt, no public URL needed)"]

    Action -->|"immediate ack message\n(response_url, within 3s)"| SlackApp
    Action -->|"background module"| Ripgrep["Ripgrep API\n(Node/Express wrapping the ripgrep CLI)"]
    Listener --> Ripgrep

    Ripgrep -->|"matched files / is_new_feature"| Action
    Action -->|"generate issue/PR content"| Gen["AI Agent block (Postman)\nor FastAPI backend -> Snowflake Cortex"]
    Gen --> Action
    Action -.->|"create issue/PR (Flow Module exists;\nwiring in the exported flow is unconfirmed)"| GitHub["GitHub REST API"]
    GitHub -.-> Action
    Action -->|"notification"| SlackApp
    Action -->|"flow-complete webhook"| DashAPI["dashboard-api\n(Express, JSON-file store)"]

    DashAPI --> Frontend["Next.js analytics dashboard\n(conflict graph, PR timeline, risk meter)"]

    Backend["FastAPI backend (optional)\nSnowflake Cortex, GitHub PR creation, ripgrep proxy"] -.->|tunneled via ngrok in local flow variant| Action
    Backend --> GitHub

    CI["GitHub Actions\nNewman health-check, every 30 min"] -.->|"probes"| Action
```

**Read this diagram carefully around the GitHub step** - see [Known limitations](#known-limitations) for why it's drawn as uncertain rather than a solid arrow.

**A note on Evaluate/Validate/Fork:** `ARCHITECTURE.md` documents the Flow's design as `Request -> Evaluate -> Validate -> Fork`, with the Fork branch returning `202 Accepted` immediately. The committed `postman/flows/relay-command-flow.json` is a simpler linear variant - six blocks (`Webhook Start -> Acknowledge Slack -> RIPGREP API -> Snowflake Cortex -> Send Slack Notification -> Final Response`) with no `Evaluate`, `Validate`, or `Fork` block, and no `202` response anywhere in it. Its "immediate ack" is the `Acknowledge Slack` block, which POSTs a `"Processing..."` message to `{{start.response_url}}` before the rest of the chain runs; the flow's own HTTP response (`Final Response`) is a `200` that depends on the whole chain completing, not a forked early return. Treat the Evaluate/Validate/Fork/202 design below as the documented architecture, not something verified against this exported flow.

### Runtime flow (as implemented in `postman/flows/relay-command-flow.json`)

```mermaid
sequenceDiagram
    participant U as PM (Slack user)
    participant S as Slack
    participant F as Postman Flow
    participant R as Ripgrep API
    participant B as Backend (Snowflake Cortex)
    participant D as dashboard-api

    U->>S: /relay "fix mobile login"
    S->>F: POST form-encoded webhook
    F->>S: Acknowledge Slack ("Processing...", must be <3s)
    F->>B: POST /api/ripgrep/search { query: text } (backend proxy)
    B->>R: proxied ripgrep search
    R-->>B: { files: [...], is_new_feature }
    B-->>F: { files: [...], is_new_feature }
    F->>B: POST /api/snowflake/generate-pr { feature_request, impacted_files }
    B-->>F: { pr_title, pr_description, branch_name }
    F->>S: Block Kit message (title, files impacted, branch, description)
    F->>F: Final Response (200, depends on the full chain)
    F->>D: POST /api/webhook/flow-complete (execution record)
```

This sequence is drawn straight from the six blocks in `postman/flows/relay-command-flow.json` (no `Evaluate`/`Validate`/`Fork` - see the note above the previous diagram). Two things worth flagging, both confirmed by reading that flow JSON rather than `ARCHITECTURE.md`:

- `ripgrep_search` in the flow calls `{{BACKEND_API_URL}}/api/ripgrep/search`, i.e. it goes through the FastAPI backend's proxy route (`backend/app/routes/ripgrep_proxy.py`), not directly to the Ripgrep API. The proxy exists specifically because ngrok in local development can only tunnel one port.
- The flow's Slack notification links to the repo generally (a "View Repo" button), not to a specific issue/PR URL - consistent with this flow variant not calling GitHub directly.

---

## Key technical decisions

- **Immediate acknowledgment for Slack's 3-second timeout.** In the exported flow, `Acknowledge Slack` POSTs a `"Processing..."` message to `response_url` before the search/generate/notify chain runs, so Slack sees a response well inside its 3-second window while the rest of the work continues. `ARCHITECTURE.md` documents a more general Fork pattern (a `202 Accepted` branch returned in parallel with up to 60 minutes of background execution) as the intended design; the committed flow JSON implements the ack-then-chain version of that idea rather than a literal Fork block, so treat the Fork/`202` framing as documented design, not verified flow behavior.
- **An `Evaluate` block flattens Slack's payload (documented design).** `ARCHITECTURE.md` describes `application/x-www-form-urlencoded` from Slack wrapping every field in a single-element array (`{"text": ["hello"]}`) and a TypeScript `Evaluate` step normalizing this before validation. This block isn't present in the exported `relay-command-flow.json`, so it's documented in `ARCHITECTURE.md` rather than confirmed in the committed flow.
- **Two independent entry points.** A deployed Postman Action (public webhook, for the "production" path) and a `slack-listener` Socket Mode app (`@slack/bolt`, no public URL required) exist side by side - useful during development when you don't want to stand up a tunnel.
- **Code search first, generation second.** Ripgrep runs before the LLM step so the generation prompt is grounded in files that actually exist in the target repo, and `is_new_feature` short-circuits the "which files" question when ripgrep finds nothing.
- **Execution analytics live outside the Flow.** `dashboard-api` is a small Express service that appends flow-completion webhooks to a JSON file (explicitly an MVP choice - the `.env.example` says "can easily switch to PostgreSQL/MongoDB later") and serves aggregate stats/conflict data to a Next.js dashboard.
- **A CI health-check, not a test suite.** `.github/workflows/pm-copilot-monitor.yml` runs a Newman (Postman CLI) collection against the deployed Action every 30 minutes and on push/PR, and opens a GitHub issue if it fails. This checks that the deployed system responds, not the flow's internal logic.

---

## Repository layout

```
relay/
├── postman/
│   ├── flows/relay-command-flow.json   # exported Flow definition
│   ├── modules/                        # 6 reusable Flow Modules (ripgrep, GitHub PR, Slack, etc.)
│   ├── collections/                    # Postman collections, incl. the CI health-check
│   └── environments/
├── ripgrep-api/          # Node/Express wrapper around the ripgrep CLI
├── slack-listener/       # Socket Mode Slack app (local-dev alternative to the Postman Action)
├── dashboard-api/        # Express service: stores flow-execution webhooks, serves analytics
├── frontend/             # Next.js analytics dashboard (conflict graph, PR timeline, risk meter)
├── backend/              # FastAPI service: Snowflake Cortex, GitHub PR creation, ripgrep proxy
├── snowflake/            # SQL setup scripts for the optional Snowflake Cortex integration
├── .github/workflows/    # Newman-based health-check / performance-test CI
├── README.md
├── ARCHITECTURE.md       # deeper technical write-up of the Flow's block structure
└── ROADMAP.md            # unimplemented ideas (Elasticsearch search, conflict detection, etc.)
```

`SETUP.md` and `ROADMAP.md` exist and are current. A few files referenced elsewhere in the docs - `DEPLOYMENT.md`, `CLAUDE.md`, `SNOWFLAKE_MLH.md`, `postman/AI-AGENT-CONFIGURATION.md`, and everything under `docs/` except `docs/WORKSPACE_URL.txt` - are `.gitignore`d (see the `/docs` rule) and are not actually in this repository despite being linked. See [Known limitations](#known-limitations).

---

## Setup

Each service has its own `.env.example`. Copy and fill in placeholders - do not reuse any values that were ever printed to a terminal or committed.

**Ripgrep API** (`ripgrep-api/.env`):
```bash
PORT=3001
ALLOWED_ORIGINS=*
REPO_CLONE_URL=https://github.com/<owner>/<repo>.git
REPO_CLONE_DIR=/tmp/ripgrep-repo-cache
GITHUB_TOKEN=ghp_your_token_here   # only needed for private repos
```

**FastAPI backend** (`backend/.env`, optional - only needed for the Snowflake Cortex generation path):
```bash
PORT=8000
GITHUB_TOKEN=your_github_token_here
SNOWFLAKE_ACCOUNT=your_account_identifier.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
ENABLE_SNOWFLAKE=true
```

**dashboard-api** (`dashboard-api/.env`, optional - only needed for the analytics dashboard):
```bash
PORT=3002
ALLOWED_ORIGINS=http://localhost:3000
DATA_STORE_PATH=./data/executions.json
```

**slack-listener** (`slack-listener/.env`, optional - local-dev alternative to a deployed Postman Action):
```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
RIPGREP_API_URL=http://localhost:3001
BACKEND_API_URL=http://localhost:8000
```

**Prerequisites**: Postman Desktop (to build/deploy the Flow as an Action), Node.js 18+, a GitHub personal access token with `repo` scope, and a Slack workspace where you can install an app.

### Run locally

```bash
git clone https://github.com/V-prajit/relay.git
cd relay

cd ripgrep-api && npm install && cp .env.example .env && npm run dev   # :3001
cd ../dashboard-api && npm install && cp .env.example .env && npm run dev  # :3002 (optional)
cd ../frontend && npm install && npm run dev                               # :3000 (optional)
cd ../backend && pip install -r requirements.txt && python run.py          # :8000 (optional)
```

`start-all.sh` / `stop-all.sh` at the repo root will start/stop the backend, ripgrep API, and dashboard together on ports 8000/3001/3002.

Health check:
```bash
curl http://localhost:3001/api/health
```

---

## Usage

Direct search test (no Slack/Postman required):
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ProfileCard", "type": "tsx"}'
```

Once a Postman Action is deployed and a Slack slash command points at its URL:
```
/relay add dark mode toggle to settings
```

Expected: an in-channel Slack acknowledgment within 3 seconds, followed by a result message with the generated title, impacted files, and branch name once the background flow completes.

---

## Testing

There is no automated unit-test suite for the Flow logic itself (Flow logic lives in Postman's visual builder, not in this repo as testable code). What exists:

- `backend/test_structure.py` - AST-based structural checks (do expected classes/functions exist) rather than behavioral tests.
- `backend/test_phase1.py`, `test_snowflake_integration.py`, `test_snowflake_quick.py`, `test_github_pr.sh` - manual/ad hoc scripts for exercising individual endpoints during development.
- `test-dashboard.sh` - a smoke-test script that curls the dashboard endpoints.
- `.github/workflows/pm-copilot-monitor.yml` - runs a Postman/Newman collection (`postman/collections/pm-copilot-health-check.json`) against the deployed Action every 30 minutes, on push, and on PR; opens a GitHub issue on scheduled failures and posts a PR comment with pass/fail counts.

Run the CI collection locally with Newman if you have a deployed Action URL:
```bash
newman run postman/collections/pm-copilot-health-check.json \
  --environment postman/environments/dev-simple.json
```

---

## Deployment

As documented, the intended production shape is: Ripgrep API on DigitalOcean App Platform, the Flow deployed as a Postman Action (Postman-hosted), and a Slack app pointed at the Action's URL. `backend/`, `frontend/`, and `dashboard-api/` are optional additions layered on top for the Snowflake Cortex generation path and the analytics dashboard.

The DigitalOcean URL referenced in `ARCHITECTURE.md` (`pm-copilot-ripgrep-api.ondigitalocean.app`) did not respond when checked while writing this README - treat it as decommissioned, not as a live demo.

---

## Known limitations

- **The GitHub issue/PR creation step is unconfirmed in the exported flow.** `postman/modules/create-github-pr-module.json` implements it as a reusable Flow Module, but the committed `postman/flows/relay-command-flow.json` calls Snowflake Cortex for content generation and Slack for notification without a visible GitHub-creation step wired in between. Since Postman Flows are normally built and iterated on inside Postman Desktop, this exported JSON may simply be a snapshot that predates or postdates the wiring shown in the docs. Needs owner confirmation.
- **Referenced documentation files are missing from the repo.** `DEPLOYMENT.md`, `CLAUDE.md`, `SNOWFLAKE_MLH.md`, `postman/AI-AGENT-CONFIGURATION.md`, and most of `docs/` are linked from the docs but excluded by `.gitignore` (`/docs` rule), so they're not actually retrievable from this repository.
- **No LICENSE file.** The previous README stated "MIT License - see LICENSE file for details," but no LICENSE file exists in the repository and GitHub reports no detected license. If MIT is intended, add the file; until then, the repository is "all rights reserved" by default.
- **The live demo is down.** The DigitalOcean-hosted Ripgrep API is unreachable, and the Postman public workspace URL in `docs/WORKSPACE_URL.txt` was never filled in past its placeholder.
- **A `.env` file was committed to git history early on** (later addressed by a `.gitignore` update in `6397cce`), and both `.env` and `ripgrep-api/.env` remain tracked in the current working tree. Any credentials that were ever in those files should be treated as compromised and rotated; git history should be scrubbed if this repo is made more visible.
- **`dashboard-api` stores execution data in a single JSON file** with no locking - fine for a hackathon demo, not for concurrent writes.
- **Ripgrep API runs as a single instance** with no load balancing (README/ARCHITECTURE describe auto-scaling as a DigitalOcean App Platform feature, not something implemented in the app itself).
- **No retry logic** on any of the HTTP calls between Flow blocks; a failed downstream call surfaces as a Slack error message rather than being retried.
- **Leftover naming from earlier project iterations.** The backend's FastAPI app is titled `BugRewind API` internally, and a few `.env.example`/doc-comment defaults reference other project names (`postman-api-toolkit`, `youareabsolutelyright`) instead of `relay`. Cosmetic, but worth a cleanup pass.

---

## Contribution and attribution

Built by a 3-person team in a hackathon setting, with roles split roughly as described in `PM_COPILOT_TEAM_TASKS.txt` (Architect / Builder / Ops).

**Prajit Viswanadha** ([LinkedIn](https://www.linkedin.com/in/prajit-viswanadha/)) - the "Architect" role: the Postman Flow's conflict-detection/routing logic, the Ripgrep API service end to end, the `dashboard-api` service and Next.js analytics dashboard end to end, and the majority of the FastAPI backend and Postman module work. By commit count this is roughly 64% of the repo's history (41 of 64 commits) and 100% of `ripgrep-api/`, `dashboard-api/`, and `frontend/components/`.

**Shashank Yaji** ([LinkedIn](https://www.linkedin.com/in/shashankyaji/)) - the "Builder" role: reusable Flow Modules and documentation cleanup; roughly 30% of commits (19 of 64), concentrated in `postman/` and root-level docs.

**Rabib Husain** ([LinkedIn](https://www.linkedin.com/in/rabib-husain/)) - the "Ops" role: Snowflake integration and deployment-related work; roughly 6% of commits (4 of 64), concentrated in `backend/` and `postman/`.

No award or placement is documented in the repository (no Devpost link, no "winner" claim in any tracked file), so none is claimed here.

---

## Resources

- [Postman Flows documentation](https://learning.postman.com/docs/postman-flows/)
- [Postman AI Agent block](https://learning.postman.com/docs/postman-flows/reference/blocks/ai-agent/)
- [Slack slash commands](https://api.slack.com/interactivity/slash-commands)
- [GitHub REST API](https://docs.github.com/en/rest)
- [ripgrep](https://github.com/BurntSushi/ripgrep)

## License

No LICENSE file is present in this repository (see [Known limitations](#known-limitations)). The prior README's MIT claim is not currently backed by a license file.
