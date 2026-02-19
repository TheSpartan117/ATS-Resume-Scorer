import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import { AuthProvider } from './contexts/AuthContext'
import UploadPage from './components/UploadPage'
import ResultsPage from './components/ResultsPage'
import EditorPage from './components/EditorPage'
import SplitViewEditor from './components/SplitViewEditor'
import SavedResumesPage from './components/SavedResumesPage'
import './index.css'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/editor" element={<SplitViewEditor />} />
          <Route path="/my-resumes" element={<SavedResumesPage />} />
        </Routes>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
