import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SplitViewEditor from './SplitViewEditor';
import * as apiClient from '../api/client';

// Mock the API client
vi.mock('../api/client', () => ({
  updateSection: vi.fn(),
}));

// Mock child components
vi.mock('./SuggestionCarousel', () => ({
  default: ({ suggestions }: any) => (
    <div data-testid="suggestion-carousel">
      {suggestions.length} suggestions
    </div>
  ),
}));

vi.mock('./SectionEditor', () => ({
  default: ({ sections, onSectionUpdate }: any) => (
    <div data-testid="section-editor">
      {sections.map((section: any) => (
        <div key={section.section_id}>
          <button
            onClick={() => onSectionUpdate(
              section.section_id,
              'updated content',
              section.start_para_idx,
              section.end_para_idx
            )}
          >
            Update {section.title}
          </button>
        </div>
      ))}
    </div>
  ),
}));

vi.mock('./OfficeViewer', () => ({
  default: ({ previewUrl }: any) => (
    <div data-testid="office-viewer">{previewUrl}</div>
  ),
}));

vi.mock('./UserMenu', () => ({
  default: () => <div data-testid="user-menu">User Menu</div>,
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({
      state: {
        result: {
          sessionId: 'test-session-123',
          sections: [
            {
              title: 'EXPERIENCE',
              content: 'Test content',
              section_id: 'exp-1',
              start_para_idx: 0,
              end_para_idx: 1,
            },
          ],
          previewUrl: 'https://example.com/preview.docx',
          score: {
            overallScore: 75,
            breakdown: {},
            issues: {
              critical: ['Critical issue 1'],
              warnings: ['Warning 1', 'Warning 2'],
              suggestions: ['Suggestion 1'],
            },
          },
        },
      },
    }),
  };
});

describe('SplitViewEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render main components', () => {
    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    expect(screen.getByTestId('suggestion-carousel')).toBeInTheDocument();
    expect(screen.getByTestId('section-editor')).toBeInTheDocument();
    expect(screen.getByTestId('office-viewer')).toBeInTheDocument();
    expect(screen.getByTestId('user-menu')).toBeInTheDocument();
  });

  it('should display suggestions from score results', () => {
    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    // Should show 4 suggestions (1 critical + 2 warnings + 1 suggestion)
    expect(screen.getByText('4 suggestions')).toBeInTheDocument();
  });

  it('should handle section update successfully', async () => {
    const mockUpdateSection = vi.spyOn(apiClient, 'updateSection').mockResolvedValue({
      success: true,
      preview_url: 'https://example.com/updated-preview.docx',
      message: 'Updated successfully',
    });

    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    const updateButton = screen.getByText('Update EXPERIENCE');
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(mockUpdateSection).toHaveBeenCalledWith({
        session_id: 'test-session-123',
        start_para_idx: 0,
        end_para_idx: 1,
        new_content: 'updated content',
      });
    });

    // Preview URL should be updated
    await waitFor(() => {
      expect(screen.getByText('https://example.com/updated-preview.docx')).toBeInTheDocument();
    });
  });

  it('should display error message on update failure', async () => {
    const mockUpdateSection = vi.spyOn(apiClient, 'updateSection').mockRejectedValue(
      new Error('Network error')
    );

    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    const updateButton = screen.getByText('Update EXPERIENCE');
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(screen.getByText(/Network error/i)).toBeInTheDocument();
    });
  });

  it('should auto-dismiss error message after 5 seconds', async () => {
    vi.useFakeTimers();

    const mockUpdateSection = vi.spyOn(apiClient, 'updateSection').mockRejectedValue(
      new Error('Test error')
    );

    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    const updateButton = screen.getByText('Update EXPERIENCE');
    fireEvent.click(updateButton);

    // Error should appear
    await waitFor(() => {
      expect(screen.getByText(/Test error/i)).toBeInTheDocument();
    });

    // Fast forward 5 seconds
    vi.advanceTimersByTime(5000);

    // Error should be dismissed
    await waitFor(() => {
      expect(screen.queryByText(/Test error/i)).not.toBeInTheDocument();
    });

    vi.useRealTimers();
  });

  it('should show loading state during update', async () => {
    let resolveUpdate: (value: any) => void;
    const updatePromise = new Promise((resolve) => {
      resolveUpdate = resolve;
    });

    const mockUpdateSection = vi.spyOn(apiClient, 'updateSection').mockReturnValue(updatePromise as any);

    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    const updateButton = screen.getByText('Update EXPERIENCE');
    fireEvent.click(updateButton);

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText(/Updating/i)).toBeInTheDocument();
    });

    // Resolve the update
    resolveUpdate!({
      success: true,
      preview_url: 'https://example.com/updated.docx',
      message: 'Success',
    });

    // Loading state should disappear
    await waitFor(() => {
      expect(screen.queryByText(/Updating/i)).not.toBeInTheDocument();
    });
  });

  it('should handle navigation to suggestions', () => {
    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    // Test that carousel allows navigation
    const carousel = screen.getByTestId('suggestion-carousel');
    expect(carousel).toBeInTheDocument();
  });

  it('should redirect to home if no result in location state', () => {
    // Mock useLocation to return empty state
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate,
        useLocation: () => ({
          state: null,
        }),
      };
    });

    render(
      <BrowserRouter>
        <SplitViewEditor />
      </BrowserRouter>
    );

    // Should navigate to home
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });
});
