'use client';

import Link from 'next/link';
import type { Execution } from '@/lib/api';

interface PRTimelineProps {
  executions: Execution[];
}

export default function PRTimeline({ executions }: PRTimelineProps) {
  if (executions.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No executions yet</p>
        <p className="text-sm text-gray-400 mt-2">
          Run your Postman Flow to see results here
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {executions.map((execution) => (
        <Link
          key={execution.id}
          href={`/dashboard/${execution.id}`}
          className="block hover:bg-gray-50 transition-colors"
        >
          <div className="px-6 py-4">
            <div className="flex items-start justify-between">
              {/* Left side - Feature info */}
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h3 className="font-mono font-semibold text-gray-900">
                    {execution.feature_name}
                  </h3>

                  {/* Status badge */}
                  {execution.success ? (
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                      Success
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                      Failed
                    </span>
                  )}

                  {/* Conflict badge */}
                  {execution.conflict_detected && (
                    <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                      ⚠️ Conflict ({execution.conflict_score}%)
                    </span>
                  )}

                  {/* New feature badge */}
                  {execution.is_new_feature && (
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      New Feature
                    </span>
                  )}
                </div>

                {/* Timestamp and PR info */}
                <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                  <span>
                    {new Date(execution.timestamp).toLocaleString()}
                  </span>
                  {execution.pr_number && (
                    <span>PR #{execution.pr_number}</span>
                  )}
                  <span>
                    {execution.total_files} {execution.total_files === 1 ? 'file' : 'files'}
                  </span>
                </div>

                {/* Reasoning trace preview (first 2 steps) */}
                {execution.reasoning_trace && execution.reasoning_trace.length > 0 && (
                  <div className="mt-2 text-sm text-gray-600">
                    <div className="flex items-start space-x-2">
                      <span className="text-gray-400">🧠</span>
                      <div>
                        {execution.reasoning_trace.slice(0, 2).map((step, idx) => (
                          <div key={idx} className="text-xs">
                            • {step}
                          </div>
                        ))}
                        {execution.reasoning_trace.length > 2 && (
                          <div className="text-xs text-gray-400 mt-1">
                            +{execution.reasoning_trace.length - 2} more steps
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Right side - PR link */}
              <div className="ml-4">
                {execution.pr_url ? (
                  <a
                    href={execution.pr_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 border border-blue-200 rounded hover:bg-blue-50 transition-colors"
                  >
                    View PR
                    <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                ) : (
                  <span className="text-sm text-gray-400">No PR</span>
                )}
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
