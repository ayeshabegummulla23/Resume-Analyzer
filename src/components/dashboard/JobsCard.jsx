export default function JobsCard({ jobs }) {
  if (!jobs || jobs.length === 0) return null

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-icon amber">💼</div>
        <h2 className="card-title">Recommended Jobs</h2>
      </div>
      <div className="jobs-list">
        {jobs.map((j, i) => (
          <div className="job-item" key={i}>
            <div className="job-info">
              <h4>{j.title}</h4>
              <span>{j.company}</span>
            </div>
            <span className={`match-badge ${j.match >= 85 ? 'high' : 'medium'}`}>
              {j.match}% match
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
