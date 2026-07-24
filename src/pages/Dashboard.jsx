import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import CandidateCard from '../components/dashboard/CandidateCard'
import ATSScoreCard from '../components/dashboard/ATSScoreCard'
import SkillsCard from '../components/dashboard/SkillsCard'
import JobsCard from '../components/dashboard/JobsCard'
import MissingSkillsCard from '../components/dashboard/MissingSkillsCard'
import CareerSummaryCard from '../components/dashboard/CareerSummaryCard'
import '../App.css'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const saved = localStorage.getItem('resumeData')
    if (saved) {
      setData(JSON.parse(saved))
    } else {
      // No data — redirect back to upload
      navigate('/upload')
    }
  }, [navigate])

  if (!data) return null

  return (
    <div className="page dashboard">
      <div className="container">
        <div className="dashboard-header">
          <h1>Analysis Dashboard</h1>
          <div className="dashboard-nav">
            <Link to="/cover-letter" className="btn-back">
              Cover Letter &#8594;
            </Link>
            <Link to="/upload" className="btn-back">
              &larr; Upload New Resume
            </Link>
          </div>
        </div>

        <div className="dashboard-grid">
          <CandidateCard candidate={data.candidate} />
          <ATSScoreCard ats={data.ats_score} />
          <SkillsCard skills={data.skills} />
          <JobsCard jobs={data.recommended_jobs} />
          <MissingSkillsCard missing={data.missing_skills} />
          <CareerSummaryCard summary={data.career_summary} />
        </div>
      </div>
    </div>
  )
}
