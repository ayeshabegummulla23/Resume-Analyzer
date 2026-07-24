export default function SkillsCard({ skills }) {
  if (!skills || skills.length === 0) return null

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon green">🛠️</div>
        <h2 className="card-title">Skills Identified</h2>
      </div>
      <div className="skills-list">
        {skills.map((s) => (
          <span className="skill-tag" key={s}>{s}</span>
        ))}
      </div>
    </div>
  )
}
