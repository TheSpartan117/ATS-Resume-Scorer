import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import EditorPage from '../EditorPage';

// Mock API calls
global.fetch = vi.fn();

const mockSessionData = {
  session_id: 'test-session-123',
  working_docx_url: '/api/downloads/test-session-123_working.docx',
  sections: [
    { name: 'Contact', start_para: 0, end_para: 3 },
    { name: 'Experience', start_para: 4, end_para: 10 }
  ],
  current_score: {
    overallScore: 75,
    breakdown: { contact: 8, experience: 18 }
  },
  suggestions: [
    {
      id: 'sug_001',
      type: 'missing_content',
      severity: 'critical',
      title: 'Missing phone number',
      description: 'Add phone to contact',
      location: { section: 'Contact' },
      action: 'add_phone'
    }
  ]
};

beforeEach(() => {
  vi.clearAllMocks();
  (global.fetch as any).mockResolvedValue({
    ok: true,
    json: async () => mockSessionData
  });
});

describe('EditorPage', () => {
  it('should render 70-30 split layout', async () => {
    render(
      <BrowserRouter>
        <EditorPage />
      </BrowserRouter>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/Missing phone number/i)).toBeInTheDocument();
    });

    // Check for suggestions panel (30%)
    expect(screen.getByTestId('suggestions-panel')).toBeInTheDocument();

    // Check for main panel (70%)
    expect(screen.getByRole('tablist')).toBeInTheDocument();
  });

  it('should have Rich Editor and Preview tabs', async () => {
    render(
      <BrowserRouter>
        <EditorPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Missing phone number/i)).toBeInTheDocument();
    });

    // Check for tabs
    expect(screen.getByRole('tab', { name: /Rich Editor/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Preview/i })).toBeInTheDocument();
  });

  it('should display current score', async () => {
    render(
      <BrowserRouter>
        <EditorPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/75/)).toBeInTheDocument();
    });
  });

  it('should have re-score and download buttons', async () => {
    render(
      <BrowserRouter>
        <EditorPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /re-score/i })).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /download/i })).toBeInTheDocument();
  });
});
