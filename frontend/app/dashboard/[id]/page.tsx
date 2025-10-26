'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getExecution, type Execution } from '@/lib/api';
import ReasoningTrace from '@/components/ReasoningTrace';
import Link from 'next/link';

export default function ExecutionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [execution, setExecution] = useState<Execution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadExecution() {
      try {
        setLoading(true);
        const data = await getExecution(id);
        setExecution(data.execution);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load execution');
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadExecution();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !execution) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Execution Not Found</h2>
          <p className="text-red-600 text-sm">{error || 'Invalid execution ID'}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="mt-4 text-sm text-blue-600 hover:text-blue-700"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <Link
              href="/dashboard"
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              ← Dashboard
            </Link>
            <div className="h-6 w-px bg-gray-300" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 font-mono">
                {execution.feature_name}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {new Date(execution.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Banner */}
        {execution.conflict_detected && (
          <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-r-lg">
            <div className="flex items-start">
              <div className="text-2xl mr-3">⚠️</div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-yellow-900">
                  Conflict Detected
                </h3>
                <p className="text-yellow-800 mt-1">
                  This PR has a {execution.conflict_score}% conflict risk with existing open PRs
                </p>

                {execution.conflicting_prs && execution.conflicting_prs.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {execution.conflicting_prs.map((pr, idx) => (
                      <div key={idx} className="bg-white rounded-lg p-3 border border-yellow-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-semibold text-gray-900">
                              PR #{pr.pr_number}
                            </span>
                            <span className="text-gray-600 ml-2">
                              {pr.pr_title}
                            </span>
                          </div>
                          <span className="text-sm font-medium text-yellow-700">
                            {pr.overlapping_files?.length || 0} overlapping files
                          </span>
                        </div>
                        {pr.overlapping_files && pr.overlapping_files.length > 0 && (
                          <div className="mt-2 text-sm text-gray-600">
                            {pr.overlapping_files.map((file, idx) => (
                              <div key={idx} className="font-mono text-xs">
                                • {file}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Details */}
          <div className="lg:col-span-1 space-y-6">
            {/* PR Info Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">PR Details</h2>

              <dl className="space-y-3 text-sm">
                <div>
                  <dt className="text-gray-600">Status</dt>
                  <dd className="mt-1">
                    {execution.success ? (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                        Success
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                        Failed
                      </span>
                    )}
                  </dd>
                </div>

                {execution.pr_number && (
                  <div>
                    <dt className="text-gray-600">PR Number</dt>
                    <dd className="mt-1 font-mono font-semibold">
                      #{execution.pr_number}
                    </dd>
                  </div>
                )}

                {execution.pr_url && (
                  <div>
                    <dt className="text-gray-600">PR Link</dt>
                    <dd className="mt-1">
                      <a
                        href={execution.pr_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-xs break-all"
                      >
                        {execution.pr_url}
                      </a>
                    </dd>
                  </div>
                )}

                <div>
                  <dt className="text-gray-600">Type</dt>
                  <dd className="mt-1">
                    {execution.is_new_feature ? (
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        New Feature
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                        Modification
                      </span>
                    )}
                  </dd>
                </div>

                <div>
                  <dt className="text-gray-600">Files Impacted</dt>
                  <dd className="mt-1 font-semibold">{execution.total_files}</dd>
                </div>

                {execution.conflict_detected && (
                  <div>
                    <dt className="text-gray-600">Conflict Risk</dt>
                    <dd className="mt-1 font-semibold text-yellow-700">
                      {execution.conflict_score}%
                    </dd>
                  </div>
                )}
              </dl>
            </div>

            {/* Impacted Files Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Impacted Files
              </h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {execution.impacted_files && execution.impacted_files.length > 0 ? (
                  execution.impacted_files.map((file, idx) => (
                    <div
                      key={idx}
                      className="text-xs font-mono bg-gray-50 px-3 py-2 rounded border border-gray-200"
                    >
                      {file}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500">
                    No files specified (new feature)
                  </p>
                )}
              </div>
            </div>

            {/* Acceptance Criteria Card */}
            {execution.acceptance_criteria && execution.acceptance_criteria.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Acceptance Criteria
                </h2>
                <ul className="space-y-2">
                  {execution.acceptance_criteria.map((criterion, idx) => (
                    <li key={idx} className="flex items-start text-sm">
                      <span className="text-green-600 mr-2">✓</span>
                      <span className="text-gray-700">{criterion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Right Column - Reasoning Trace */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <ReasoningTrace
                steps={execution.reasoning_trace || []}
                conflictDetected={execution.conflict_detected}
                conflictScore={execution.conflict_score}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
