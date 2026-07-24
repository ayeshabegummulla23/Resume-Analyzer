export default function CandidateCard({ candidate }) {
  if (!candidate) return null

  const details = [
    { label: 'Name', value: candidate.name || 'N/A' },
    { label: 'Email', value: candidate.email || 'N/A' },
    { label: 'Phone', value: candidate.phone || 'N/A' },
    { label: 'Education', value: candidate.education || 'N/A' },
    { label: 'Experience', value: candidate.experience || 'N/A' },
  ]

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon blue">👤</div>
        <h2 className="card-title">Candidate Details</h2>
      </div>
      <div className="candidate-details">
        {details.map((d) => (
          <div className="detail-row" key={d.label}>
            <span className="detail-label">{d.label}</span>
            <span className="detail-value">{d.value}</span>
          </div>
        ))}
        {candidate.projects && candidate.projects.length > 0 && (
          <div className="detail-row">
            <span className="detail-label">Projects</span>
            <span className="detail-value">
              {candidate.projects.join(', ')}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
