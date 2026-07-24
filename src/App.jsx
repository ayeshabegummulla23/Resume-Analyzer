import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import UploadPage from './pages/UploadPage'
import Dashboard from './pages/Dashboard'
import CoverLetterPage from './pages/CoverLetterPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/cover-letter" element={<CoverLetterPage />} />
    </Routes>
  )
}
