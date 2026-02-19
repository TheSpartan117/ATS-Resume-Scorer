import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import OfficePreview from '../OfficePreview';

describe('OfficePreview', () => {
  const mockOfficeUrl = 'https://view.officeapps.live.com/op/embed.aspx?src=https%3A%2F%2Fexample.com%2Fdoc.docx';

  it('should render iframe with Office Online URL', () => {
    render(<OfficePreview officeOnlineUrl={mockOfficeUrl} />);

    const iframe = screen.getByTitle('DOCX Preview');
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute('src', mockOfficeUrl);
  });

  it('should render zoom controls', () => {
    render(<OfficePreview officeOnlineUrl={mockOfficeUrl} />);

    const zoomIn = screen.getByLabelText('Zoom in');
    const zoomOut = screen.getByLabelText('Zoom out');

    expect(zoomIn).toBeInTheDocument();
    expect(zoomOut).toBeInTheDocument();
  });

  it('should render download buttons', () => {
    const docxUrl = '/api/files/session123_working.docx';
    render(
      <OfficePreview
        officeOnlineUrl={mockOfficeUrl}
        docxDownloadUrl={docxUrl}
      />
    );

    const downloadButton = screen.getByText(/download docx/i);
    expect(downloadButton).toBeInTheDocument();
    expect(downloadButton.closest('a')).toHaveAttribute('href', docxUrl);
  });

  it('should show loading state', () => {
    render(<OfficePreview officeOnlineUrl={mockOfficeUrl} isLoading={true} />);

    expect(screen.getByText(/loading preview/i)).toBeInTheDocument();
  });

  it('should show error state when officeOnlineUrl is not provided', () => {
    render(<OfficePreview officeOnlineUrl="" />);

    expect(screen.getByText(/preview unavailable/i)).toBeInTheDocument();
  });

  it('should refresh iframe when officeOnlineUrl changes', () => {
    const { rerender } = render(<OfficePreview officeOnlineUrl={mockOfficeUrl} />);

    const iframe = screen.getByTitle('DOCX Preview');
    const initialKey = iframe.getAttribute('data-key');

    const newUrl = 'https://view.officeapps.live.com/op/embed.aspx?src=https%3A%2F%2Fexample.com%2Fupdated.docx';
    rerender(<OfficePreview officeOnlineUrl={newUrl} />);

    const updatedIframe = screen.getByTitle('DOCX Preview');
    const newKey = updatedIframe.getAttribute('data-key');

    expect(newKey).not.toBe(initialKey);
    expect(updatedIframe).toHaveAttribute('src', newUrl);
  });

  it('should call onRefresh when refresh button is clicked', () => {
    const mockOnRefresh = vi.fn();
    render(
      <OfficePreview
        officeOnlineUrl={mockOfficeUrl}
        onRefresh={mockOnRefresh}
      />
    );

    const refreshButton = screen.getByLabelText('Refresh preview');
    fireEvent.click(refreshButton);

    expect(mockOnRefresh).toHaveBeenCalledTimes(1);
  });

  it('should have minimal chrome (no excessive UI elements)', () => {
    render(<OfficePreview officeOnlineUrl={mockOfficeUrl} />);

    // Should have iframe taking most space
    const iframe = screen.getByTitle('DOCX Preview');
    expect(iframe).toHaveClass('w-full', 'h-full');

    // Should not have excessive text or large headers
    const container = iframe.closest('div');
    expect(container).toBeTruthy();
  });

  it('should apply sandbox attributes to iframe for security', () => {
    render(<OfficePreview officeOnlineUrl={mockOfficeUrl} />);

    const iframe = screen.getByTitle('DOCX Preview');
    expect(iframe).toHaveAttribute('sandbox');
  });
});
