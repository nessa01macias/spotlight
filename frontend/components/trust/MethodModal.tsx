'use client';

import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface MethodModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * MethodModal - "How we score" explainer modal
 *
 * Shows:
 * - Scoring formula with weights
 * - Data sources (PAAVO, HSY, Digitransit, OSM)
 * - Last refresh timestamps
 * - Methodology transparency
 */
export default function MethodModal({ isOpen, onClose }: MethodModalProps) {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-150"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-120"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-neutral-900/50 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-150"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-120"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-8 shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <Dialog.Title className="text-2xl font-semibold text-neutral-900">
                      How We Score Opportunities
                    </Dialog.Title>
                    <p className="mt-1 text-neutral-600">
                      Evidence-based methodology using public Finnish data
                    </p>
                  </div>
                  <button
                    onClick={onClose}
                    className="text-neutral-400 hover:text-neutral-600 transition-colors"
                  >
                    <XMarkIcon className="w-6 h-6" />
                  </button>
                </div>

                {/* Scoring Formula */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                    Scoring Formula
                  </h3>
                  <div className="bg-gradient-50 rounded-lg p-6 border border-gradient-100">
                    <div className="font-mono text-sm space-y-2">
                      <div className="flex justify-between">
                        <span className="text-neutral-700">Population Density</span>
                        <span className="font-semibold text-neutral-900">35%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-700">Income Fit</span>
                        <span className="font-semibold text-neutral-900">25%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-700">Transit Access</span>
                        <span className="font-semibold text-neutral-900">20%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-700">Competition</span>
                        <span className="font-semibold text-neutral-900">15%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-neutral-700">Walkability</span>
                        <span className="font-semibold text-neutral-900">5%</span>
                      </div>
                      <div className="border-t border-gradient-200 mt-2 pt-2 flex justify-between">
                        <span className="font-semibold text-neutral-900">Total Score</span>
                        <span className="font-semibold text-neutral-900">0-100</span>
                      </div>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-neutral-600">
                    * Safety proxy (nightlife density + public stats) is optional with max 5% weight cap
                  </p>
                </div>

                {/* Revenue Prediction */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                    Revenue Prediction
                  </h3>
                  <div className="space-y-3">
                    <div className="bg-neutral-50 rounded-lg p-4">
                      <code className="text-sm text-neutral-700">
                        revenue_mid = concept_base_revenue × demographic_multiplier × access_multiplier
                      </code>
                    </div>
                    <div className="bg-neutral-50 rounded-lg p-4">
                      <code className="text-sm text-neutral-700">
                        revenue_range = revenue_mid ± (15-30% based on confidence)
                      </code>
                    </div>
                  </div>
                </div>

                {/* Data Sources */}
                <div className="mb-8">
                  <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                    Data Sources
                  </h3>
                  <div className="space-y-3">
                    {[
                      {
                        name: 'Statistics Finland (PAAVO)',
                        desc: 'Demographics, income, age distribution by postal area',
                        updated: '2024 Q4',
                        coverage: '95%',
                      },
                      {
                        name: 'HSY Population Grid',
                        desc: 'Fine-grained population density (250m grid)',
                        updated: '2024 Q3',
                        coverage: '98%',
                      },
                      {
                        name: 'Digitransit Pelias',
                        desc: 'Geocoding, transit stops, routing',
                        updated: 'Real-time',
                        coverage: '99%',
                      },
                      {
                        name: 'OpenStreetMap Overpass',
                        desc: 'Competitors, POIs, walkability',
                        updated: 'Last 24h',
                        coverage: '88%',
                      },
                    ].map((source) => (
                      <div
                        key={source.name}
                        className="flex justify-between items-start p-4 border border-neutral-200 rounded-lg hover:border-gradient-200 transition-colors"
                      >
                        <div>
                          <div className="font-medium text-neutral-900">{source.name}</div>
                          <div className="text-sm text-neutral-600 mt-1">{source.desc}</div>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-xs font-medium text-confidence-veryHigh">
                            {source.coverage}
                          </div>
                          <div className="text-xs text-neutral-500 mt-1">{source.updated}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Confidence Explanation */}
                <div className="bg-gradient-50 rounded-lg p-6 border border-gradient-100">
                  <h4 className="font-semibold text-neutral-900 mb-2">
                    Understanding Confidence Scores
                  </h4>
                  <ul className="space-y-2 text-sm text-neutral-700">
                    <li>
                      <span className="font-medium text-confidence-veryHigh">≥90%</span> — Very high data coverage; estimate band ±10%
                    </li>
                    <li>
                      <span className="font-medium text-confidence-high">75-90%</span> — High data coverage; estimate band ±15%
                    </li>
                    <li>
                      <span className="font-medium text-confidence-medium">60-75%</span> — Medium data coverage; estimate band ±20%
                    </li>
                    <li>
                      <span className="font-medium text-confidence-low">&lt;60%</span> — Limited data; estimate band ±30%; use with caution
                    </li>
                  </ul>
                </div>

                {/* Footer */}
                <div className="mt-8 pt-6 border-t border-neutral-200">
                  <p className="text-sm text-neutral-600">
                    Our model learns from real outcomes. When customers report actual revenue, we improve predictions for everyone.{' '}
                    <a href="#" className="text-gradient-400 hover:underline">
                      Learn about outcome learning →
                    </a>
                  </p>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
