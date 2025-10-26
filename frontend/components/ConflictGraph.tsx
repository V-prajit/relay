'use client';

/**
 * ConflictGraph - Simplified visualization for conflict relationships
 *
 * For a full implementation with D3.js force-directed graph:
 * 1. npm install d3 @types/d3
 * 2. Import D3 and use force simulation
 * 3. See: https://d3js.org/d3-force
 *
 * This simple version uses basic SVG for MVP
 */

import { useEffect, useState } from 'react';
import { getConflictGraph, type ConflictGraphData } from '@/lib/api';

export default function ConflictGraph() {
  const [graphData, setGraphData] = useState<ConflictGraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadGraph() {
      try {
        const data = await getConflictGraph();
        setGraphData(data.graph);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load graph');
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !graphData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-red-600">{error || 'No graph data available'}</p>
        </div>
      </div>
    );
  }

  const { nodes, edges, stats } = graphData;

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center text-gray-500">
          <p>No conflicts to visualize</p>
          <p className="text-sm mt-2">Run flows with conflicts to see graph</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div className="bg-blue-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-600">{stats.total_nodes}</div>
          <div className="text-gray-600">Files</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-yellow-600">{stats.total_edges}</div>
          <div className="text-gray-600">Conflicts</div>
        </div>
        <div className="bg-red-50 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-red-600">{stats.high_risk_nodes}</div>
          <div className="text-gray-600">High Risk</div>
        </div>
      </div>

      {/* Simplified visualization - List view */}
      {/* For full D3 force graph, see implementation notes at top of file */}
      <div className="border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
        <h3 className="font-semibold text-gray-900 mb-3">Conflict Hotspots</h3>
        <div className="space-y-2">
          {nodes
            .sort((a, b) => b.conflicts.length - a.conflicts.length)
            .slice(0, 10)
            .map((node) => (
              <div
                key={node.id}
                className="flex items-center justify-between bg-gray-50 rounded-lg p-3"
              >
                <div className="flex items-center space-x-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: node.color }}
                  />
                  <span className="font-mono text-sm text-gray-900">
                    {node.label}
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-sm">
                  <span className="text-gray-600">
                    {node.conflicts.length} conflicts
                  </span>
                  <span
                    className="px-2 py-1 rounded text-xs font-medium"
                    style={{
                      backgroundColor: node.color + '20',
                      color: node.color
                    }}
                  >
                    {node.conflicts.length > 3 ? 'High Risk' : 'Moderate'}
                  </span>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Note about full implementation */}
      <div className="text-xs text-gray-500 bg-blue-50 border border-blue-200 rounded-lg p-3">
        💡 <strong>Pro Tip:</strong> For a full interactive force-directed graph visualization,
        install D3.js and implement force simulation. See{' '}
        <a
          href="https://d3js.org/d3-force"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline"
        >
          D3 Force Documentation
        </a>
      </div>
    </div>
  );
}
