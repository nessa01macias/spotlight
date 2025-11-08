'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { grainTexture } from '@/lib/design-system';
import { MagnifyingGlassIcon, MapPinIcon } from '@heroicons/react/24/outline';
import type { Concept } from '@/lib/types';

export default function Home() {
  const router = useRouter();
  const [selectedConcept, setSelectedConcept] = useState<Concept>('FastCasual');
  const [city, setCity] = useState('Helsinki');
  const [loading, setLoading] = useState(false);

  const concepts: { value: Concept; label: string }[] = [
    { value: 'QSR', label: 'Quick Service' },
    { value: 'FastCasual', label: 'Fast Casual' },
    { value: 'Coffee', label: 'Coffee Shop' },
    { value: 'CasualDining', label: 'Casual Dining' },
    { value: 'FineDining', label: 'Fine Dining' },
  ];

  const exampleCities = ['Helsinki', 'Tampere', 'Turku', 'Espoo'];

  const handleRecommend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!city.trim() || !selectedConcept) return;

    setLoading(true);
    // Navigate to recommend page with params
    router.push(`/recommend?city=${encodeURIComponent(city)}&concept=${selectedConcept}&limit=10`);
  };

  return (
    <div
      className="min-h-screen bg-gradient-to-br from-gradient-50 via-white to-gradient-100 flex flex-col"
      style={grainTexture}
    >
      {/* Hero Section */}
      <div className="flex-1 flex items-center justify-center px-6">
        <div className="max-w-3xl w-full space-y-12">
          {/* Heading */}
          <div className="text-center space-y-6">
            <h1 className="text-7xl font-bold text-neutral-900 tracking-tight">
              Spotlight
            </h1>
            <p className="text-2xl text-neutral-600 leading-relaxed">
              Find your next restaurant location in 60 seconds
            </p>
            <p className="text-lg text-neutral-500">
              Get 10 ranked addresses with AI-powered predictions
            </p>
          </div>

          {/* Main Form */}
          <form onSubmit={handleRecommend} className="space-y-6">
            {/* Concept Selector */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-neutral-700">
                What concept are you opening?
              </label>
              <div className="grid grid-cols-5 gap-3">
                {concepts.map((concept) => (
                  <button
                    key={concept.value}
                    type="button"
                    onClick={() => setSelectedConcept(concept.value)}
                    className={`
                      px-4 py-3 rounded-lg border-2 font-medium transition-all
                      ${
                        selectedConcept === concept.value
                          ? 'border-gradient-400 bg-gradient-50 text-gradient-600'
                          : 'border-neutral-200 bg-white text-neutral-700 hover:border-neutral-300'
                      }
                    `}
                  >
                    {concept.label}
                  </button>
                ))}
              </div>
            </div>

            {/* City Input */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-neutral-700">
                Where are you looking?
              </label>
              <div className="relative">
                <MapPinIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="Enter city name (e.g., Helsinki)"
                  className="w-full pl-12 pr-4 py-4 border-2 border-neutral-200 rounded-lg text-lg focus:border-gradient-400 focus:outline-none transition-colors"
                  required
                />
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <span>Try:</span>
                {exampleCities.map((exCity, i) => (
                  <button
                    key={exCity}
                    type="button"
                    onClick={() => setCity(exCity)}
                    className="px-3 py-1 rounded-full bg-neutral-100 hover:bg-neutral-200 text-neutral-700 transition-colors"
                  >
                    {exCity}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`
                w-full py-5 px-6 rounded-lg font-semibold text-lg
                transition-all shadow-md hover:shadow-lg
                ${
                  loading
                    ? 'bg-neutral-300 text-neutral-500 cursor-not-allowed'
                    : 'bg-gradient-400 text-white hover:bg-gradient-500'
                }
              `}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-3">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Finding opportunities...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <MagnifyingGlassIcon className="w-6 h-6" />
                  Show Top Opportunities
                </span>
              )}
            </button>
          </form>

          {/* Secondary Action */}
          <div className="text-center pt-6 border-t border-neutral-200">
            <p className="text-neutral-600 mb-3">
              Want to explore on your own?
            </p>
            <button
              onClick={() => router.push('/discover')}
              className="text-gradient-500 hover:text-gradient-600 font-medium hover:underline transition-colors"
            >
              Browse opportunities by city →
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-8 text-center text-sm text-neutral-500">
        <p>© 2025 Spotlight. Powered by public Finnish data sources.</p>
      </footer>
    </div>
  );
}
