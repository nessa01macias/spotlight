'use client';

import { useState } from 'react';
import { InformationCircleIcon } from '@heroicons/react/24/outline';

export interface Toggle {
  id: string;
  label: string;
  description?: string;
  defaultValue?: boolean;
  tooltip?: string;
}

interface ToggleGroupProps {
  title?: string;
  toggles: Toggle[];
  onChange?: (id: string, value: boolean) => void;
  className?: string;
}

/**
 * ToggleGroup - Filter toggles including "Safety proxy" with explainer
 *
 * Features:
 * - Visible toggles (not hidden in advanced)
 * - Tooltip support for each toggle
 * - Clean, accessible design
 */
export default function ToggleGroup({
  title,
  toggles,
  onChange,
  className = '',
}: ToggleGroupProps) {
  const [values, setValues] = useState<Record<string, boolean>>(
    toggles.reduce((acc, toggle) => {
      acc[toggle.id] = toggle.defaultValue ?? false;
      return acc;
    }, {} as Record<string, boolean>)
  );

  const [showTooltip, setShowTooltip] = useState<string | null>(null);

  const handleToggle = (id: string) => {
    const newValue = !values[id];
    setValues((prev) => ({ ...prev, [id]: newValue }));
    onChange?.(id, newValue);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-neutral-900">{title}</h3>
      )}

      <div className="space-y-3">
        {toggles.map((toggle) => (
          <div
            key={toggle.id}
            className="flex items-start justify-between gap-3 p-4 bg-white border border-gradient-100 rounded-lg hover:border-gradient-200 transition-colors"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <label
                  htmlFor={toggle.id}
                  className="text-sm font-medium text-neutral-900 cursor-pointer"
                >
                  {toggle.label}
                </label>
                {toggle.tooltip && (
                  <div className="relative">
                    <button
                      type="button"
                      onMouseEnter={() => setShowTooltip(toggle.id)}
                      onMouseLeave={() => setShowTooltip(null)}
                      className="text-neutral-400 hover:text-neutral-600 transition-colors"
                      aria-label="More information"
                    >
                      <InformationCircleIcon className="w-4 h-4" />
                    </button>
                    {showTooltip === toggle.id && (
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 pointer-events-none">
                        <div className="bg-neutral-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg max-w-xs">
                          {toggle.tooltip}
                          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
                            <div className="border-4 border-transparent border-t-neutral-900"></div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              {toggle.description && (
                <p className="text-xs text-neutral-600 mt-1">
                  {toggle.description}
                </p>
              )}
            </div>

            {/* Toggle switch */}
            <button
              id={toggle.id}
              type="button"
              role="switch"
              aria-checked={values[toggle.id]}
              onClick={() => handleToggle(toggle.id)}
              className={`
                relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full
                border-2 border-transparent transition-colors duration-150 ease-out
                focus:outline-none focus:ring-2 focus:ring-gradient-400 focus:ring-offset-2
                ${values[toggle.id] ? 'bg-gradient-400' : 'bg-neutral-300'}
              `}
            >
              <span
                className={`
                  pointer-events-none inline-block h-5 w-5 transform rounded-full
                  bg-white shadow ring-0 transition duration-150 ease-out
                  ${values[toggle.id] ? 'translate-x-5' : 'translate-x-0'}
                `}
              />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
