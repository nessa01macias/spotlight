'use client';

import Button from '@/components/ui/Button';
import { ArrowsRightLeftIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline';

interface StickyActionBarProps {
  onCompare?: () => void;
  onDownload?: () => void;
  compareLabel?: string;
  downloadLabel?: string;
  isLoading?: boolean;
  className?: string;
}

/**
 * StickyActionBar - Bottom sticky bar with Compare/Download CTAs
 *
 * Always visible at bottom of Area Detail/Site Analysis pages
 * Max 2 actions per screen
 */
export default function StickyActionBar({
  onCompare,
  onDownload,
  compareLabel = 'Compare against top alternatives',
  downloadLabel = 'Download investor-ready PDF',
  isLoading = false,
  className = '',
}: StickyActionBarProps) {
  return (
    <div className={`sticky bottom-0 left-0 right-0 z-40 ${className}`}>
      <div className="bg-white border-t border-gradient-200 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-end gap-3">
            {onCompare && (
              <Button
                variant="secondary"
                size="md"
                onClick={onCompare}
                isLoading={isLoading}
              >
                <ArrowsRightLeftIcon className="w-5 h-5 mr-2" />
                {compareLabel}
              </Button>
            )}
            {onDownload && (
              <Button
                variant="primary"
                size="md"
                onClick={onDownload}
                isLoading={isLoading}
              >
                <DocumentArrowDownIcon className="w-5 h-5 mr-2" />
                {downloadLabel}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
