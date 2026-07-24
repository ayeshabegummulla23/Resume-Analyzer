import { useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import '../App.css'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Default form values so the user sees a pre-filled example
const defaults = {
  name: '',
  email: '',
  phone: '',
  skills: '',
  education: '',
  experience: '',
  job_role: '',
  tone: 'professional',
}

export default function CoverLetterPage() {
  // ── Form state ──
  const [form, setForm] = useState(defaults)
  // ── Generated letter text ──
  const [letter, setLetter] = useState('')
  // ── Loading & error states ──
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  // ── Copy feedback ──
  const [copied, setCopied] = useState(false)

  // Update a single field
  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  // Submit form to the backend
  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLetter('')
    setLoading(true)

    try {
      // Convert comma-separated skills string into an array
      const skillsArray = form.skills
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)

      const response = await fetch(`${API}/generate-cover-letter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          phone: form.phone,
          skills: skillsArray,
          education: form.education,
          experience: form.experience,
          job_role: form.job_role,
          tone: form.tone,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Generation failed')
      }

      setLetter(data.result.cover_letter)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Copy letter text to clipboard
  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(letter)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea')
      textarea.value = letter
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  // Download letter as a .txt file
  function handleDownload() {
    const blob = new Blob([letter], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `cover-letter-${form.name || 'candidate'}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="page coverletter-page">
      <div className="container">
        <Navbar />

        <div className="cl-header">
          <h1>Cover Letter Generator</h1>
          <p className="cl-subtitle">
            Generate a professional cover letter tailored to your target role
          </p>
        </div>

        <div className="cl-layout">
          {/* ── Left: Form ── */}
          <form className="cl-form card" onSubmit={handleSubmit}>
            <div className="cl-form-grid">
              <div className="field">
                <label htmlFor="name">Full Name *</label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  placeholder="John Doe"
                  value={form.name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="email">Email *</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="john@example.com"
                  value={form.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="phone">Phone *</label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  placeholder="+91 98765 43210"
                  value={form.phone}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="job_role">Target Job Role *</label>
                <input
                  id="job_role"
                  name="job_role"
                  type="text"
                  placeholder="Senior Frontend Developer"
                  value={form.job_role}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="field full-width">
                <label htmlFor="skills">
                  Skills <span className="hint">(comma-separated)</span>
                </label>
                <input
                  id="skills"
                  name="skills"
                  type="text"
                  placeholder="React, Python, SQL, Docker"
                  value={form.skills}
                  onChange={handleChange}
                />
              </div>

              <div className="field full-width">
                <label htmlFor="education">Education</label>
                <input
                  id="education"
                  name="education"
                  type="text"
                  placeholder="B.Tech Computer Science - IIT Delhi"
                  value={form.education}
                  onChange={handleChange}
                />
              </div>

              <div className="field full-width">
                <label htmlFor="experience">Experience</label>
                <textarea
                  id="experience"
                  name="experience"
                  rows="3"
                  placeholder="3 years as a full-stack developer at TechCorp..."
                  value={form.experience}
                  onChange={handleChange}
                />
              </div>

              <div className="field full-width">
                <label htmlFor="tone">Tone</label>
                <select
                  id="tone"
                  name="tone"
                  value={form.tone}
                  onChange={handleChange}
                >
                  <option value="professional">Professional</option>
                  <option value="enthusiastic">Enthusiastic</option>
                  <option value="concise">Concise</option>
                </select>
              </div>
            </div>

            {error && <p className="cl-error">{error}</p>}

            <button
              type="submit"
              className="btn-primary cl-generate-btn"
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Cover Letter'}
            </button>
          </form>

          {/* ── Right: Output ── */}
          <div className="cl-output card">
            <div className="card-header">
              <div className="card-icon purple">&#9998;</div>
              <h2 className="card-title">Your Cover Letter</h2>
            </div>

            {letter ? (
              <>
                <div className="cl-letter-box">
                  <pre className="cl-letter-text">{letter}</pre>
                </div>

                <div className="cl-actions">
                  <button
                    className="btn-secondary cl-action-btn"
                    onClick={handleCopy}
                  >
                    {copied ? 'Copied!' : 'Copy to Clipboard'}
                  </button>
                  <button
                    className="btn-primary cl-action-btn"
                    onClick={handleDownload}
                  >
                    Download as TXT
                  </button>
                </div>
              </>
            ) : (
              <div className="cl-placeholder">
                <p>
                  Fill in your details and click
                  <strong> Generate Cover Letter</strong> to see
                  the result here.
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="cl-footer-link">
          <Link to="/dashboard" className="btn-back">
            &larr; Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
