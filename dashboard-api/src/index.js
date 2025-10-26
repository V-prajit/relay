import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';

// Load environment variables
dotenv.config();

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Import routes
import webhooksRouter from './routes/webhooks.js';
import analyticsRouter from './routes/analytics.js';
import conflictsRouter from './routes/conflicts.js';

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
  credentials: true
}));
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// Initialize data store
const DATA_DIR = join(__dirname, '../data');
const EXECUTIONS_FILE = join(DATA_DIR, 'executions.json');

// Ensure data directory and file exist
async function initializeDataStore() {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true });

    // Check if executions file exists
    try {
      await fs.access(EXECUTIONS_FILE);
    } catch {
      // File doesn't exist, create with empty array
      await fs.writeFile(EXECUTIONS_FILE, JSON.stringify([], null, 2));
      console.log('✅ Initialized executions data store');
    }
  } catch (error) {
    console.error('❌ Failed to initialize data store:', error);
    process.exit(1);
  }
}

// Routes
app.use('/api/webhook', webhooksRouter);
app.use('/api/analytics', analyticsRouter);
app.use('/api/conflicts', conflictsRouter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'PM Copilot Dashboard API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      webhook: '/api/webhook',
      analytics: '/api/analytics',
      conflicts: '/api/conflicts'
    },
    documentation: 'https://github.com/youareabsolutelyright'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Cannot ${req.method} ${req.path}`,
    available_endpoints: ['/health', '/api/webhook', '/api/analytics', '/api/conflicts']
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('❌ Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// Start server
async function startServer() {
  await initializeDataStore();

  app.listen(PORT, () => {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 PM Copilot Dashboard API');
    console.log('='.repeat(60));
    console.log(`📡 Server running on: http://localhost:${PORT}`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`💾 Data store: ${EXECUTIONS_FILE}`);
    console.log('='.repeat(60) + '\n');
    console.log('Available endpoints:');
    console.log(`  GET  /health                    - Health check`);
    console.log(`  POST /api/webhook/flow-complete - Receive flow execution data`);
    console.log(`  GET  /api/analytics/executions  - List all executions`);
    console.log(`  GET  /api/analytics/stats       - Get statistics`);
    console.log(`  GET  /api/conflicts             - Get conflict data`);
    console.log('\n' + '='.repeat(60) + '\n');
  });
}

// Handle shutdown gracefully
process.on('SIGTERM', () => {
  console.log('\n📴 SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\n📴 SIGINT received, shutting down gracefully...');
  process.exit(0);
});

// Start the server
startServer().catch(err => {
  console.error('❌ Failed to start server:', err);
  process.exit(1);
});

export default app;
