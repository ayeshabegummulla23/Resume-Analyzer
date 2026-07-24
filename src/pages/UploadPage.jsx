import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Spinner from '../components/Spinner'
import '../App.css'

const API = 'http://127.0.0.1:8000'

export default function UploadPage() {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const inputRef = useRef(null)
  const navigate = useNavigate()

  const allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ]

  function handleFile(f) {
    if (f && allowedTypes.includes(f.type)) {
      setFile(f)
    } else {
      alert('Please upload a PDF or DOCX file.')
    }
  }

  function onDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    handleFile(f)
  }

  function onDragOver(e) {
    e.preventDefault()
    setIsDragging(true)
  }

  function onDragLeave() {
    setIsDragging(false)
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B'
    return (bytes / 1024).toFixed(1) + ' KB'
  }

  // Step 1: Upload the file, Step 2: Analyze it
  async function handleAnalyze() {
    if (!file) return

    setIsLoading(true)

    try {
      // ── Step 1: Upload the resume file ──
      const formData = new FormData()
      formData.append('file', file)

      const uploadRes = await fetch(`${API}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!uploadRes.ok) {
        const err = await uploadRes.json()
        throw new Error(err.detail || 'Upload failed')
      }

      // ── Step 2: Trigger analysis on the uploaded file ──
      const analyzeRes = await fetch(`${API}/analyze`, {
        method: 'POST',
      })

      if (!analyzeRes.ok) {
        const err = await analyzeRes.json()
        throw new Error(err.detail || 'Analysis failed')
      }

      const data = await analyzeRes.json()

      // ── Step 3: Save results and navigate ──
      localStorage.setItem('resumeData', JSON.stringify(data.results))
      navigate('/dashboard')
    } catch (err) {
      console.error(err)
      alert(err.message || 'Something went wrong. Is the backend running?')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) return <Spinner />

  return (
    <div className="page upload-page">
      <div className="container">
        <Navbar />

        <section className="upload-section">
          <h1>Upload Your Resume</h1>
          <p className="upload-subtitle">
            Supported formats: PDF, DOCX
          </p>

          <div
            className={`dropzone ${isDragging ? 'active' : ''}`}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onClick={() => inputRef.current?.click()}
          >
            <span className="dropzone-icon">
              {file ? '\uD83D\uDCC4' : '\u2B06\uFE0F'}
            </span>
            {file ? (
              <>
                <h3>File selected</h3>
                <p>Click or drop to replace</p>
              </>
            ) : (
              <>
                <h3>Drag & drop your resume here</h3>
                <p>
                  or <span className="browse-link">browse files</span>
                </p>
              </>
            )}
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.docx"
              style={{ display: 'none' }}
              onChange={(e) => handleFile(e.target.files[0])}
            />
          </div>

          {file && (
            <div className="file-info">
              <span>\uD83D\uDCC4</span>
              <span className="file-name">{file.name}</span>
              <span className="file-size">{formatSize(file.size)}</span>
              <button
                className="remove-file"
                onClick={(e) => {
                  e.stopPropagation()
                  setFile(null)
                }}
              >
                &times;
              </button>
            </div>
          )}

          <div className="analyze-btn-wrapper">
            <button
              className="btn-primary analyze-btn"
              disabled={!file}
              onClick={handleAnalyze}
            >
              Analyze Resume &rarr;
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}
