export default function ATSScoreCard({ ats }) {
  if (!ats) return null

  const score = ats.overall || 0
  const circumference = 2 * Math.PI * 60
  const offset = circumference - (score / 100) * circumference

  const ringClass = score >= 70 ? '' : score >= 50 ? 'orange' : 'red'

  // Build breakdown array from the ats.breakdown object
  const raw = ats.breakdown || {}
  const fb = ats.feedback || {}
  const breakdown = [
    { label: 'Formatting', value: raw.formatting || 0, tip: fb.formatting || '' },
    { label: 'Keywords', value: raw.keywords || 0, tip: fb.keywords || '' },
    { label: 'Structure', value: raw.structure || 0, tip: fb.structure || '' },
    { label: 'Relevance', value: raw.relevance || 0, tip: fb.relevance || '' },
  ]

  // Pick bar color based on value
  function barColor(val) {
    if (val >= 70) return 'green'
    if (val >= 50) return 'amber'
    return 'red'
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon cyan">📊</div>
        <h2 className="card-title">ATS Score</h2>
      </div>
      <div className="ats-score-center">
        <div className="score-ring">
          <svg viewBox="0 0 140 140">
            <circle className="ring-bg" cx="70" cy="70" r="60" />
            <circle
              className={`ring-fill ${ringClass}`}
              cx="70"
              cy="70"
              r="60"
              style={{ strokeDashoffset: offset }}
            />
          </svg>
          <div className="score-value">{score}</div>
        </div>
        <span className="score-label">out of 100</span>
        <div className="ats-breakdown">
          {breakdown.map((b) => (
            <div className="breakdown-item" key={b.label}>
              <span className="label">{b.label}</span>
              <div className="breakdown-bar">
                <div
                  className={`fill ${barColor(b.value)}`}
                  style={{ width: `${b.value}%` }}
                />
              </div>
              <span>{b.value}%</span>
              {b.tip && (
                <span className="breakdown-feedback">{b.tip}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
