export default function CareerSummaryCard({ summary }) {
  if (!summary) return null

  const highlights = (summary.highlights || []).map((text, i) => ({
    text,
    color: ['blue', 'green', 'cyan'][i % 3],
  }))

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon purple">📝</div>
        <h2 className="card-title">Career Summary</h2>
      </div>
      <p className="summary-text">{summary.summary || 'No summary available.'}</p>
      {highlights.length > 0 && (
        <div className="summary-highlights">
          {highlights.map((h, i) => (
            <div className="highlight" key={i}>
              <span className={`highlight-dot ${h.color}`} />
              {h.text}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
