/**
 * API Client for PM Copilot Dashboard
 * Fetches data from the Dashboard API backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3002';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

export interface Execution {
  id: string;
  timestamp: string;
  success: boolean;
  feature_name: string;
  pr_number: number | null;
  pr_url: string | null;
  impacted_files: string[];
  total_files: number;
  is_new_feature: boolean;
  conflict_detected: boolean;
  conflict_score: number;
  conflicting_prs: Array<{
    pr_number: number;
    pr_title: string;
    overlapping_files: string[];
    conflict_score?: number;
  }>;
  reasoning_trace: string[];
  acceptance_criteria: string[];
  user_id?: string;
  duration_ms?: number | null;
  error_message?: string | null;
}

export interface Stats {
  summary: {
    total_executions: number;
    successful_executions: number;
    failed_executions: number;
    success_rate: string;
  };
  conflicts: {
    total_with_conflicts: number;
    total_without_conflicts: number;
    conflict_rate: string;
    risk_distribution: {
      high_risk: number;
      medium_risk: number;
      low_risk: number;
    };
    avg_conflict_score: string;
  };
  features: {
    new_features_created: number;
    existing_features_modified: number;
    avg_files_impacted: string;
    top_features: Array<{ feature: string; count: number }>;
  };
  activity: {
    executions_last_24h: number;
    most_recent: string | null;
  };
}

export interface ConflictGraphData {
  nodes: Array<{
    id: string;
    label: string;
    fullPath: string;
    type: string;
    conflicts: Array<{
      execution_id: string;
      feature: string;
      score: number;
    }>;
    size: number;
    color: string;
  }>;
  edges: Array<{
    source: string;
    target: string;
    conflict_score: number;
    pr_number: number;
    pr_title: string;
  }>;
  stats: {
    total_nodes: number;
    total_edges: number;
    high_risk_nodes: number;
  };
}

export interface TimelineData {
  timestamp: string;
  total: number;
  successful: number;
  failed: number;
  with_conflicts: number;
  avg_conflict_score: number;
}

/**
 * Get list of executions
 */
export async function getExecutions(params?: {
  limit?: number;
  offset?: number;
  conflict_only?: boolean;
  success_only?: boolean;
}) {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.set('limit', params.limit.toString());
  if (params?.offset) queryParams.set('offset', params.offset.toString());
  if (params?.conflict_only) queryParams.set('conflict_only', 'true');
  if (params?.success_only) queryParams.set('success_only', 'true');

  const query = queryParams.toString();
  const endpoint = `/api/analytics/executions${query ? '?' + query : ''}`;

  return fetchAPI<{
    success: boolean;
    total: number;
    limit: number;
    offset: number;
    count: number;
    executions: Execution[];
  }>(endpoint);
}

/**
 * Get single execution by ID
 */
export async function getExecution(id: string) {
  return fetchAPI<{
    success: boolean;
    execution: Execution;
  }>(`/api/analytics/executions/${id}`);
}

/**
 * Get overall statistics
 */
export async function getStats() {
  return fetchAPI<{
    success: boolean;
    timestamp: string;
  } & Stats>('/api/analytics/stats');
}

/**
 * Get timeline data
 */
export async function getTimeline(params?: { days?: number; interval?: 'hour' | 'day' }) {
  const queryParams = new URLSearchParams();
  if (params?.days) queryParams.set('days', params.days.toString());
  if (params?.interval) queryParams.set('interval', params.interval);

  const query = queryParams.toString();
  const endpoint = `/api/analytics/timeline${query ? '?' + query : ''}`;

  return fetchAPI<{
    success: boolean;
    days: number;
    interval: string;
    data_points: number;
    timeline: TimelineData[];
  }>(endpoint);
}

/**
 * Get conflict graph data
 */
export async function getConflictGraph() {
  return fetchAPI<{
    success: boolean;
    graph: ConflictGraphData;
  }>('/api/conflicts/graph');
}

/**
 * Get conflict hotspots
 */
export async function getConflictHotspots() {
  return fetchAPI<{
    success: boolean;
    total_hotspots: number;
    returned: number;
    hotspots: Array<{
      file: string;
      conflict_count: number;
      avg_conflict_score: string;
      max_conflict_score: number;
      recent_conflicts: Array<{
        id: string;
        feature: string;
        score: number;
        timestamp: string;
      }>;
    }>;
  }>('/api/conflicts/hotspots');
}

/**
 * Get conflict risk distribution
 */
export async function getRiskDistribution() {
  return fetchAPI<{
    success: boolean;
    total_conflicts: number;
    distribution: Array<{
      range: string;
      count: number;
      percentage: string;
    }>;
  }>('/api/conflicts/risk-distribution');
}
