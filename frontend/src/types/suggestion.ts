// frontend/src/types/suggestion.ts
export interface DetailedSuggestion {
  id: string;
  severity: 'critical' | 'warning' | 'suggestion' | 'info';
  title: string;
  description: string;
  actionable?: {
    current: string;
    target: string;
    items: string[];
  };
  affectedSection?: string;
}

export interface SuggestionCarouselProps {
  score: number;
  suggestions: DetailedSuggestion[];
  issueCounts: {
    critical: number;
    warnings: number;
    suggestions: number;
  };
  onRescore: () => void;
  onSuggestionClick: (sectionId?: string) => void;
  isRescoring?: boolean;
}
