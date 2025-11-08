'use client';

import { useState, KeyboardEvent } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface UniversalSearchProps {
  defaultQuery?: string;
  onSearch?: (query: string) => void;
  size?: 'default' | 'large';
}

/**
 * UniversalSearch - Large centered search with clickable example chips
 *
 * Features:
 * - Keyboard support (Enter to submit, clear focus ring)
 * - Clickable example chips that prefill and submit
 * - Gradient-themed focus states
 * - Optimistic navigation (route first, hydrate after)
 */
export default function UniversalSearch({
  defaultQuery = '',
  onSearch,
  size = 'default',
}: UniversalSearchProps) {
  const router = useRouter();
  const [query, setQuery] = useState(defaultQuery);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a city or address');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Call universal search API
      const result = await api.universalSearch(query.trim());

      // Route based on search type
      if (result.search_type === 'discovery') {
        // Redirect to discovery view with city
        const params = new URLSearchParams({ city: result.city || query });
        router.push(`/discover?${params.toString()}`);
      } else if (result.search_type === 'single_site') {
        // Redirect to analysis with single address
        const params = new URLSearchParams({ addresses: result.addresses?.[0] || query });
        router.push(`/analyze?${params.toString()}`);
      } else if (result.search_type === 'comparison') {
        // Redirect to analysis with multiple addresses
        const params = new URLSearchParams({ addresses: result.addresses?.join('|') || query });
        router.push(`/analyze?${params.toString()}`);
      }

      if (onSearch) {
        onSearch(query);
      }
    } catch (err: any) {
      console.error('Search error:', err);
      setError(err.response?.data?.detail || 'Search failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
    // Auto-submit after a brief delay to show the change
    setTimeout(() => {
      const form = document.querySelector('form');
      form?.requestSubmit();
    }, 100);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.form?.requestSubmit();
    }
  };

  const isLarge = size === 'large';

  return (
    <div className={`w-full ${isLarge ? 'max-w-4xl' : 'max-w-3xl'}`}>
      <form onSubmit={handleSearch} className="relative">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Where are you looking to expand?"
            className={`
              w-full px-6 text-lg border-2 border-gradient-200 rounded-xl
              bg-white shadow-sm
              focus:outline-none focus:border-gradient-400 focus:ring-4 focus:ring-gradient-100
              transition-all duration-150 ease-out
              disabled:opacity-50 disabled:cursor-not-allowed
              ${isLarge ? 'py-5 pr-16 text-xl' : 'py-4 pr-14'}
            `}
            disabled={isLoading}
            aria-label="Search for city or address"
          />
          <button
            type="submit"
            disabled={isLoading}
            className={`
              absolute right-2 top-1/2 -translate-y-1/2
              bg-gradient-400 text-white rounded-lg
              hover:bg-gradient-300 active:bg-gradient-400
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-150 ease-out
              shadow-sm hover:shadow-md
              ${isLarge ? 'p-3' : 'p-2.5'}
            `}
            aria-label="Submit search"
          >
            {isLoading ? (
              <div className={`border-2 border-white border-t-transparent rounded-full animate-spin ${isLarge ? 'w-7 h-7' : 'w-6 h-6'}`} />
            ) : (
              <MagnifyingGlassIcon className={isLarge ? 'w-7 h-7' : 'w-6 h-6'} />
            )}
          </button>
        </div>

        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Clickable example chips */}
        <div className="mt-4 flex items-center gap-2 flex-wrap">
          <span className="text-sm text-neutral-600">Try:</span>
          {['Helsinki', '00100', 'Kamppi 5'].map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => handleExampleClick(example)}
              className="px-3 py-1.5 text-sm font-medium text-gradient-400 bg-gradient-50 border border-gradient-200 rounded-lg hover:bg-gradient-100 hover:border-gradient-300 transition-all duration-150 ease-out"
            >
              {example}
            </button>
          ))}
        </div>
      </form>

      {isLoading && (
        <div className="mt-6 text-center">
          <p className="text-sm text-neutral-600">Analyzing location data...</p>
        </div>
      )}
    </div>
  );
}
