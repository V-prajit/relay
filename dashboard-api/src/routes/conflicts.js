import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';

const router = express.Router();

// Get data file path
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const EXECUTIONS_FILE = join(__dirname, '../../data/executions.json');

/**
 * Helper function to read executions from file
 */
async function getExecutions() {
  try {
    const fileData = await fs.readFile(EXECUTIONS_FILE, 'utf-8');
    return JSON.parse(fileData);
  } catch (error) {
    console.error('Error reading executions:', error);
    return [];
  }
}

/**
 * GET /api/conflicts
 * Get all executions with conflicts
 *
 * Query params:
 * - min_score: Minimum conflict score to include (default: 0)
 * - limit: Number of results (default: 50)
 */
router.get('/', async (req, res) => {
  try {
    let executions = await getExecutions();

    // Filter to only conflicts
    executions = executions.filter(e => e.conflict_detected);

    // Apply minimum score filter
    const min_score = parseInt(req.query.min_score) || 0;
    if (min_score > 0) {
      executions = executions.filter(e => e.conflict_score >= min_score);
    }

    // Pagination
    const limit = parseInt(req.query.limit) || 50;
    const paginatedExecutions = executions.slice(0, limit);

    res.json({
      success: true,
      total_conflicts: executions.length,
      returned: paginatedExecutions.length,
      conflicts: paginatedExecutions.map(e => ({
        id: e.id,
        timestamp: e.timestamp,
        feature_name: e.feature_name,
        pr_number: e.pr_number,
        pr_url: e.pr_url,
        conflict_score: e.conflict_score,
        conflicting_prs: e.conflicting_prs,
        impacted_files: e.impacted_files
      }))
    });

  } catch (error) {
    console.error('Error fetching conflicts:', error);
    res.status(500).json({
      error: 'Failed to fetch conflicts',
      details: error.message
    });
  }
});

/**
 * GET /api/conflicts/graph
 * Get conflict graph data for visualization
 * Returns nodes (files) and edges (conflicts between PRs)
 */
router.get('/graph', async (req, res) => {
  try {
    const executions = await getExecutions();

    // Filter to executions with conflicts
    const conflictExecutions = executions.filter(e => e.conflict_detected);

    // Build graph structure
    const nodes = new Map(); // file -> node data
    const edges = []; // array of {source, target, conflict_score, prs}

    conflictExecutions.forEach(execution => {
      // Add impacted files as nodes
      execution.impacted_files?.forEach(file => {
        if (!nodes.has(file)) {
          nodes.set(file, {
            id: file,
            label: file.split('/').pop(), // Just filename
            fullPath: file,
            type: 'impacted',
            conflicts: []
          });
        }

        // Record conflict
        nodes.get(file).conflicts.push({
          execution_id: execution.id,
          feature: execution.feature_name,
          score: execution.conflict_score
        });
      });

      // Create edges for conflicting PRs
      execution.conflicting_prs?.forEach(conflictPr => {
        const overlappingFiles = conflictPr.overlapping_files || [];

        overlappingFiles.forEach(file => {
          edges.push({
            source: file,
            target: execution.feature_name,
            conflict_score: conflictPr.conflict_score || execution.conflict_score,
            pr_number: conflictPr.pr_number,
            pr_title: conflictPr.pr_title
          });
        });
      });
    });

    // Convert nodes map to array
    const nodesArray = Array.from(nodes.values());

    // Calculate node sizes based on conflict count
    nodesArray.forEach(node => {
      node.size = Math.max(5, node.conflicts.length * 2);
      node.color = node.conflicts.length > 3 ? '#ff4444' : '#4CAF50';
    });

    res.json({
      success: true,
      graph: {
        nodes: nodesArray,
        edges: edges,
        stats: {
          total_nodes: nodesArray.length,
          total_edges: edges.length,
          high_risk_nodes: nodesArray.filter(n => n.conflicts.length > 3).length
        }
      }
    });

  } catch (error) {
    console.error('Error generating conflict graph:', error);
    res.status(500).json({
      error: 'Failed to generate conflict graph',
      details: error.message
    });
  }
});

/**
 * GET /api/conflicts/hotspots
 * Get files that are most frequently involved in conflicts (conflict hotspots)
 */
router.get('/hotspots', async (req, res) => {
  try {
    const executions = await getExecutions();
    const conflictExecutions = executions.filter(e => e.conflict_detected);

    // Count conflicts per file
    const fileConflicts = {};

    conflictExecutions.forEach(execution => {
      execution.impacted_files?.forEach(file => {
        if (!fileConflicts[file]) {
          fileConflicts[file] = {
            file,
            count: 0,
            total_score: 0,
            max_score: 0,
            executions: []
          };
        }

        fileConflicts[file].count++;
        fileConflicts[file].total_score += execution.conflict_score || 0;
        fileConflicts[file].max_score = Math.max(
          fileConflicts[file].max_score,
          execution.conflict_score || 0
        );
        fileConflicts[file].executions.push({
          id: execution.id,
          feature: execution.feature_name,
          score: execution.conflict_score,
          timestamp: execution.timestamp
        });
      });
    });

    // Convert to array and calculate averages
    const hotspots = Object.values(fileConflicts).map(item => ({
      file: item.file,
      conflict_count: item.count,
      avg_conflict_score: (item.total_score / item.count).toFixed(2),
      max_conflict_score: item.max_score,
      recent_conflicts: item.executions.slice(0, 5) // Last 5 conflicts
    }));

    // Sort by conflict count
    hotspots.sort((a, b) => b.conflict_count - a.conflict_count);

    // Get top 20
    const top_hotspots = hotspots.slice(0, 20);

    res.json({
      success: true,
      total_hotspots: hotspots.length,
      returned: top_hotspots.length,
      hotspots: top_hotspots
    });

  } catch (error) {
    console.error('Error calculating hotspots:', error);
    res.status(500).json({
      error: 'Failed to calculate hotspots',
      details: error.message
    });
  }
});

/**
 * GET /api/conflicts/risk-distribution
 * Get distribution of conflict risk scores
 */
router.get('/risk-distribution', async (req, res) => {
  try {
    const executions = await getExecutions();
    const conflictExecutions = executions.filter(e => e.conflict_detected);

    // Define risk buckets
    const buckets = {
      '0-20': 0,
      '21-40': 0,
      '41-60': 0,
      '61-80': 0,
      '81-100': 0
    };

    conflictExecutions.forEach(e => {
      const score = e.conflict_score || 0;

      if (score <= 20) buckets['0-20']++;
      else if (score <= 40) buckets['21-40']++;
      else if (score <= 60) buckets['41-60']++;
      else if (score <= 80) buckets['61-80']++;
      else buckets['81-100']++;
    });

    // Convert to array format for charts
    const distribution = Object.entries(buckets).map(([range, count]) => ({
      range,
      count,
      percentage: conflictExecutions.length > 0
        ? ((count / conflictExecutions.length) * 100).toFixed(1)
        : '0'
    }));

    res.json({
      success: true,
      total_conflicts: conflictExecutions.length,
      distribution
    });

  } catch (error) {
    console.error('Error calculating risk distribution:', error);
    res.status(500).json({
      error: 'Failed to calculate risk distribution',
      details: error.message
    });
  }
});

export default router;
