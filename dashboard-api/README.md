# PM Copilot Dashboard API

Backend API for the PM Copilot Dashboard. Receives flow execution data from Postman Flows and provides analytics endpoints for visualization.

## Features

- ✅ **Webhook endpoint** to receive Postman Flow execution data
- ✅ **Analytics API** for querying execution history and statistics
- ✅ **Conflict analysis** endpoints for visualizing PR conflicts
- ✅ **Timeline data** for charts and graphs
- ✅ **Hotspot detection** for files with frequent conflicts
- ✅ **Simple JSON file storage** (easily upgradeable to PostgreSQL/MongoDB)

---

## Quick Start

###  1: Install Dependencies

```bash
cd dashboard-api
npm install
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (optional - defaults work)
```

### Step 3: Run the Server

```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start
```

Server runs on **http://localhost:3002** by default.

---

## API Endpoints

### Health Check

```
GET /health
```

Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T14:30:00Z",
  "uptime": 123.456,
  "environment": "development"
}
```

---

### Webhooks

#### Receive Flow Execution Data

```
POST /api/webhook/flow-complete
```

**Body** (sent from Postman Flow Output block):
```json
{
  "success": true,
  "feature_name": "profile-card",
  "pr_url": "https://github.com/owner/repo/pull/43",
  "pr_number": 43,
  "impacted_files": ["src/components/ProfileCard.tsx"],
  "conflict_detected": false,
  "conflict_score": 0,
  "conflicting_prs": [],
  "reasoning_trace": ["Parsed intent", "Searched codebase", "Generated PR"],
  "acceptance_criteria": ["ProfileCard displays avatar", "Tests pass"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Execution data stored successfully",
  "execution_id": "uuid-here",
  "stored_at": "2025-10-25T14:30:00Z"
}
```

---

### Analytics

#### List Executions

```
GET /api/analytics/executions?limit=50&offset=0&conflict_only=false
```

**Query Parameters:**
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset (default: 0)
- `conflict_only`: Filter only conflicts (true/false)
- `success_only`: Filter only successful (true/false)
- `start_date`: Start date filter (ISO string)
- `end_date`: End date filter (ISO string)

**Response:**
```json
{
  "success": true,
  "total": 100,
  "limit": 50,
  "offset": 0,
  "count": 50,
  "executions": [
    {
      "id": "uuid",
      "timestamp": "2025-10-25T14:30:00Z",
      "feature_name": "profile-card",
      "pr_number": 43,
      "pr_url": "...",
      "conflict_detected": false,
      "conflict_score": 0,
      "reasoning_trace": [...],
      ...
    }
  ]
}
```

#### Get Single Execution

```
GET /api/analytics/executions/:id
```

Returns detailed information about a specific execution.

#### Get Statistics

```
GET /api/analytics/stats
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2025-10-25T14:30:00Z",
  "summary": {
    "total_executions": 100,
    "successful_executions": 95,
    "failed_executions": 5,
    "success_rate": "95.0%"
  },
  "conflicts": {
    "total_with_conflicts": 12,
    "total_without_conflicts": 88,
    "conflict_rate": "12.0%",
    "risk_distribution": {
      "high_risk": 2,
      "medium_risk": 5,
      "low_risk": 5
    },
    "avg_conflict_score": "23.45"
  },
  "features": {
    "new_features_created": 30,
    "existing_features_modified": 70,
    "avg_files_impacted": "2.3",
    "top_features": [
      {"feature": "dark-mode", "count": 5},
      {"feature": "profile-card", "count": 4}
    ]
  },
  "activity": {
    "executions_last_24h": 15,
    "most_recent": "2025-10-25T14:30:00Z"
  }
}
```

#### Get Timeline Data

```
GET /api/analytics/timeline?days=7&interval=day
```

**Query Parameters:**
- `days`: Number of days (default: 7)
- `interval`: Grouping (hour/day, default: day)

**Response:**
```json
{
  "success": true,
  "days": 7,
  "interval": "day",
  "data_points": 7,
  "timeline": [
    {
      "timestamp": "2025-10-19",
      "total": 15,
      "successful": 14,
      "failed": 1,
      "with_conflicts": 3,
      "avg_conflict_score": 18.5
    }
  ]
}
```

---

### Conflicts

#### Get All Conflicts

```
GET /api/conflicts?min_score=0&limit=50
```

**Query Parameters:**
- `min_score`: Minimum conflict score (default: 0)
- `limit`: Number of results (default: 50)

**Response:**
```json
{
  "success": true,
  "total_conflicts": 12,
  "returned": 12,
  "conflicts": [
    {
      "id": "uuid",
      "timestamp": "2025-10-25T14:30:00Z",
      "feature_name": "dark-mode",
      "pr_number": 42,
      "pr_url": "...",
      "conflict_score": 45,
      "conflicting_prs": [
        {
          "pr_number": 40,
          "pr_title": "Update theme",
          "overlapping_files": ["src/styles/theme.ts"]
        }
      ],
      "impacted_files": ["src/components/Settings.tsx", "src/styles/theme.ts"]
    }
  ]
}
```

#### Get Conflict Graph

```
GET /api/conflicts/graph
```

Returns graph data for visualization (nodes = files, edges = conflicts).

**Response:**
```json
{
  "success": true,
  "graph": {
    "nodes": [
      {
        "id": "src/components/Settings.tsx",
        "label": "Settings.tsx",
        "fullPath": "src/components/Settings.tsx",
        "type": "impacted",
        "conflicts": [...],
        "size": 8,
        "color": "#ff4444"
      }
    ],
    "edges": [
      {
        "source": "src/components/Settings.tsx",
        "target": "dark-mode",
        "conflict_score": 45,
        "pr_number": 40,
        "pr_title": "Update theme"
      }
    ],
    "stats": {
      "total_nodes": 15,
      "total_edges": 8,
      "high_risk_nodes": 3
    }
  }
}
```

#### Get Conflict Hotspots

```
GET /api/conflicts/hotspots
```

Returns files most frequently involved in conflicts.

**Response:**
```json
{
  "success": true,
  "total_hotspots": 25,
  "returned": 20,
  "hotspots": [
    {
      "file": "src/components/Settings.tsx",
      "conflict_count": 5,
      "avg_conflict_score": "32.50",
      "max_conflict_score": 60,
      "recent_conflicts": [...]
    }
  ]
}
```

#### Get Risk Distribution

```
GET /api/conflicts/risk-distribution
```

Returns distribution of conflict scores across risk levels.

---

## Integrating with Postman Flow

### Step 1: Add HTTP Block to Output

In your Postman Flow, after the AI Agent generates the final output:

1. Add **HTTP Request** block
2. Connect it to AI Agent's success output
3. Configure:
   - **Method**: POST
   - **URL**: `http://localhost:3002/api/webhook/flow-complete`
   - **Headers**: `Content-Type: application/json`
   - **Body**: Pass the AI Agent's output directly

### Step 2: Test the Integration

Run your flow and check the Dashboard API logs:

```bash
npm run dev
```

You should see:
```
✅ Stored execution: profile-card (uuid-here)
```

### Step 3: View Data

Query the analytics endpoint:
```bash
curl http://localhost:3002/api/analytics/stats
```

---

## Data Storage

### JSON File Storage (Current)

Data is stored in `data/executions.json`:
- Simple and portable
- No database setup required
- Keeps last 1000 executions
- Perfect for demos and MVP

### Upgrading to Database (Future)

To scale, migrate to PostgreSQL or MongoDB:

1. **Install database driver**: `npm install pg` or `npm install mongodb`
2. **Update routes**: Replace file read/write with DB queries
3. **Set DATABASE_URL** in `.env`

Schema structure is already designed for easy migration.

---

## Development

### File Structure

```
dashboard-api/
├── src/
│   ├── index.js              # Main server
│   ├── routes/
│   │   ├── webhooks.js       # Webhook endpoints
│   │   ├── analytics.js      # Analytics endpoints
│   │   └── conflicts.js      # Conflict analysis endpoints
│   └── data/
│       └── executions.json   # Data store
├── package.json
├── .env.example
└── README.md
```

### Adding New Endpoints

1. Create route file in `src/routes/`
2. Import in `src/index.js`
3. Add to Express app: `app.use('/api/path', router)`

### Testing

```bash
# Test health endpoint
curl http://localhost:3002/health

# Test webhook
curl -X POST http://localhost:3002/api/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Get stats
curl http://localhost:3002/api/analytics/stats
```

---

## Deployment

### Deploy to DigitalOcean App Platform

1. **Create App**: Connect GitHub repo
2. **Configure**:
   - Build Command: `npm install`
   - Run Command: `npm start`
   - Port: 3002
3. **Set Environment Variables** in DigitalOcean dashboard
4. **Deploy**: DigitalOcean builds and runs automatically

### Deploy to Railway / Render / Fly.io

Similar process - all support Node.js apps out of the box.

---

## Troubleshooting

### Port Already in Use

Change `PORT` in `.env` to a different value (e.g., 3003).

### Data Not Saving

1. Check file permissions on `data/` directory
2. Verify `DATA_STORE_PATH` in `.env`
3. Check logs for error messages

### CORS Errors

Update `ALLOWED_ORIGINS` in `.env` to include your frontend URL:
```
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## Next Steps

- ✅ Start the API server: `npm run dev`
- ✅ Test webhook endpoint with Postman or curl
- ✅ Integrate with Postman Flow Output block
- ⏭️ Build frontend dashboard to visualize this data (see `../frontend/README.md`)
- ⏭️ Deploy to cloud platform

---

## License

MIT
