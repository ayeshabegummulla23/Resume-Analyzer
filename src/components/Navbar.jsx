import { Link } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="logo">
        <div className="logo-icon">CP</div>
        CareerPilot AI
      </Link>
      <div className="nav-links">
        <a href="#features">Features</a>
        <Link to="/upload">Upload Resume</Link>
      </div>
    </nav>
  )
}
