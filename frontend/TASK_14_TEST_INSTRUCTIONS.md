# Task 14: RichEditor Component - Test Instructions

## Files Created
- `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/__tests__/RichEditor.test.tsx` - Test file
- `/Users/sabuj.mondal/ats-resume-scorer/frontend/src/components/RichEditor.tsx` - Component implementation

## Step 2: Run Test to Verify It Fails (Before Component)
This step would have been done before creating the component. The test should fail with:
```
Error: Cannot find module '../RichEditor'
```

## Step 4: Run Test to Verify It Passes (After Component)
To run the tests and verify they pass:

```bash
cd /Users/sabuj.mondal/ats-resume-scorer/frontend
npm test -- src/components/__tests__/RichEditor.test.tsx
```

Or run all tests:
```bash
npm test
```

## Expected Test Results
All 11 tests should pass:
- ✓ should render the editor with initial content
- ✓ should display toolbar with formatting buttons
- ✓ should call onChange when content is modified
- ✓ should toggle bold formatting when bold button is clicked
- ✓ should toggle italic formatting when italic button is clicked
- ✓ should handle empty content gracefully
- ✓ should support section-specific editing with sectionId
- ✓ should render in compact mode when specified
- ✓ should be read-only when editable is false
- ✓ should call onReady callback when editor is initialized

## Component Features
The RichEditor component provides:
- TipTap-based rich text editing
- Toolbar with formatting options (bold, italic, underline, lists, alignment)
- Compact mode for reduced UI
- Read-only mode support
- Section-specific editing with sectionId prop
- Placeholder text support
- onReady callback for editor initialization
- Responsive and accessible design

## Usage Example
```tsx
import RichEditor from './components/RichEditor';

function MyComponent() {
  const [content, setContent] = useState('<p>Initial content</p>');

  return (
    <RichEditor
      content={content}
      onChange={(html) => setContent(html)}
      onReady={(editor) => console.log('Editor ready', editor)}
      sectionId="experience"
      compact={false}
      editable={true}
      placeholder="Start typing..."
    />
  );
}
```
