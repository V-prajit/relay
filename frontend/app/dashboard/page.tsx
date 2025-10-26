'use client';

import { useEffect, useState } from 'react';
import { getExecutions, getStats, type Execution, type Stats } from '@/lib/api';
import RiskMeter from '@/components/RiskMeter';
import PRTimeline from '@/components/PRTimeline';
import Link from 'next/link';

export default function DashboardPage() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [executionsData, statsData] = await Promise.all([
          getExecutions({ limit: 20 }),
          getStats()
        ]);

        setExecutions(executionsData.executions);
        setStats({
          summary: statsData.summary,
          conflicts: statsData.conflicts,
          features: statsData.features,
          activity: statsData.activity
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }

    loadData();

    // Poll for updates every 10 seconds
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Dashboard</h2>
          <p className="text-red-600 text-sm">{error}</p>
          <p className="text-red-500 text-xs mt-4">
            Make sure the Dashboard API is running on http://localhost:3002
          </p>
        </div>
      </div>
    );
  }

  const avgConflictScore = stats ? parseFloat(stats.conflicts.avg_conflict_score) : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            PM Copilot Dashboard
          </h1>
          <p className="text-gray-600 mt-1">
            AI-powered conflict detection and PR analytics
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Executions"
            value={stats?.summary.total_executions || 0}
            subtitle={`${stats?.summary.success_rate} success rate`}
            color="blue"
          />
          <StatCard
            title="Conflicts Detected"
            value={stats?.conflicts.total_with_conflicts || 0}
            subtitle={`${stats?.conflicts.conflict_rate} conflict rate`}
            color="red"
          />
          <StatCard
            title="New Features"
            value={stats?.features.new_features_created || 0}
            subtitle={`vs ${stats?.features.existing_features_modified} modified`}
            color="green"
          />
          <StatCard
            title="Last 24 Hours"
            value={stats?.activity.executions_last_24h || 0}
            subtitle="Recent activity"
            color="purple"
          />
        </div>

        {/* Risk Meter and Timeline */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Average Conflict Risk
            </h2>
            <RiskMeter score={avgConflictScore} />
            <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {stats?.conflicts.risk_distribution.high_risk || 0}
                </div>
                <div className="text-gray-600">High Risk</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {stats?.conflicts.risk_distribution.medium_risk || 0}
                </div>
                <div className="text-gray-600">Medium Risk</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {stats?.conflicts.risk_distribution.low_risk || 0}
                </div>
                <div className="text-gray-600">Low Risk</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Top Features
            </h2>
            <div className="space-y-3">
              {stats?.features.top_features.slice(0, 5).map((feature, idx) => (
                <div key={feature.feature} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-gray-400 font-medium w-6">#{idx + 1}</div>
                    <div className="font-mono text-sm text-gray-900">{feature.feature}</div>
                  </div>
                  <div className="text-sm font-semibold text-blue-600">
                    {feature.count} PRs
                  </div>
                </div>
              ))}
              {(!stats?.features.top_features || stats.features.top_features.length === 0) && (
                <div className="text-center text-gray-500 py-8">
                  No executions yet
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Executions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Recent Executions
            </h2>
          </div>
          <PRTimeline executions={executions} />
        </div>
      </main>
    </div>
  );
}

function StatCard({
  title,
  value,
  subtitle,
  color
}: {
  title: string;
  value: number;
  subtitle: string;
  color: 'blue' | 'red' | 'green' | 'purple';
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="text-sm font-medium text-gray-600 mb-1">{title}</div>
      <div className={`text-3xl font-bold ${colorClasses[color].split(' ')[1]} mb-1`}>
        {value.toLocaleString()}
      </div>
      <div className="text-xs text-gray-500">{subtitle}</div>
    </div>
  );
}
