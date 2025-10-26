import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';

const router = express.Router();

// Get data file path
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const EXECUTIONS_FILE = join(__dirname, '../../data/executions.json');

/**
 * POST /api/webhook/flow-complete
 * Receive flow execution data from Postman Flow Output block
 *
 * Expected body from Postman Flow:
 * {
 *   "success": true,
 *   "feature_name": "profile-card",
 *   "pr_url": "https://github.com/...",
 *   "pr_number": 43,
 *   "impacted_files": ["src/components/ProfileCard.tsx"],
 *   "conflict_detected": false,
 *   "conflict_score": 0,
 *   "conflicting_prs": [],
 *   "reasoning_trace": ["Parsed intent", "Searched codebase", ...],
 *   "acceptance_criteria": [...]
 * }
 */
router.post('/flow-complete', async (req, res) => {
  try {
    const flowData = req.body;

    // Validate required fields
    if (!flowData.feature_name) {
      return res.status(400).json({
        error: 'Missing required field: feature_name'
      });
    }

    // Create execution record
    const execution = {
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      success: flowData.success !== false,
      feature_name: flowData.feature_name,
      pr_number: flowData.pr_number || null,
      pr_url: flowData.pr_url || null,
      impacted_files: flowData.impacted_files || [],
      total_files: flowData.total_files || flowData.impacted_files?.length || 0,
      is_new_feature: flowData.is_new_feature || false,

      // Conflict data
      conflict_detected: flowData.conflict_detected || false,
      conflict_score: flowData.conflict_score || 0,
      conflicting_prs: flowData.conflicting_prs || [],

      // AI reasoning
      reasoning_trace: flowData.reasoning_trace || [],
      acceptance_criteria: flowData.acceptance_criteria || [],

      // Metadata
      user_id: flowData.user_id || 'unknown',
      duration_ms: flowData.duration_ms || null,
      error_message: flowData.error || null
    };

    // Read existing executions
    const fileData = await fs.readFile(EXECUTIONS_FILE, 'utf-8');
    const executions = JSON.parse(fileData);

    // Add new execution at the beginning (most recent first)
    executions.unshift(execution);

    // Keep only last 1000 executions to prevent unbounded growth
    const trimmedExecutions = executions.slice(0, 1000);

    // Write back to file
    await fs.writeFile(
      EXECUTIONS_FILE,
      JSON.stringify(trimmedExecutions, null, 2)
    );

    console.log(`✅ Stored execution: ${execution.feature_name} (${execution.id})`);

    res.status(201).json({
      success: true,
      message: 'Execution data stored successfully',
      execution_id: execution.id,
      stored_at: execution.timestamp
    });

  } catch (error) {
    console.error('❌ Error storing execution data:', error);
    res.status(500).json({
      error: 'Failed to store execution data',
      details: error.message
    });
  }
});

/**
 * POST /api/webhook/test
 * Test endpoint to verify webhook is working
 */
router.post('/test', (req, res) => {
  console.log('📨 Test webhook received:', req.body);
  res.json({
    success: true,
    message: 'Webhook endpoint is working',
    received_data: req.body,
    timestamp: new Date().toISOString()
  });
});

export default router;
