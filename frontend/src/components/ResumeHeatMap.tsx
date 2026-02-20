/**
 * Resume Heat Map Component
 *
 * Visualizes keyword matches in the resume using color highlighting:
 * - Green: High match (>0.8 similarity)
 * - Yellow: Moderate match (0.5-0.8)
 * - No highlight: Low match (<0.5)
 *
 * Uses semantic similarity scores from backend for accurate highlighting.
 */

import React, { useState, useMemo } from 'react';

interface KeywordMatch {
  keyword: string;
  similarity: number;
  positions?: number[];
}

interface ResumeHeatMapProps {
  resumeText: string;
  keywords: KeywordMatch[];
  showHeatMap?: boolean;
  onToggle?: (show: boolean) => void;
}

interface WordHighlight {
  text: string;
  highlightClass: string;
  matchedKeyword?: string;
  similarity?: number;
}

const ResumeHeatMap: React.FC<ResumeHeatMapProps> = ({
  resumeText,
  keywords,
  showHeatMap = true,
  onToggle
}) => {
  const [isEnabled, setIsEnabled] = useState(showHeatMap);

  // Process text and apply highlighting
  const highlightedWords = useMemo(() => {
    if (!isEnabled || !keywords || keywords.length === 0) {
      return [];
    }

    // Split resume into words while preserving structure
    const words = resumeText.split(/(\s+)/);
    const result: WordHighlight[] = [];

    // Create keyword lookup map
    const keywordMap = new Map<string, KeywordMatch>();
    keywords.forEach(kw => {
      keywordMap.set(kw.keyword.toLowerCase(), kw);
    });

    // Process each word
    for (let i = 0; i < words.length; i++) {
      const word = words[i];

      // Preserve whitespace as-is
      if (/^\s+$/.test(word)) {
        result.push({
          text: word,
          highlightClass: ''
        });
        continue;
      }

      // Find best match for this word
      const cleanWord = word.toLowerCase().replace(/[^\w\s]/g, '');
      let bestMatch: { keyword: KeywordMatch; similarity: number } | null = null;

      // Check for exact matches first
      for (const [kwText, kwData] of keywordMap.entries()) {
        if (cleanWord === kwText.toLowerCase()) {
          bestMatch = { keyword: kwData, similarity: 1.0 };
          break;
        }
      }

      // If no exact match, check for partial matches
      if (!bestMatch) {
        for (const [kwText, kwData] of keywordMap.entries()) {
          // Check if this word is part of a multi-word keyword
          if (kwText.toLowerCase().includes(cleanWord) || cleanWord.includes(kwText.toLowerCase())) {
            // Use fuzzy matching or provided similarity
            const similarity = kwData.similarity || calculateSimilarity(cleanWord, kwText);
            if (!bestMatch || similarity > bestMatch.similarity) {
              bestMatch = { keyword: kwData, similarity };
            }
          }
        }
      }

      // Apply highlighting based on similarity
      if (bestMatch && bestMatch.similarity >= 0.5) {
        result.push({
          text: word,
          highlightClass: getHighlightClass(bestMatch.similarity),
          matchedKeyword: bestMatch.keyword.keyword,
          similarity: bestMatch.similarity
        });
      } else {
        result.push({
          text: word,
          highlightClass: ''
        });
      }
    }

    return result;
  }, [resumeText, keywords, isEnabled]);

  // Calculate similarity between two strings (simple implementation)
  const calculateSimilarity = (word1: string, word2: string): number => {
    const longer = word1.length > word2.length ? word1 : word2;
    const shorter = word1.length > word2.length ? word2 : word1;

    if (longer.length === 0) return 1.0;

    const editDistance = levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  };

  // Levenshtein distance for string similarity
  const levenshteinDistance = (str1: string, str2: string): number => {
    const matrix: number[][] = [];

    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }

    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }

    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }

    return matrix[str2.length][str1.length];
  };

  // Get CSS class for highlight color
  const getHighlightClass = (similarity: number): string => {
    if (similarity > 0.8) {
      return 'bg-green-200 hover:bg-green-300 transition-colors';
    } else if (similarity > 0.5) {
      return 'bg-yellow-200 hover:bg-yellow-300 transition-colors';
    }
    return '';
  };

  const handleToggle = () => {
    const newState = !isEnabled;
    setIsEnabled(newState);
    if (onToggle) {
      onToggle(newState);
    }
  };

  // Calculate statistics
  const stats = useMemo(() => {
    const highMatches = keywords.filter(kw => kw.similarity > 0.8).length;
    const moderateMatches = keywords.filter(kw => kw.similarity >= 0.5 && kw.similarity <= 0.8).length;
    const totalMatches = highMatches + moderateMatches;

    return { highMatches, moderateMatches, totalMatches };
  }, [keywords]);

  return (
    <div className="resume-heat-map-container">
      {/* Heat Map Controls */}
      <div className="flex items-center justify-between mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center gap-4">
          <button
            onClick={handleToggle}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isEnabled
                ? 'bg-blue-500 text-white hover:bg-blue-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isEnabled ? 'Hide' : 'Show'} Heat Map
          </button>

          {isEnabled && (
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-200 rounded"></div>
                <span>High Match ({stats.highMatches})</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-200 rounded"></div>
                <span>Moderate Match ({stats.moderateMatches})</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded"></div>
                <span>No Match</span>
              </div>
            </div>
          )}
        </div>

        {isEnabled && (
          <div className="text-sm font-medium text-gray-700">
            Total Matches: {stats.totalMatches} / {keywords.length}
          </div>
        )}
      </div>

      {/* Heat Map Display */}
      <div className="resume-content bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        {isEnabled && highlightedWords.length > 0 ? (
          <div className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
            {highlightedWords.map((wordData, idx) => (
              <span
                key={idx}
                className={wordData.highlightClass}
                title={
                  wordData.matchedKeyword
                    ? `Matches: ${wordData.matchedKeyword} (${Math.round((wordData.similarity || 0) * 100)}% similarity)`
                    : ''
                }
              >
                {wordData.text}
              </span>
            ))}
          </div>
        ) : (
          <div className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
            {resumeText}
          </div>
        )}
      </div>

      {/* Legend */}
      {isEnabled && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2">How to Read the Heat Map</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>
              <span className="font-medium">Green highlights:</span> Strong keyword matches (80%+ similarity) - These are well-aligned with the job description.
            </li>
            <li>
              <span className="font-medium">Yellow highlights:</span> Moderate matches (50-80% similarity) - Related terms that partially match requirements.
            </li>
            <li>
              <span className="font-medium">No highlight:</span> Words that don't match job description keywords.
            </li>
            <li className="mt-2 text-xs text-blue-600">
              <strong>Tip:</strong> Hover over highlighted words to see which keywords they match.
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ResumeHeatMap;

/**
 * Utility function to extract keywords from API response
 */
export const extractKeywordsFromScore = (scoreResponse: any): KeywordMatch[] => {
  if (!scoreResponse) return [];

  const keywords: KeywordMatch[] = [];

  // Extract from matched_keywords if available
  if (scoreResponse.matched_keywords) {
    scoreResponse.matched_keywords.forEach((kw: any) => {
      keywords.push({
        keyword: kw.keyword || kw,
        similarity: kw.similarity || 1.0
      });
    });
  }

  // Extract from missing_keywords (mark as low similarity)
  if (scoreResponse.missing_keywords) {
    scoreResponse.missing_keywords.forEach((kw: any) => {
      keywords.push({
        keyword: kw.keyword || kw,
        similarity: 0.3 // Low similarity for missing keywords
      });
    });
  }

  return keywords;
};
