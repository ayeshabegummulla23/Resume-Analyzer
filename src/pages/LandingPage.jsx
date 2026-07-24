import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import '../App.css'

const features = [
  {
    icon: '\u2601\uFE0F',
    title: 'ATS Score Analysis',
    desc: 'Get your resume scored against Applicant Tracking Systems used by top companies worldwide.',
  },
  {
    icon: '\uD83D\uDD0D',
    title: 'Skills Extraction',
    desc: 'AI identifies your key skills and maps them against in-demand technologies in your field.',
  },
  {
    icon: '\uD83D\uDCBC',
    title: 'Job Matching',
    desc: 'Receive personalized job recommendations that align with your experience and skill set.',
  },
  {
    icon: '\u26A0\uFE0F',
    title: 'Gap Detection',
    desc: 'Discover missing skills and qualifications that could strengthen your candidacy.',
  },
  {
    icon: '\uD83D\uDCC8',
    title: 'Career Insights',
    desc: 'Get a comprehensive summary of your professional profile with actionable improvements.',
  },
  {
    icon: '\u26A1',
    title: 'Instant Results',
    desc: 'Receive a full analysis in seconds. No waiting, no sign-up \u2014 just upload and go.',
  },
]

export default function LandingPage() {
  return (
    <div className="page">
      <div className="container">
        <Navbar />

        <section className="hero">
          <div className="hero-badge">AI-Powered Resume Analysis</div>
          <h1>
            Your Resume, <br />
            <span className="gradient-text">Optimized by AI</span>
          </h1>
          <p>
            Upload your resume and let CareerPilot AI analyze it against ATS systems,
            identify skill gaps, and match you with the best job opportunities.
          </p>
          <div className="hero-actions">
            <Link to="/upload" className="btn-primary">
              Upload Resume
              <span>&rarr;</span>
            </Link>
            <a href="#features" className="btn-secondary">
              Learn More
            </a>
          </div>
        </section>

        <section id="features" className="features">
          <h2>Everything You Need</h2>
          <p className="subtitle">
            Powerful AI tools to give your job search a competitive edge
          </p>
          <div className="features-grid">
            {features.map((f, i) => (
              <div className="feature-card" key={i}>
                <div className="feature-icon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <footer className="footer">
          &copy; {new Date().getFullYear()} CareerPilot AI. All rights reserved.
        </footer>
      </div>
    </div>
  )
}
