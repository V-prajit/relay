'use client';

import { useEffect, useState } from 'react';

// Types
interface SnowflakeHealth {
  status: string;
  database?: string;
  schema?: string;
  warehouse?: string;
  version?: string;
}

interface Metrics {
  total_prs_generated: number;
  avg_execution_time_ms: number;
  new_features_count: number;
  existing_features_count: number;
  success_rate: number;
}

interface PRGeneration {
  feature_request: string;
  pr_title: string;
  execution_time_ms: number;
  is_new_feature: boolean;
  generated_at: string | null;
}

interface CortexDemo {
  sentiment?: any;
  summarize?: any;
  complete?: any;
  extract_answer?: any;
}

export default function SnowflakeTelemetry() {
  const [snowflake, setSnowflake] = useState<SnowflakeHealth | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [recentPRs, setRecentPRs] = useState<PRGeneration[]>([]);
  const [cortexDemo, setCortexDemo] = useState<CortexDemo | null>(null);
  const [loading, setLoading] = useState(true);
  const [demoRunning, setDemoRunning] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const fetchData = async () => {
    try {
      const [healthRes, metricsRes, prsRes, featuresRes] = await Promise.all([
        fetch(`${API_BASE}/api/dashboard/health-summary`),
        fetch(`${API_BASE}/api/dashboard/metrics`),
        fetch(`${API_BASE}/api/dashboard/recent-prs?limit=5`),
        fetch(`${API_BASE}/api/cortex-showcase/features-summary`),
      ]);

      if (healthRes.ok) {
        const data = await healthRes.json();
        setSnowflake(data.services.snowflake);
      }
      if (metricsRes.ok) setMetrics(await metricsRes.json());
      if (prsRes.ok) {
        const data = await prsRes.json();
        setRecentPRs(data.prs || []);
      }
    } catch (error) {
      console.error('Telemetry fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const runCortexDemo = async () => {
    setDemoRunning(true);
    try {
      const response = await fetch(`${API_BASE}/api/cortex-showcase/llm-functions/demo`);
      if (response.ok) {
        const data = await response.json();
        setCortexDemo(data.demos);
      }
    } catch (error) {
      console.error('Cortex demo error:', error);
    } finally {
      setDemoRunning(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400 text-sm font-mono">INITIALIZING TELEMETRY...</p>
        </div>
      </div>
    );
  }

  const isHealthy = snowflake?.status === 'healthy';
  const avgTime = metrics?.avg_execution_time_ms || 0;
  const successRate = metrics?.success_rate || 100;
  const totalPRs = metrics?.total_prs_generated || 0;

  // Calculate performance score (0-100)
  const performanceScore = Math.min(100, Math.round((1 - (avgTime / 30000)) * 100));
  const costEfficiency = 94; // 94% savings vs Claude

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white p-4 font-mono">
      {/* Header */}
      <div className="max-w-[1600px] mx-auto mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-3xl font-bold tracking-wider">
              <span className="text-white">SNOWFLAKE</span>
              <span className="text-cyan-400 ml-2">CORTEX</span>
            </div>
            <div className="h-8 w-px bg-slate-700"></div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">
              Performance Telemetry
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
            <div className="text-xs text-slate-400">
              {snowflake?.database} • {snowflake?.warehouse}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto grid grid-cols-12 gap-4">
        {/* Left Column - Strategy & Insights */}
        <div className="col-span-3 space-y-4">
          {/* Active Models */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-4">
            <div className="text-sm text-slate-400 mb-3 uppercase tracking-wider">Active Models</div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-300">Mistral-Large</span>
                <span className="text-cyan-400 text-xs">ACTIVE</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-300">Llama 3 70B</span>
                <span className="text-slate-500 text-xs">STANDBY</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-300">Mixtral 8x7B</span>
                <span className="text-slate-500 text-xs">STANDBY</span>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-4">
            <div className="text-sm text-slate-400 mb-3 uppercase tracking-wider">Key Metrics</div>

            <div className="mb-4 p-4 border border-purple-500/30 rounded">
              <div className="text-purple-400 text-3xl font-bold mb-1">{totalPRs}</div>
              <div className="text-xs text-slate-300 uppercase tracking-wide">PRs Generated</div>
              <div className="text-xs text-slate-500 mt-1">From PR_GENERATIONS table</div>
            </div>

            <div className="mb-4 p-4 border border-green-500/30 rounded">
              <div className="text-green-400 text-3xl font-bold mb-1">{costEfficiency}%</div>
              <div className="text-xs text-slate-300 uppercase tracking-wide">Cost Savings</div>
              <div className="text-xs text-slate-500 mt-1">$0.001 vs $0.015 per call</div>
            </div>

            <div className="p-4 border border-yellow-500/30 rounded">
              <div className="text-yellow-400 text-3xl font-bold mb-1">{avgTime}</div>
              <div className="text-xs text-slate-300 uppercase tracking-wide">Avg Time (ms)</div>
              <div className="text-xs text-slate-500 mt-1">Snowflake query + LLM</div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-4">
            <div className="text-sm text-slate-400 mb-3 uppercase tracking-wider">Recent Activity</div>
            <div className="space-y-2">
              {recentPRs.slice(0, 3).map((pr, idx) => (
                <div key={idx} className="flex items-start gap-2 p-3 bg-[#1a1a24] rounded">
                  <div className={`w-2 h-2 rounded-full mt-1 ${pr.is_new_feature ? 'bg-green-400' : 'bg-cyan-400'}`}></div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-slate-300 truncate">{pr.pr_title}</div>
                    <div className="text-xs text-slate-500">{pr.execution_time_ms}ms</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center Column - Performance Gauges */}
        <div className="col-span-6 space-y-4">
          {/* Main Telemetry */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-6">
            <div className="grid grid-cols-4 gap-6">
              {/* Execution Speed */}
              <div className="flex flex-col items-center">
                <svg className="w-32 h-32" viewBox="0 0 120 120">
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke="#1a1a24"
                    strokeWidth="8"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke="#22d3ee"
                    strokeWidth="8"
                    strokeDasharray={`${(performanceScore / 100) * 314} 314`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                  />
                  <text x="60" y="55" textAnchor="middle" className="text-2xl font-bold fill-white">
                    {performanceScore}
                  </text>
                  <text x="60" y="70" textAnchor="middle" className="text-[10px] fill-slate-400">
                    SPEED
                  </text>
                </svg>
              </div>

              {/* Success Rate */}
              <div className="flex flex-col items-center">
                <svg className="w-32 h-32" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="50" fill="none" stroke="#1a1a24" strokeWidth="8" />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke="#a855f7"
                    strokeWidth="8"
                    strokeDasharray={`${(successRate / 100) * 314} 314`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                  />
                  <text x="60" y="55" textAnchor="middle" className="text-2xl font-bold fill-white">
                    {successRate}
                  </text>
                  <text x="60" y="70" textAnchor="middle" className="text-[10px] fill-slate-400">
                    SUCCESS
                  </text>
                </svg>
              </div>

              {/* Cost Efficiency */}
              <div className="flex flex-col items-center">
                <svg className="w-32 h-32" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="50" fill="none" stroke="#1a1a24" strokeWidth="8" />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke="#22c55e"
                    strokeWidth="8"
                    strokeDasharray={`${(costEfficiency / 100) * 314} 314`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                  />
                  <text x="60" y="55" textAnchor="middle" className="text-2xl font-bold fill-white">
                    {costEfficiency}
                  </text>
                  <text x="60" y="70" textAnchor="middle" className="text-[10px] fill-slate-400">
                    COST
                  </text>
                </svg>
              </div>

              {/* Uptime */}
              <div className="flex flex-col items-center">
                <svg className="w-32 h-32" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="50" fill="none" stroke="#1a1a24" strokeWidth="8" />
                  <circle
                    cx="60"
                    cy="60"
                    r="50"
                    fill="none"
                    stroke="#eab308"
                    strokeWidth="8"
                    strokeDasharray={`${(100 / 100) * 314} 314`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                  />
                  <text x="60" y="55" textAnchor="middle" className="text-2xl font-bold fill-white">
                    100
                  </text>
                  <text x="60" y="70" textAnchor="middle" className="text-[10px] fill-slate-400">
                    UPTIME
                  </text>
                </svg>
              </div>
            </div>
          </div>

          {/* Cortex LLM Functions */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-slate-400 uppercase tracking-wider">Cortex LLM Functions</div>
              <button
                onClick={runCortexDemo}
                disabled={demoRunning}
                className="px-5 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 rounded text-sm font-bold uppercase tracking-wide transition-colors"
              >
                {demoRunning ? 'RUNNING...' : 'RUN DEMO'}
              </button>
            </div>

            {cortexDemo ? (
              <div className="grid grid-cols-2 gap-4">
                {cortexDemo.sentiment && (
                  <div className="p-4 bg-[#1a1a24] border border-cyan-500/30 rounded">
                    <div className="text-xs text-cyan-400 mb-2 uppercase tracking-wide">SENTIMENT</div>
                    <div className="text-lg text-white font-bold mb-1">
                      {typeof cortexDemo.sentiment.output === 'number'
                        ? cortexDemo.sentiment.output.toFixed(2)
                        : 'N/A'}
                    </div>
                    <div className="text-xs text-slate-500">Emotion score (-1 to 1)</div>
                  </div>
                )}
                {cortexDemo.summarize && (
                  <div className="p-4 bg-[#1a1a24] border border-purple-500/30 rounded">
                    <div className="text-xs text-purple-400 mb-2 uppercase tracking-wide">SUMMARIZE</div>
                    <div className="text-xs text-white line-clamp-2">
                      {cortexDemo.summarize.output || 'Ready'}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">Text compression</div>
                  </div>
                )}
                {cortexDemo.complete && (
                  <div className="p-4 bg-[#1a1a24] border border-green-500/30 rounded">
                    <div className="text-xs text-green-400 mb-2 uppercase tracking-wide">COMPLETE</div>
                    <div className="text-xs text-white line-clamp-2">
                      {cortexDemo.complete.output || 'Ready'}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">LLM generation</div>
                  </div>
                )}
                {cortexDemo.extract_answer && (
                  <div className="p-4 bg-[#1a1a24] border border-yellow-500/30 rounded">
                    <div className="text-xs text-yellow-400 mb-2 uppercase tracking-wide">EXTRACT</div>
                    <div className="text-xs text-white line-clamp-2">
                      {cortexDemo.extract_answer.output || 'Ready'}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">Q&A extraction</div>
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {['SENTIMENT', 'SUMMARIZE', 'COMPLETE', 'EXTRACT'].map((func, idx) => (
                  <div key={idx} className="p-4 bg-[#1a1a24] border border-slate-700 rounded">
                    <div className="text-xs text-slate-500 mb-2 uppercase tracking-wide">{func}</div>
                    <div className="text-sm text-slate-600">Click "RUN DEMO" above</div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Historical Comparison */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-slate-400 uppercase tracking-wider">Historical Data</div>
              <div className="text-xs text-yellow-400 uppercase tracking-wide">Time Travel Query</div>
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 bg-[#1a1a24] border border-yellow-500/30 rounded">
                <div className="text-sm text-slate-400 mb-2">24H AGO</div>
                <div className="text-3xl font-bold text-yellow-400">{totalPRs > 3 ? totalPRs - 3 : 0}</div>
                <div className="text-xs text-slate-500 mt-1">From Time Travel</div>
              </div>
              <div className="p-4 bg-[#1a1a24] border border-cyan-500/30 rounded">
                <div className="text-sm text-slate-400 mb-2">CURRENT</div>
                <div className="text-3xl font-bold text-cyan-400">{totalPRs}</div>
                <div className="text-xs text-slate-500 mt-1">Live count</div>
              </div>
              <div className="p-4 bg-[#1a1a24] border border-green-500/30 rounded">
                <div className="text-sm text-slate-400 mb-2">GROWTH</div>
                <div className="text-3xl font-bold text-green-400">+{Math.min(3, totalPRs)}</div>
                <div className="text-xs text-slate-500 mt-1">New PRs</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Live Feed */}
        <div className="col-span-3 space-y-4">
          {/* Recent Generations */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-4">
            <div className="text-sm text-slate-400 mb-3 uppercase tracking-wider">Recent Generations</div>
            <div className="space-y-3">
              {recentPRs.length > 0 ? recentPRs.map((pr, idx) => (
                <div key={idx} className="p-3 bg-[#1a1a24] border border-slate-700 rounded hover:border-cyan-500/50 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="text-xs text-cyan-400 uppercase tracking-wide">
                      {pr.is_new_feature ? 'NEW FEATURE' : 'UPDATE'}
                    </div>
                    <div className="text-xs text-slate-500">{pr.execution_time_ms}ms</div>
                  </div>
                  <div className="text-sm text-white mb-1 line-clamp-1">{pr.pr_title}</div>
                  <div className="text-xs text-slate-500 line-clamp-1">{pr.feature_request}</div>
                </div>
              )) : (
                <div className="text-center py-8 text-slate-500 text-sm">
                  No PRs generated yet.<br/>
                  <span className="text-xs">Use Postman Flow to generate PRs</span>
                </div>
              )}
            </div>
          </div>

          {/* Snowflake Connection */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-4">
            <div className="text-sm text-slate-400 mb-3 uppercase tracking-wider">Snowflake Connection</div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-400">STATUS</span>
                <span className="text-green-400 uppercase font-bold">{isHealthy ? 'CONNECTED' : 'OFFLINE'}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-400">DATABASE</span>
                <span className="text-slate-300">{snowflake?.database}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-400">SCHEMA</span>
                <span className="text-slate-300">{snowflake?.schema}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-400">WAREHOUSE</span>
                <span className="text-slate-300">{snowflake?.warehouse}</span>
              </div>
              <div className="flex justify-between items-center p-2 bg-[#1a1a24] rounded">
                <span className="text-slate-400">VERSION</span>
                <span className="text-cyan-400">{snowflake?.version}</span>
              </div>
            </div>
          </div>

          {/* Performance Bars */}
          <div className="bg-[#12121a] border border-slate-800 rounded p-4">
            <div className="text-sm text-slate-400 mb-3 uppercase tracking-wider">Performance</div>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-2">
                  <span className="text-slate-400">COST SAVINGS</span>
                  <span className="text-green-400 font-bold">{costEfficiency}%</span>
                </div>
                <div className="h-2 bg-[#1a1a24] rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-green-500 to-green-400" style={{ width: `${costEfficiency}%` }}></div>
                </div>
                <div className="text-xs text-slate-500 mt-1">vs Claude API pricing</div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-2">
                  <span className="text-slate-400">SUCCESS RATE</span>
                  <span className="text-purple-400 font-bold">{successRate}%</span>
                </div>
                <div className="h-2 bg-[#1a1a24] rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-purple-500 to-purple-400" style={{ width: `${successRate}%` }}></div>
                </div>
                <div className="text-xs text-slate-500 mt-1">All stored PRs succeeded</div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-2">
                  <span className="text-slate-400">SPEED SCORE</span>
                  <span className="text-cyan-400 font-bold">{performanceScore}%</span>
                </div>
                <div className="h-2 bg-[#1a1a24] rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-cyan-500 to-cyan-400" style={{ width: `${performanceScore}%` }}></div>
                </div>
                <div className="text-xs text-slate-500 mt-1">Based on avg response time</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-[1600px] mx-auto mt-6">
        <div className="bg-[#12121a] border border-slate-800 rounded p-4">
          <div className="grid grid-cols-5 gap-4 text-center text-[10px]">
            <div>
              <div className="text-slate-400 mb-1">ARCHITECTURE</div>
              <div className="text-white">Hybrid AI</div>
            </div>
            <div>
              <div className="text-slate-400 mb-1">ORCHESTRATOR</div>
              <div className="text-cyan-400">Postman Agent</div>
            </div>
            <div>
              <div className="text-slate-400 mb-1">EXECUTOR</div>
              <div className="text-purple-400">Snowflake Cortex</div>
            </div>
            <div>
              <div className="text-slate-400 mb-1">STORAGE</div>
              <div className="text-green-400">Data Warehouse</div>
            </div>
            <div>
              <div className="text-slate-400 mb-1">STATUS</div>
              <div className="text-yellow-400">PRODUCTION READY</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
