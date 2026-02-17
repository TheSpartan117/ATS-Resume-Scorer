import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import UploadPage from './components/UploadPage'
import ResultsPage from './components/ResultsPage'
import EditorPage from './components/EditorPage'
import './index.css'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/editor" element={<EditorPage />} />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
