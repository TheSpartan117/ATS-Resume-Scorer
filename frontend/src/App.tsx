import { Routes, Route } from 'react-router-dom'
import UploadPage from './components/UploadPage'
import ResultsPage from './components/ResultsPage'
import './index.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/results" element={<ResultsPage />} />
    </Routes>
  )
}

export default App
