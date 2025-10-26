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
 * GET /api/analytics/executions
 * Get list of all flow executions with optional filters
 *
 * Query params:
 * - limit: Number of results (default: 50)
 * - offset: Pagination offset (default: 0)
 * - conflict_only: Filter only executions with conflicts (true/false)
 * - success_only: Filter only successful executions (true/false)
 * - start_date: Filter by start date (ISO string)
 * - end_date: Filter by end date (ISO string)
 */
router.get('/executions', async (req, res) => {
  try {
    let executions = await getExecutions();

    // Apply filters
    const { conflict_only, success_only, start_date, end_date } = req.query;

    if (conflict_only === 'true') {
      executions = executions.filter(e => e.conflict_detected);
    }

    if (success_only === 'true') {
      executions = executions.filter(e => e.success);
    }

    if (start_date) {
      executions = executions.filter(e =>
        new Date(e.timestamp) >= new Date(start_date)
      );
    }

    if (end_date) {
      executions = executions.filter(e =>
        new Date(e.timestamp) <= new Date(end_date)
      );
    }

    // Pagination
    const limit = parseInt(req.query.limit) || 50;
    const offset = parseInt(req.query.offset) || 0;

    const total = executions.length;
    const paginatedExecutions = executions.slice(offset, offset + limit);

    res.json({
      success: true,
      total,
      limit,
      offset,
      count: paginatedExecutions.length,
      executions: paginatedExecutions
    });

  } catch (error) {
    console.error('Error fetching executions:', error);
    res.status(500).json({
      error: 'Failed to fetch executions',
      details: error.message
    });
  }
});

/**
 * GET /api/analytics/executions/:id
 * Get details of a specific execution
 */
router.get('/executions/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const executions = await getExecutions();

    const execution = executions.find(e => e.id === id);

    if (!execution) {
      return res.status(404).json({
        error: 'Execution not found',
        execution_id: id
      });
    }

    res.json({
      success: true,
      execution
    });

  } catch (error) {
    console.error('Error fetching execution:', error);
    res.status(500).json({
      error: 'Failed to fetch execution',
      details: error.message
    });
  }
});

/**
 * GET /api/analytics/stats
 * Get overall statistics about flow executions
 */
router.get('/stats', async (req, res) => {
  try {
    const executions = await getExecutions();

    // Calculate statistics
    const total_executions = executions.length;
    const successful_executions = executions.filter(e => e.success).length;
    const failed_executions = total_executions - successful_executions;

    const executions_with_conflicts = executions.filter(e => e.conflict_detected).length;
    const executions_without_conflicts = total_executions - executions_with_conflicts;

    const new_features_created = executions.filter(e => e.is_new_feature).length;
    const existing_features_modified = total_executions - new_features_created;

    // Conflict score distribution
    const high_risk = executions.filter(e => e.conflict_score >= 60).length;
    const medium_risk = executions.filter(e => e.conflict_score >= 30 && e.conflict_score < 60).length;
    const low_risk = executions.filter(e => e.conflict_score > 0 && e.conflict_score < 30).length;

    // Average values
    const avg_conflict_score = executions.length > 0
      ? executions.reduce((sum, e) => sum + (e.conflict_score || 0), 0) / executions.length
      : 0;

    const avg_files_impacted = executions.length > 0
      ? executions.reduce((sum, e) => sum + (e.total_files || 0), 0) / executions.length
      : 0;

    // Recent activity (last 24 hours)
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recent_executions = executions.filter(e =>
      new Date(e.timestamp) > yesterday
    ).length;

    // Most active features (top 5)
    const featureCounts = {};
    executions.forEach(e => {
      featureCounts[e.feature_name] = (featureCounts[e.feature_name] || 0) + 1;
    });

    const top_features = Object.entries(featureCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([feature, count]) => ({ feature, count }));

    res.json({
      success: true,
      timestamp: new Date().toISOString(),
      summary: {
        total_executions,
        successful_executions,
        failed_executions,
        success_rate: total_executions > 0
          ? ((successful_executions / total_executions) * 100).toFixed(1) + '%'
          : '0%'
      },
      conflicts: {
        total_with_conflicts: executions_with_conflicts,
        total_without_conflicts: executions_without_conflicts,
        conflict_rate: total_executions > 0
          ? ((executions_with_conflicts / total_executions) * 100).toFixed(1) + '%'
          : '0%',
        risk_distribution: {
          high_risk,
          medium_risk,
          low_risk
        },
        avg_conflict_score: avg_conflict_score.toFixed(2)
      },
      features: {
        new_features_created,
        existing_features_modified,
        avg_files_impacted: avg_files_impacted.toFixed(1),
        top_features
      },
      activity: {
        executions_last_24h: recent_executions,
        most_recent: executions[0]?.timestamp || null
      }
    });

  } catch (error) {
    console.error('Error calculating stats:', error);
    res.status(500).json({
      error: 'Failed to calculate statistics',
      details: error.message
    });
  }
});

/**
 * GET /api/analytics/timeline
 * Get execution timeline data (for charts)
 *
 * Query params:
 * - days: Number of days to include (default: 7)
 * - interval: Grouping interval (hour, day) (default: day)
 */
router.get('/timeline', async (req, res) => {
  try {
    const executions = await getExecutions();
    const days = parseInt(req.query.days) || 7;
    const interval = req.query.interval || 'day';

    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
    const recentExecutions = executions.filter(e =>
      new Date(e.timestamp) > cutoffDate
    );

    // Group by date
    const groupedData = {};

    recentExecutions.forEach(e => {
      const date = new Date(e.timestamp);
      let key;

      if (interval === 'hour') {
        key = date.toISOString().slice(0, 13) + ':00:00';
      } else {
        key = date.toISOString().slice(0, 10);
      }

      if (!groupedData[key]) {
        groupedData[key] = {
          timestamp: key,
          total: 0,
          successful: 0,
          failed: 0,
          with_conflicts: 0,
          avg_conflict_score: 0,
          conflict_scores: []
        };
      }

      groupedData[key].total++;
      if (e.success) groupedData[key].successful++;
      else groupedData[key].failed++;
      if (e.conflict_detected) groupedData[key].with_conflicts++;
      groupedData[key].conflict_scores.push(e.conflict_score || 0);
    });

    // Calculate averages
    const timeline = Object.values(groupedData).map(item => {
      const avgScore = item.conflict_scores.length > 0
        ? item.conflict_scores.reduce((a, b) => a + b, 0) / item.conflict_scores.length
        : 0;

      return {
        timestamp: item.timestamp,
        total: item.total,
        successful: item.successful,
        failed: item.failed,
        with_conflicts: item.with_conflicts,
        avg_conflict_score: parseFloat(avgScore.toFixed(2))
      };
    });

    // Sort by timestamp
    timeline.sort((a, b) => a.timestamp.localeCompare(b.timestamp));

    res.json({
      success: true,
      days,
      interval,
      data_points: timeline.length,
      timeline
    });

  } catch (error) {
    console.error('Error generating timeline:', error);
    res.status(500).json({
      error: 'Failed to generate timeline',
      details: error.message
    });
  }
});

export default router;
