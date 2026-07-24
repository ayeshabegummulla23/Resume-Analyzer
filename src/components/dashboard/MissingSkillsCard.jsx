export default function MissingSkillsCard({ missing }) {
  if (!missing || missing.length === 0) return null

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon red">⚠️</div>
        <h2 className="card-title">Missing Skills</h2>
      </div>
      <div className="missing-list">
        {missing.map((m) => (
          <div className="missing-item" key={m.skill}>
            <span className="skill-name">{m.skill}</span>
            <span className={`priority ${m.priority}`}>{m.priority}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
