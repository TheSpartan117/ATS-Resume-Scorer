/**
 * PassProbabilityCard Component - Phase 3.2
 *
 * Displays ATS pass probability with:
 * - Large prominent percentage display
 * - Color-coded (Green >80%, Yellow 60-80%, Red <60%)
 * - Platform breakdown (Taleo, Workday, Greenhouse)
 * - Clear interpretation
 */

import React, { useState } from 'react';

interface PlatformProbability {
  probability: number;
  status: string; // excellent, good, fair, poor
}

interface PassProbabilityData {
  overall_probability: number;
  platform_breakdown: {
    [platform: string]: PlatformProbability;
  };
  confidence_level: string; // high, moderate, low
  interpretation: string;
  color_code: string; // green, yellow, red
  based_on_score: number;
}

interface PassProbabilityCardProps {
  passProbability: PassProbabilityData;
  className?: string;
}

const PassProbabilityCard: React.FC<PassProbabilityCardProps> = ({
  passProbability,
  className = '',
}) => {
  const [showDetails, setShowDetails] = useState(false);

  // Get color classes based on color code
  const getColorClasses = () => {
    switch (passProbability.color_code) {
      case 'green':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'text-green-700',
          percentage: 'text-green-600',
          badge: 'bg-green-100 text-green-800',
        };
      case 'yellow':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-700',
          percentage: 'text-yellow-600',
          badge: 'bg-yellow-100 text-yellow-800',
        };
      case 'red':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-700',
          percentage: 'text-red-600',
          badge: 'bg-red-100 text-red-800',
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'text-gray-700',
          percentage: 'text-gray-600',
          badge: 'bg-gray-100 text-gray-800',
        };
    }
  };

  const colors = getColorClasses();

  // Get platform icon
  const getPlatformIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return '✅';
      case 'good':
        return '✓';
      case 'fair':
        return '⚠️';
      case 'poor':
        return '❌';
      default:
        return '○';
    }
  };

  // Get confidence badge
  const getConfidenceBadge = () => {
    const confidenceMap: Record<string, { label: string; color: string }> = {
      high: { label: 'High Confidence', color: 'bg-blue-100 text-blue-800' },
      moderate: { label: 'Moderate Confidence', color: 'bg-blue-50 text-blue-700' },
      low: { label: 'Low Confidence', color: 'bg-gray-100 text-gray-700' },
    };

    const conf = confidenceMap[passProbability.confidence_level] || confidenceMap.moderate;

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${conf.color}`}>
        {conf.label}
      </span>
    );
  };

  return (
    <div className={`${colors.bg} border ${colors.border} rounded-lg p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">ATS Pass Probability</h3>
        {getConfidenceBadge()}
      </div>

      {/* Large Percentage Display */}
      <div className="text-center mb-4">
        <div className={`text-6xl font-bold ${colors.percentage}`}>
          {passProbability.overall_probability}%
        </div>
        <div className={`mt-2 text-base font-medium ${colors.text}`}>
          {passProbability.interpretation}
        </div>
      </div>

      {/* Platform Breakdown Toggle */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full flex items-center justify-between py-2 px-3 bg-white rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
      >
        <span className="text-sm font-medium text-gray-700">
          Platform Breakdown
        </span>
        <span className="text-gray-500">
          {showDetails ? '▼' : '▶'}
        </span>
      </button>

      {/* Platform Details */}
      {showDetails && (
        <div className="mt-3 space-y-2">
          {Object.entries(passProbability.platform_breakdown).map(([platform, data]) => (
            <div
              key={platform}
              className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">{getPlatformIcon(data.status)}</span>
                <div>
                  <div className="font-medium text-gray-900">{platform}</div>
                  <div className="text-xs text-gray-500 capitalize">{data.status}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-gray-900">
                  {data.probability}%
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Based on your overall score of {passProbability.based_on_score}/100
        </p>
      </div>
    </div>
  );
};

export default PassProbabilityCard;
