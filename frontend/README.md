# ATS Resume Scorer - Frontend

React frontend for the ATS Resume Scorer platform.

## Tech Stack

- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS v3 (styling)
- ESLint (code quality)

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Development server runs on http://localhost:5173

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── App.tsx        # Main app component
├── index.css      # Tailwind directives
└── main.tsx       # Entry point
```

## Integration

This frontend connects to the FastAPI backend at `http://localhost:8000` (configured in future API client).

## Development

- Uses React 19 with TypeScript for type safety
- Tailwind CSS for styling (utility-first approach)
- Vite for fast HMR and builds
- ESLint for code quality enforcement

## Split-View Editor Components

### SuggestionCarousel
- Navigate through suggestions with prev/next buttons
- Show score and issue counts
- Display actionable items for each suggestion
- Click to highlight affected section

### SectionEditor
- Dynamic section list based on detected sections
- Collapsible sections with icons
- Debounced updates (500ms delay)
- Character count per section

### OfficeViewer
- Embed DOCX via Microsoft Office Online
- Auto-refresh on preview URL change
- Loading overlay during updates
- Error handling with download fallback

### Usage

```tsx
import SplitViewEditor from './components/SplitViewEditor';

// Route to editor after upload
<Route path="/editor" element={<SplitViewEditor />} />
```
