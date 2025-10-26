import express from 'express';
import { search, getSupportedTypes } from '../services/ripgrep.js';

const router = express.Router();

/**
 * POST /search
 * Search codebase using ripgrep
 *
 * Request body:
 * {
 *   "query": "ProfileCard",
 *   "path": "src/",
 *   "type": "tsx",
 *   "case_sensitive": false
 * }
 *
 * Response:
 * {
 *   "success": true,
 *   "data": {
 *     "files": ["src/components/ProfileCard.tsx", ...],
 *     "matches": [{file, line, column, content, match_text}, ...],
 *     "total": 5
 *   }
 * }
 */
router.post('/search', async (req, res) => {
  try {
    const { query, path, type, case_sensitive } = req.body;

    // Validation
    if (!query || typeof query !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'Query parameter is required and must be a string',
      });
    }

    // Execute search
    const results = await search(query, {
      path: path || process.env.DEFAULT_SEARCH_PATH || './',
      type,
      case_sensitive: case_sensitive || false,
      max_results: parseInt(process.env.MAX_SEARCH_RESULTS || '50', 10),
    });

    // Determine if this is a new feature (no existing files)
    const isNewFeature = results.files.length === 0;

    res.json({
      success: true,
      data: {
        ...results,
        files: results.files,  // Keep as empty array if no files found
        is_new_feature: isNewFeature,
        message: isNewFeature
          ? 'No existing files found - may be a new feature. Claude should create new files and suggest a file structure.'
          : 'Found existing files that may be related to this feature.',
      },
      query: {
        pattern: query,
        path: path || './',
        type: type || 'all',
        case_sensitive: case_sensitive || false,
      },
    });
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * GET /types
 * Get list of supported file types
 *
 * Response:
 * {
 *   "success": true,
 *   "types": ["js", "ts", "tsx", "jsx", "py", ...]
 * }
 */
router.get('/types', async (req, res) => {
  try {
    const types = await getSupportedTypes();

    res.json({
      success: true,
      types,
    });
  } catch (error) {
    console.error('Failed to get types:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * GET /health
 * Health check endpoint
 */
router.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    timestamp: new Date().toISOString(),
  });
});

export default router;
