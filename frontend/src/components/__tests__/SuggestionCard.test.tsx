import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import SuggestionCard from '../SuggestionCard';

describe('SuggestionCard', () => {
  const mockOnAction = vi.fn();
  const mockOnDismiss = vi.fn();

  beforeEach(() => {
    mockOnAction.mockClear();
    mockOnDismiss.mockClear();
  });

  it('should render critical suggestion with all details', () => {
    const suggestion = {
      id: 'sug_001',
      type: 'missing_content',
      severity: 'critical',
      title: 'Missing phone number',
      description: 'ATS systems expect phone in contact info',
      location: { section: 'Contact', line: null },
      action: 'add_phone',
      example: '(555) 123-4567',
    };

    render(
      <SuggestionCard
        suggestion={suggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    // Check title with severity icon
    expect(screen.getByText(/Missing phone number/i)).toBeInTheDocument();

    // Check location
    expect(screen.getByText(/Location:/i)).toBeInTheDocument();

    // Check description
    expect(screen.getByText(/ATS systems expect phone/i)).toBeInTheDocument();

    // Check example
    expect(screen.getByText(/\(555\) 123-4567/i)).toBeInTheDocument();
  });

  it('should render warning suggestion with action buttons', () => {
    const suggestion = {
      id: 'sug_002',
      type: 'content_change',
      severity: 'warning',
      title: 'Weak action verb',
      description: "Replace 'Responsible for' with stronger verb",
      location: { section: 'Experience', line: 15, para_idx: 8 },
      current_text: 'Responsible for managing team',
      suggested_text: 'Led cross-functional team',
      action: 'replace_text',
    };

    render(
      <SuggestionCard
        suggestion={suggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    // Check title
    expect(screen.getByText(/Weak action verb/i)).toBeInTheDocument();

    // Check current and suggested text
    expect(screen.getByText(/Responsible for managing team/i)).toBeInTheDocument();
    expect(screen.getByText(/Led cross-functional team/i)).toBeInTheDocument();

    // Check for action buttons
    expect(screen.getByRole('button', { name: /Show Location/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Replace Text/i })).toBeInTheDocument();
  });

  it('should call onAction when action button is clicked', () => {
    const suggestion = {
      id: 'sug_001',
      type: 'missing_content',
      severity: 'critical',
      title: 'Missing phone number',
      description: 'ATS systems expect phone in contact info',
      location: { section: 'Contact', line: null },
      action: 'add_phone',
      example: '(555) 123-4567',
    };

    render(
      <SuggestionCard
        suggestion={suggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    const actionButton = screen.getByRole('button', { name: /Add Phone/i });
    fireEvent.click(actionButton);

    expect(mockOnAction).toHaveBeenCalledWith(suggestion, 'add_phone');
  });

  it('should call onDismiss when dismiss button is clicked', () => {
    const suggestion = {
      id: 'sug_001',
      type: 'missing_content',
      severity: 'critical',
      title: 'Missing phone number',
      description: 'ATS systems expect phone in contact info',
      location: { section: 'Contact', line: null },
      action: 'add_phone',
      example: '(555) 123-4567',
    };

    render(
      <SuggestionCard
        suggestion={suggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    const dismissButton = screen.getByRole('button', { name: /dismiss/i });
    fireEvent.click(dismissButton);

    expect(mockOnDismiss).toHaveBeenCalledWith('sug_001');
  });

  it('should display different severity styles', () => {
    const criticalSuggestion = {
      id: 'sug_001',
      type: 'missing_content',
      severity: 'critical',
      title: 'Critical issue',
      description: 'This is critical',
      location: { section: 'Contact', line: null },
      action: 'add_phone',
      example: '(555) 123-4567',
    };

    const { rerender } = render(
      <SuggestionCard
        suggestion={criticalSuggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    const criticalCard = screen.getByText(/Critical issue/i).closest('.suggestion-card');
    expect(criticalCard).toHaveClass('severity-critical');

    const warningSuggestion = {
      ...criticalSuggestion,
      id: 'sug_002',
      severity: 'warning',
      title: 'Warning issue',
    };

    rerender(
      <SuggestionCard
        suggestion={warningSuggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    const warningCard = screen.getByText(/Warning issue/i).closest('.suggestion-card');
    expect(warningCard).toHaveClass('severity-warning');
  });

  it('should render missing section suggestion with add button', () => {
    const suggestion = {
      id: 'sug_003',
      type: 'missing_section',
      severity: 'warning',
      title: 'Missing Skills section',
      description: '+10 ATS points with Skills listed',
      location: { section: 'Should be after Experience', line: null },
      action: 'add_section',
      example: 'Technical + Soft skills',
    };

    render(
      <SuggestionCard
        suggestion={suggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText(/Missing Skills section/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Add Skills Section/i })).toBeInTheDocument();
  });

  it('should render formatting issue with show location only', () => {
    const suggestion = {
      id: 'sug_004',
      type: 'formatting',
      severity: 'info',
      title: 'Inconsistent date format',
      description: 'Mix of "Jan 2020" & "1/20" formats',
      location: { section: 'Education', line: 42 },
      action: 'show_location',
    };

    render(
      <SuggestionCard
        suggestion={suggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText(/Inconsistent date format/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Show Location/i })).toBeInTheDocument();
    // Should not have replace button for formatting issues
    expect(screen.queryByRole('button', { name: /Replace/i })).not.toBeInTheDocument();
  });

  it('should handle fixed state correctly', () => {
    const suggestion = {
      id: 'sug_001',
      type: 'missing_content',
      severity: 'critical',
      title: 'Missing phone number',
      description: 'ATS systems expect phone in contact info',
      location: { section: 'Contact', line: null },
      action: 'add_phone',
      example: '(555) 123-4567',
      state: 'fixed',
    };

    render(
      <SuggestionCard
        suggestion={suggestion}
        onAction={mockOnAction}
        onDismiss={mockOnDismiss}
      />
    );

    // Should show fixed badge
    expect(screen.getByText(/Fixed/i)).toBeInTheDocument();

    // Action buttons should be disabled or hidden
    const actionButton = screen.queryByRole('button', { name: /Add Phone/i });
    if (actionButton) {
      expect(actionButton).toBeDisabled();
    }
  });
});
