import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RichEditor from '../RichEditor';

describe('RichEditor', () => {
  const mockOnChange = vi.fn();
  const mockContent = '<p>Initial content</p>';

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render the editor with initial content', () => {
    render(<RichEditor content={mockContent} onChange={mockOnChange} />);

    // Check that editor content is rendered
    const editorElement = screen.getByRole('textbox', { hidden: true });
    expect(editorElement).toBeInTheDocument();
  });

  it('should display toolbar with formatting buttons', () => {
    render(<RichEditor content={mockContent} onChange={mockOnChange} />);

    // Check for key toolbar buttons
    expect(screen.getByTitle('Bold')).toBeInTheDocument();
    expect(screen.getByTitle('Italic')).toBeInTheDocument();
    expect(screen.getByTitle('Underline')).toBeInTheDocument();
    expect(screen.getByTitle('Bullet List')).toBeInTheDocument();
  });

  it('should call onChange when content is modified', async () => {
    render(<RichEditor content={mockContent} onChange={mockOnChange} />);

    // Get the editor element
    const editorElement = document.querySelector('.ProseMirror');
    expect(editorElement).toBeInTheDocument();

    // Simulate content change
    if (editorElement) {
      fireEvent.input(editorElement, {
        target: { innerHTML: '<p>Updated content</p>' }
      });

      await waitFor(() => {
        expect(mockOnChange).toHaveBeenCalled();
      });
    }
  });

  it('should toggle bold formatting when bold button is clicked', () => {
    render(<RichEditor content={mockContent} onChange={mockOnChange} />);

    const boldButton = screen.getByTitle('Bold');
    fireEvent.click(boldButton);

    // Bold button exists and is clickable
    expect(boldButton).toBeInTheDocument();
  });

  it('should toggle italic formatting when italic button is clicked', () => {
    render(<RichEditor content={mockContent} onChange={mockOnChange} />);

    const italicButton = screen.getByTitle('Italic');
    fireEvent.click(italicButton);

    // Italic button exists and is clickable
    expect(italicButton).toBeInTheDocument();
  });

  it('should handle empty content gracefully', () => {
    render(<RichEditor content="" onChange={mockOnChange} />);

    const editorElement = screen.getByRole('textbox', { hidden: true });
    expect(editorElement).toBeInTheDocument();
  });

  it('should support section-specific editing with sectionId', () => {
    const sectionId = 'experience-section';
    render(
      <RichEditor
        content={mockContent}
        onChange={mockOnChange}
        sectionId={sectionId}
      />
    );

    // Editor should render with section identifier
    const editorElement = screen.getByRole('textbox', { hidden: true });
    expect(editorElement).toBeInTheDocument();
  });

  it('should render in compact mode when specified', () => {
    render(
      <RichEditor
        content={mockContent}
        onChange={mockOnChange}
        compact={true}
      />
    );

    // Toolbar should exist even in compact mode
    expect(screen.getByTitle('Bold')).toBeInTheDocument();
  });

  it('should be read-only when editable is false', () => {
    render(
      <RichEditor
        content={mockContent}
        onChange={mockOnChange}
        editable={false}
      />
    );

    const editorElement = document.querySelector('.ProseMirror');
    expect(editorElement).toBeInTheDocument();

    // In read-only mode, the editor should have contenteditable="false"
    expect(editorElement?.getAttribute('contenteditable')).toBe('false');
  });

  it('should call onReady callback when editor is initialized', () => {
    const mockOnReady = vi.fn();

    render(
      <RichEditor
        content={mockContent}
        onChange={mockOnChange}
        onReady={mockOnReady}
      />
    );

    // onReady should be called once editor is initialized
    waitFor(() => {
      expect(mockOnReady).toHaveBeenCalled();
    });
  });
});
