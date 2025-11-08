'use client';

import { useEffect, useState, useRef } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { ArrowLeftIcon, MapIcon } from '@heroicons/react/24/outline';
import api from '@/lib/api';
import { Concept } from '@/lib/types';
import { grainTexture } from '@/lib/design-system';
import { AddressListItem } from '@/components/AddressListItem';
import { MapView } from '@/components/MapView';

interface MetricProvenance {
  score: number;
  weight: number;
  weighted_score: number;
  source: string;
  coverage: number;
  raw_value?: number | null;
  raw_unit?: string | null;
}

interface ScoreProvenance {
  population: MetricProvenance;
  income_fit: MetricProvenance;
  transit_access: MetricProvenance;
  competition_inverse: MetricProvenance;
  traffic_access: MetricProvenance;
  crime_penalty_cap?: MetricProvenance;
  total_score: number;
  confidence_basis: string;
}

interface RecommendedAddress {
  rank: number;
  address: string;
  lat: number;
  lng: number;
  score: number;
  revenue_min_eur: number;
  revenue_max_eur: number;
  confidence: number;
  coverage: {
    demo: number;
    comp: number;
    access: number;
    traffic: number;
    rent: number;
    crime: number;
  };
  why: string[];
  decision: 'MAKE_OFFER' | 'NEGOTIATE' | 'PASS';
  decision_reasoning?: string;
  provenance?: ScoreProvenance;
  area_id?: string;
  metrics?: Record<string, any>;
}

interface RecommendResult {
  job_id: string;
  city: string;
  concept: string;
  top: RecommendedAddress[];
  method: {
    weights_version: string;
    weights: Record<string, number>;
    sources: Array<{ name: string; refreshed_at: string }>;
  };
  degraded: string[];
}

export default function RecommendPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const city = searchParams.get('city');
  const concept = searchParams.get('concept') as Concept;
  const limit = parseInt(searchParams.get('limit') || '10', 10);

  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedRank, setSelectedRank] = useState<number | undefined>(undefined);
  const listRefs = useRef<{ [key: number]: HTMLDivElement | null }>({});
  
  // SSE stage tracking
  const [currentStage, setCurrentStage] = useState<string>('Starting');
  const [stageProgress, setStageProgress] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!city || !concept) {
      setError('Missing city or concept parameter');
      setIsLoading(false);
      return;
    }

    let eventSource: EventSource | null = null;
    let completedSuccessfully = false; // Track if job completed successfully

    const startRecommendation = async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      try {
        // Step 1: Start the recommendation job
        console.log('🎯 Starting recommendation job...');
        const response = await fetch(`${apiUrl}/api/recommend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            city,
            concept,
            limit,
            include_crime: false
          })
        });

        if (!response.ok) {
          throw new Error(`Failed to start job: ${response.statusText}`);
        }

        const data = await response.json();
        const jobIdValue = data.job_id;
        setJobId(jobIdValue);
        console.log(`✅ Job started: ${jobIdValue}`);

        // Step 2: Connect to SSE stream for progress updates
        console.log(`📡 Connecting to SSE stream...`);
        eventSource = new EventSource(`${apiUrl}/api/stream/${jobIdValue}`);

        eventSource.onopen = () => {
          console.log('✅ SSE connection established');
        };

        // Stage descriptions for better UX
        const stageDescriptions: Record<string, string> = {
          'GEO': 'Identifying high-potential neighborhoods...',
          'DEMO': 'Analyzing population & income demographics...',
          'COMP': 'Counting competitors in each area...',
          'TRANSIT': 'Evaluating metro & tram accessibility...',
          'TRAFFIC': 'Analyzing foot traffic patterns...',
          'RENTS': 'Estimating commercial rent costs...',
          'REVENUE': 'Predicting monthly revenue for each site...'
        };

        // Artificial stage progression for better UX
        const stages = ['GEO', 'DEMO', 'COMP', 'TRANSIT', 'TRAFFIC', 'RENTS', 'REVENUE'];
        let currentStageIndex = 0;
        
        const progressThroughStages = () => {
          if (currentStageIndex < stages.length) {
            const stage = stages[currentStageIndex];
            setCurrentStage(stage);
            
            // Set to "running" state
            const description = stageDescriptions[stage] || 'Processing...';
            setStageProgress(prev => ({ 
              ...prev, 
              [stage]: description
            }));
            
            // After 1 second, mark as done and move to next
            setTimeout(() => {
              setStageProgress(prev => ({ 
                ...prev, 
                [stage]: '✓ Done'
              }));
              
              currentStageIndex++;
              progressThroughStages();
            }, 1000);
          }
        };
        
        // Start artificial progression after connection opens
        setTimeout(() => {
          progressThroughStages();
        }, 500);

        // Listen for all stage events (but ignore them for UI updates)
        const handleStageEvent = (stageName: string) => (event: MessageEvent) => {
          const data = JSON.parse(event.data);
          console.log(`📡 ${stageName}:`, data);
          // Don't update UI here - artificial progression handles it
        };

        eventSource.addEventListener('GEO', handleStageEvent('GEO'));
        eventSource.addEventListener('DEMO', handleStageEvent('DEMO'));
        eventSource.addEventListener('COMP', handleStageEvent('COMP'));
        eventSource.addEventListener('TRANSIT', handleStageEvent('TRANSIT'));
        eventSource.addEventListener('TRAFFIC', handleStageEvent('TRAFFIC'));
        eventSource.addEventListener('RENTS', handleStageEvent('RENTS'));
        eventSource.addEventListener('REVENUE', handleStageEvent('REVENUE'));

        // Backend sends COMPLETE (uppercase), not complete (lowercase)
        eventSource.addEventListener('COMPLETE', (event) => {
          const data = JSON.parse(event.data);
          console.log('✅ COMPLETE event received:', data);
          
          // Mark as completed successfully to prevent onerror from showing error
          completedSuccessfully = true;
          
          // The complete event contains the full result in the job_manager
          // We need to fetch the final result
          fetch(`${apiUrl}/api/job/${jobIdValue}`)
            .then(res => res.json())
            .then(jobData => {
              console.log('✅ Final result:', jobData);
              if (jobData.result) {
                setResult(jobData.result);
              }
              setIsLoading(false);
              eventSource?.close();
            })
            .catch(err => {
              console.error('Failed to fetch final result:', err);
              setError('Job completed but failed to load results');
              setIsLoading(false);
              eventSource?.close();
            });
        });

        eventSource.addEventListener('error_event', (event) => {
          try {
            const data = JSON.parse(event.data);
            console.error('❌ Error event from backend:', data);
            setError(data.message || 'Job failed');
            setIsLoading(false);
            eventSource?.close();
          } catch (e) {
            console.error('Failed to parse error event:', e);
          }
        });

        eventSource.onerror = (error) => {
          console.error('❌ SSE connection error:', error);
          
          // Don't show error if job completed successfully (connection closes after COMPLETE)
          if (!completedSuccessfully) {
            setError('Lost connection to backend. Is the server running?');
            setIsLoading(false);
          }
          
          eventSource?.close();
        };

      } catch (err: any) {
        console.error('Failed to start recommendation:', err);
        setError(err.message || 'Failed to start recommendation');
        setIsLoading(false);
      }
    };

    startRecommendation();

    // Cleanup on unmount
    return () => {
      if (eventSource) {
        console.log('🧹 Closing SSE connection');
        eventSource.close();
      }
    };
  }, [city, concept, limit]);

  if (!city || !concept) {
    return (
      <div
        className="min-h-screen bg-gradient-to-br from-gradient-50 via-white to-gradient-100 flex items-center justify-center"
        style={grainTexture}
      >
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 max-w-md">
          <h3 className="text-lg font-semibold text-red-900 mb-2">Missing Parameters</h3>
          <p className="text-red-700 mb-4">
            City and concept are required. Please return to the home page and submit the form.
          </p>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-gradient-50 via-white to-gradient-100"
      style={grainTexture}
    >
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-neutral-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push('/')}
              className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span className="font-medium">New Search</span>
            </button>
            <div className="text-right">
              <p className="text-sm text-neutral-600">Searching for</p>
              <p className="font-semibold text-neutral-900">
                {concept} in {city}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Error State */}
        {error && !isLoading && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Go Home
            </button>
          </div>
        )}

        {/* Loading State with Stage Progress */}
        {isLoading && !error && (
          <div className="mb-8">
            <div className="bg-white rounded-xl border border-neutral-200 p-8 shadow-sm">
              <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 border-4 border-gradient-200 border-t-gradient-400 rounded-full animate-spin" />
                  <div>
                    <h3 className="text-xl font-semibold text-neutral-900">Analyzing {city}...</h3>
                    <p className="text-sm text-neutral-600">Running multi-agent analysis pipeline</p>
                  </div>
                </div>

                {/* Stage Progress List - Show all stages */}
                <div className="space-y-2">
                  {['GEO', 'DEMO', 'COMP', 'TRANSIT', 'TRAFFIC', 'RENTS', 'REVENUE'].map((stage) => {
                    const message = stageProgress[stage];
                    const isActive = currentStage === stage;
                    const isDone = message?.includes('✓');
                    const isPending = !message;
                    
                    return (
                      <div 
                        key={stage}
                        className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                          isActive 
                            ? 'bg-gradient-100 border border-gradient-300' 
                            : isDone 
                            ? 'bg-green-50 border border-green-200'
                            : 'bg-neutral-50 border border-neutral-200'
                        }`}
                      >
                        {/* Status Icon */}
                        <div className="flex-shrink-0">
                          {isDone ? (
                            <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                          ) : isActive ? (
                            <div className="w-6 h-6 border-3 border-gradient-300 border-t-gradient-500 rounded-full animate-spin" />
                          ) : (
                            <div className="w-6 h-6 rounded-full bg-neutral-300" />
                          )}
                        </div>
                        
                        {/* Stage Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className={`text-sm font-semibold ${
                              isActive ? 'text-gradient-700' : isDone ? 'text-green-700' : 'text-neutral-500'
                            }`}>
                              {stage}
                            </p>
                            {isActive && (
                              <span className="text-xs text-gradient-600 font-medium">Running...</span>
                            )}
                          </div>
                          <p className={`text-xs mt-0.5 ${
                            isActive ? 'text-gradient-600' : isDone ? 'text-green-600' : 'text-neutral-400'
                          }`}>
                            {message || 'Pending...'}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Results Header with Tour Button */}
            <div className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                    Top {result.top.length} Addresses for {result.concept} in {result.city}
                  </h2>
                  <p className="text-neutral-600">
                    Click any address or map pin to explore. Results ranked by predicted revenue and confidence.
                  </p>
                </div>
                <button
                  onClick={() => {
                    const top5 = result.top.slice(0, 5);
                    const waypoints = top5.slice(1, -1).map(addr => `${addr.lat},${addr.lng}`).join('|');
                    const origin = `${top5[0].lat},${top5[0].lng}`;
                    const destination = `${top5[top5.length - 1].lat},${top5[top5.length - 1].lng}`;
                    const tourUrl = `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}&waypoints=${waypoints}&travelmode=walking`;
                    window.open(tourUrl, '_blank');
                  }}
                  className="px-4 py-2 rounded-lg font-medium text-white bg-gradient-400 hover:bg-gradient-300 transition-colors flex items-center gap-2 shadow-sm whitespace-nowrap"
                >
                  <MapIcon className="w-5 h-5" />
                  Plan Tour (Top 5)
                </button>
              </div>
              {result.degraded.length > 0 && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-900 font-medium">
                    ⚠ Some data sources were unavailable: {result.degraded.join(', ')}
                  </p>
                </div>
              )}
            </div>

            {/* Split Screen Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: Scrollable Address List */}
              <div className="space-y-3 max-h-[800px] overflow-y-auto pr-2">
                {result.top.map((address) => (
                  <div
                    key={address.rank}
                    ref={(el) => {
                      listRefs.current[address.rank] = el;
                    }}
                  >
                    <AddressListItem
                      {...address}
                      concept={result.concept}
                      isSelected={selectedRank === address.rank}
                      onClick={() => {
                        setSelectedRank(address.rank);
                      }}
                    />
                  </div>
                ))}
              </div>

              {/* Right: Sticky Map */}
              <div className="lg:sticky lg:top-4 h-[800px]">
                <MapView
                  locations={result.top.map(addr => ({
                    rank: addr.rank,
                    lat: addr.lat,
                    lng: addr.lng,
                    address: addr.address,
                    decision: addr.decision,
                  }))}
                  selectedRank={selectedRank}
                  onPinClick={(rank) => {
                    setSelectedRank(rank);
                    // Scroll the selected card into view
                    listRefs.current[rank]?.scrollIntoView({
                      behavior: 'smooth',
                      block: 'nearest',
                    });
                  }}
                  apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || 'AIzaSyBXGbZ0f6cCG4Kf6PpxBt5y9eKhPJU8vX4'}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
