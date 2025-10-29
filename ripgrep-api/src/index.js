import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import searchRouter from './routes/search.js';
import { ensureRepoCloned, pullLatestChanges } from './services/git.js';

// Get directory paths
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from ripgrep-api/.env
dotenv.config({ path: join(__dirname, '..', '.env') });

const app = express();
const PORT = process.env.PORT || 3001;
const ALLOWED_ORIGINS = process.env.ALLOWED_ORIGINS || '*';

// Middleware
app.use(express.json());

// CORS configuration
if (ALLOWED_ORIGINS === '*') {
  app.use(cors());
} else {
  app.use(cors({
    origin: ALLOWED_ORIGINS.split(',').map(o => o.trim()),
  }));
}

// Request logging middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api', searchRouter);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'Ripgrep API',
    version: '1.0.0',
    description: 'HTTP API wrapper for ripgrep code search',
    endpoints: {
      health: 'GET /api/health',
      search: 'POST /api/search',
      types: 'GET /api/types',
    },
    documentation: 'https://github.com/yourusername/youareabsolutelyright',
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    success: false,
    error: err.message || 'Internal server error',
  });
});

// Background sync interval (default: 5 minutes)
const REPO_PULL_INTERVAL = parseInt(process.env.REPO_PULL_INTERVAL || '300000', 10);
let syncIntervalId = null;

// Start server with repo cloning
async function startServer() {
  try {
    // Clone/update repository before starting server
    console.log('\n╔════════════════════════════════════════════╗');
    console.log('║     Initializing Repository Clone        ║');
    console.log('╚════════════════════════════════════════════╝\n');

    await ensureRepoCloned();

    // Start background sync if interval is set
    if (REPO_PULL_INTERVAL > 0) {
      console.log(`\n🔄 Starting background sync (every ${REPO_PULL_INTERVAL / 1000}s)`);
      syncIntervalId = setInterval(async () => {
        console.log('\n🔄 Background sync triggered...');
        await pullLatestChanges();
      }, REPO_PULL_INTERVAL);
    }

    // Start the server
    app.listen(PORT, '0.0.0.0', () => {
      console.log(`
╔════════════════════════════════════════════╗
║        Ripgrep API Server Running         ║
╠════════════════════════════════════════════╣
║  Port:        ${PORT.toString().padEnd(30)} ║
║  Environment: ${(process.env.NODE_ENV || 'development').padEnd(30)} ║
║  CORS:        ${ALLOWED_ORIGINS.padEnd(30)} ║
╚════════════════════════════════════════════╝

Available endpoints:
  → GET  /              - API information
  → GET  /api/health   - Health check
  → POST /api/search   - Code search
  → POST /api/sync     - Manual repo sync
  → GET  /api/types    - Supported file types

Press Ctrl+C to stop the server
      `);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error.message);
    process.exit(1);
  }
}

// Graceful shutdown
function shutdown() {
  console.log('\n📴 Shutting down gracefully...');

  // Clear background sync interval
  if (syncIntervalId) {
    clearInterval(syncIntervalId);
    console.log('✅ Stopped background sync');
  }

  process.exit(0);
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

// Start the server
startServer();
