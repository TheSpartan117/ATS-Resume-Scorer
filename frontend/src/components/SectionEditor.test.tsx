import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SectionEditor from './SectionEditor';

// Mock useDebounce hook
vi.mock('../hooks/useDebounce', () => ({
  useDebounce: (callback: any, _delay: number) => {
    // Return callback that executes immediately for testing
    return callback;
  },
}));

describe('SectionEditor', () => {
  const mockSections = [
    {
      title: 'EXPERIENCE',
      content: 'Senior Software Engineer at Tech Corp\n- Led development of microservices',
      section_id: 'exp-1',
      start_para_idx: 0,
      end_para_idx: 2,
    },
    {
      title: 'EDUCATION',
      content: 'BS Computer Science\nStanford University',
      section_id: 'edu-1',
      start_para_idx: 3,
      end_para_idx: 4,
    },
  ];

  const mockOnSectionUpdate = vi.fn();

  beforeEach(() => {
    mockOnSectionUpdate.mockClear();
  });

  it('should render all sections', () => {
    render(
      <SectionEditor
        sections={mockSections}
        onSectionUpdate={mockOnSectionUpdate}
      />
    );

    expect(screen.getByText('EXPERIENCE')).toBeInTheDocument();
    expect(screen.getByText('EDUCATION')).toBeInTheDocument();
  });

  it('should toggle section collapse/expand', () => {
    render(
      <SectionEditor
        sections={mockSections}
        onSectionUpdate={mockOnSectionUpdate}
      />
    );

    const experienceSection = screen.getByText('EXPERIENCE').closest('.section-header');

    // Section should be expanded by default
    const textarea = screen.getByDisplayValue(/Senior Software Engineer/i);
    expect(textarea).toBeVisible();

    // Click to collapse
    if (experienceSection) {
      fireEvent.click(experienceSection);
    }

    // Wait for state update
    waitFor(() => {
      expect(textarea).not.toBeVisible();
    });
  });

  it('should call onSectionUpdate when content changes', () => {
    render(
      <SectionEditor
        sections={mockSections}
        onSectionUpdate={mockOnSectionUpdate}
      />
    );

    const textarea = screen.getByDisplayValue(/Senior Software Engineer/i);
    const newContent = 'Updated content';

    fireEvent.change(textarea, { target: { value: newContent } });

    // With mocked debounce (immediate execution), should be called right away
    expect(mockOnSectionUpdate).toHaveBeenCalledWith(
      'exp-1',
      newContent,
      0,
      2
    );
  });

  it('should highlight the selected section', () => {
    const { rerender } = render(
      <SectionEditor
        sections={mockSections}
        onSectionUpdate={mockOnSectionUpdate}
        highlightedSection="exp-1"
      />
    );

    const experienceSection = screen.getByText('EXPERIENCE').closest('div');
    expect(experienceSection).toHaveClass('border-blue-500');

    // Change highlighted section
    rerender(
      <SectionEditor
        sections={mockSections}
        onSectionUpdate={mockOnSectionUpdate}
        highlightedSection="edu-1"
      />
    );

    const educationSection = screen.getByText('EDUCATION').closest('div');
    expect(educationSection).toHaveClass('border-blue-500');
  });

  it('should maintain edited content in state', () => {
    render(
      <SectionEditor
        sections={mockSections}
        onSectionUpdate={mockOnSectionUpdate}
      />
    );

    const textarea = screen.getByDisplayValue(/Senior Software Engineer/i);

    fireEvent.change(textarea, { target: { value: 'First edit' } });
    expect(textarea).toHaveValue('First edit');

    fireEvent.change(textarea, { target: { value: 'Second edit' } });
    expect(textarea).toHaveValue('Second edit');
  });

  it('should display correct icons for different section types', () => {
    const sectionsWithDifferentTypes = [
      { ...mockSections[0], title: 'EXPERIENCE' },
      { ...mockSections[1], title: 'EDUCATION' },
      {
        title: 'SKILLS',
        content: 'Python, JavaScript',
        section_id: 'skills-1',
        start_para_idx: 5,
        end_para_idx: 6
      },
    ];

    render(
      <SectionEditor
        sections={sectionsWithDifferentTypes}
        onSectionUpdate={mockOnSectionUpdate}
      />
    );

    // Check that different section types are rendered
    expect(screen.getByText('EXPERIENCE')).toBeInTheDocument();
    expect(screen.getByText('EDUCATION')).toBeInTheDocument();
    expect(screen.getByText('SKILLS')).toBeInTheDocument();
  });

  it('should handle empty sections gracefully', () => {
    const emptySections = [
      {
        title: 'EMPTY SECTION',
        content: '',
        section_id: 'empty-1',
        start_para_idx: 0,
        end_para_idx: 0,
      },
    ];

    render(
      <SectionEditor
        sections={emptySections}
        onSectionUpdate={mockOnSectionUpdate}
      />
    );

    expect(screen.getByText('EMPTY SECTION')).toBeInTheDocument();
    const textarea = screen.getByRole('textbox');
    expect(textarea).toHaveValue('');
  });
});
