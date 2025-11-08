'use client';

import { useEffect, useState } from 'react';
import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface Stage {
  id: string;
  label: string;
  status: 'idle' | 'running' | 'done' | 'warn' | 'fail';
  ms?: number;
  cached?: boolean;
  metrics?: Record<string, any>;
}

interface LiveAgentConsoleProps {
  streamUrl: string;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

const STAGES = [
  { id: 'GEO', label: 'Geocoding city' },
  { id: 'DEMO', label: 'Demographics' },
  { id: 'COMP', label: 'Competition' },
  { id: 'TRANSIT', label: 'Transit access' },
  { id: 'TRAFFIC', label: 'Traffic analysis' },
  { id: 'RENTS', label: 'Rent estimates' },
  { id: 'REVENUE', label: 'Revenue modeling' },
];

export function LiveAgentConsole({ streamUrl, onComplete, onError }: LiveAgentConsoleProps) {
  const [stages, setStages] = useState<Stage[]>(
    STAGES.map(s => ({ ...s, status: 'idle' as const }))
  );
  const [isComplete, setIsComplete] = useState(false);
  const [hasFailed, setHasFailed] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(streamUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle keepalive
        if (data.type === 'keepalive') {
          return;
        }

        // Handle stage update
        if (data.stage && data.stage !== 'COMPLETE' && data.stage !== 'ERROR') {
          setStages(prev => prev.map(stage =>
            stage.id === data.stage
              ? {
                  ...stage,
                  status: data.status,
                  ms: data.ms,
                  cached: data.cached,
                  metrics: data.metrics
                }
              : stage
          ));
        }

        // Handle completion
        if (data.stage === 'COMPLETE') {
          setIsComplete(true);
          if (onComplete && data.result) {
            onComplete(data.result);
          }
          eventSource.close();
        }

        // Handle error
        if (data.stage === 'ERROR') {
          setHasFailed(true);
          if (onError) {
            onError(data.error || 'Unknown error occurred');
          }
          eventSource.close();
        }
      } catch (err) {
        console.error('Failed to parse SSE event:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err);
      eventSource.close();
      setHasFailed(true);
      if (onError) {
        onError('Connection to server lost');
      }
    };

    return () => {
      eventSource.close();
    };
  }, [streamUrl, onComplete, onError]);

  const getStageIcon = (stage: Stage) => {
    switch (stage.status) {
      case 'done':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />;
      case 'warn':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />;
      case 'fail':
        return <XCircleIcon className="w-5 h-5 text-red-600" />;
      case 'running':
        return (
          <div className="w-5 h-5 border-2 border-gradient-200 border-t-gradient-400 rounded-full animate-spin" />
        );
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-neutral-200" />;
    }
  };

  const getStageColor = (stage: Stage) => {
    switch (stage.status) {
      case 'done':
        return 'bg-green-50 border-green-200 text-green-900';
      case 'warn':
        return 'bg-yellow-50 border-yellow-200 text-yellow-900';
      case 'fail':
        return 'bg-red-50 border-red-200 text-red-900';
      case 'running':
        return 'bg-gradient-50 border-gradient-300 text-gradient-900';
      default:
        return 'bg-neutral-50 border-neutral-200 text-neutral-500';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-neutral-900">
          {isComplete ? 'Analysis Complete' : hasFailed ? 'Analysis Failed' : 'Analyzing...'}
        </h3>
        {!isComplete && !hasFailed && (
          <div className="flex items-center gap-2 text-sm text-neutral-600">
            <div className="w-4 h-4 border-2 border-gradient-200 border-t-gradient-400 rounded-full animate-spin" />
            <span>Processing</span>
          </div>
        )}
      </div>

      <div className="space-y-3">
        {stages.map((stage, index) => (
          <div
            key={stage.id}
            className={`flex items-center justify-between p-4 rounded-lg border transition-all ${getStageColor(
              stage
            )}`}
          >
            <div className="flex items-center gap-3">
              {getStageIcon(stage)}
              <div>
                <p className="font-medium">{stage.label}</p>
                {stage.cached && (
                  <p className="text-xs text-neutral-500 mt-1">Cached</p>
                )}
              </div>
            </div>
            {stage.ms !== undefined && (
              <span className="text-sm font-medium">{stage.ms}ms</span>
            )}
          </div>
        ))}
      </div>

      {isComplete && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-900 font-medium">
            Found top addresses! Scroll down to see recommendations.
          </p>
        </div>
      )}

      {hasFailed && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-900 font-medium">
            Analysis failed. Please try again or contact support.
          </p>
        </div>
      )}
    </div>
  );
}
