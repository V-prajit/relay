import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import searchRouter from './routes/search.js';

// Load environment variables
dotenv.config();

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

// Start server
app.listen(PORT, () => {
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
  → GET  /api/types    - Supported file types

Press Ctrl+C to stop the server
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\nSIGINT received, shutting down gracefully...');
  process.exit(0);
});
