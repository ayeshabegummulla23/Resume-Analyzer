export default function Spinner() {
  return (
    <div className="spinner-overlay">
      <div className="spinner" />
      <p className="spinner-text">Analyzing your resume...</p>
      <p className="spinner-sub">
        Our AI is reviewing your skills, experience, and qualifications
      </p>
    </div>
  )
}
