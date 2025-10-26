'use client';

import { useState } from 'react';

interface ReasoningTraceProps {
  steps: string[];
  conflictDetected?: boolean;
  conflictScore?: number;
}

export default function ReasoningTrace({
  steps,
  conflictDetected = false,
  conflictScore = 0
}: ReasoningTraceProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (index: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSteps(newExpanded);
  };

  if (steps.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No reasoning trace available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          🧠 AI Agent Reasoning Trace
        </h3>
        <div className="text-sm text-gray-500">
          {steps.length} steps
        </div>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

        {/* Steps */}
        <div className="space-y-6">
          {steps.map((step, index) => {
            const isExpanded = expandedSteps.has(index);
            const isConflictStep = step.toLowerCase().includes('conflict');
            const isErrorStep = step.toLowerCase().includes('error') || step.toLowerCase().includes('fail');

            return (
              <div key={index} className="relative pl-12">
                {/* Step number bubble */}
                <div
                  className={`absolute left-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    isErrorStep
                      ? 'bg-red-100 text-red-600'
                      : isConflictStep
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-blue-100 text-blue-600'
                  }`}
                >
                  {index + 1}
                </div>

                {/* Step content */}
                <div
                  className={`rounded-lg border p-4 transition-all ${
                    isErrorStep
                      ? 'border-red-200 bg-red-50'
                      : isConflictStep
                      ? 'border-yellow-200 bg-yellow-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <p className="text-sm text-gray-900 flex-1">
                      {step}
                    </p>

                    {/* Expand button if step is long */}
                    {step.length > 100 && (
                      <button
                        onClick={() => toggleStep(index)}
                        className="ml-2 text-xs text-blue-600 hover:text-blue-700"
                      >
                        {isExpanded ? 'Less' : 'More'}
                      </button>
                    )}
                  </div>

                  {/* Expanded details */}
                  {isExpanded && step.length > 100 && (
                    <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-600">
                      {step}
                    </div>
                  )}

                  {/* Special indicators */}
                  {isConflictStep && (
                    <div className="mt-2 text-xs font-medium text-yellow-700">
                      ⚠️ Conflict detected at this step
                    </div>
                  )}

                  {isErrorStep && (
                    <div className="mt-2 text-xs font-medium text-red-700">
                      ❌ Error encountered
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Final result indicator */}
        <div className="relative pl-12 mt-6">
          <div
            className={`absolute left-0 w-8 h-8 rounded-full flex items-center justify-center ${
              conflictDetected
                ? 'bg-yellow-400 text-white'
                : 'bg-green-500 text-white'
            }`}
          >
            {conflictDetected ? '⚠️' : '✓'}
          </div>

          <div
            className={`rounded-lg border p-4 ${
              conflictDetected
                ? 'border-yellow-300 bg-yellow-50'
                : 'border-green-300 bg-green-50'
            }`}
          >
            <div className="font-semibold text-sm">
              {conflictDetected ? (
                <span className="text-yellow-800">
                  ⚠️ Completed with Conflicts (Risk: {conflictScore}%)
                </span>
              ) : (
                <span className="text-green-800">
                  ✅ Completed Successfully
                </span>
              )}
            </div>
            <div className="text-xs text-gray-600 mt-1">
              All steps executed by AI Agent
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
