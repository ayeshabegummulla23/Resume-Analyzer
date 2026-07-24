# CareerPilot AI

AI-powered resume analyzer and cover letter generator. Upload a resume (PDF/DOCX), get an ATS score with breakdown, skill extraction, job matching, missing skills, and a career summary — all powered by Google Gemini with automatic regex fallback.

## Features

- **ATS Score** — Realistic score out of 100 with per-category feedback (formatting, keywords, structure, relevance)
- **Skill Extraction** — Automatic detection of technical skills, tools, and frameworks
- **Job Matching** — Top 4 job recommendations with match percentage
- **Missing Skills** — Identified gaps with priority levels (high / medium / low)
- **Career Summary** — AI-generated professional summary with highlights
- **Cover Letter Generator** — One-click cover letter in 3 tones (professional, enthusiastic, concise)
- **Regex Fallback** — Works fully offline if Gemini API key is not set

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, React Router 7, Vite 8 |
| Backend | FastAPI, Uvicorn |
| AI | Google Gemini 1.5 Flash |
| Parsing | PyPDF2 (PDF), python-docx (DOCX) |
| Styling | Vanilla CSS (dark theme, Inter font) |

## Project Structure

```
Resume Analyzer/
├── index.html                  # Vite entry HTML
├── package.json                # Node dependencies & scripts
├── vite.config.js              # Vite config (port 5173)
│
├── server/                     # FastAPI backend
│   ├── main.py                 # App init, CORS, routes
│   ├── parser.py               # PDF/DOCX text extraction
│   ├── analyzer.py             # AI analysis engine + regex fallback
│   ├── ai_client.py            # Gemini API client (cover letter)
│   ├── cover_letter.py         # Template-based cover letter generator
│   └── requirements.txt        # Python dependencies
│
└── src/                        # React frontend
    ├── main.jsx                # Entry point with BrowserRouter
    ├── App.jsx                 # Route definitions
    ├── App.css                 # All component styles
    ├── index.css               # CSS variables & reset
    ├── pages/
    │   ├── LandingPage.jsx     # Hero + features
    │   ├── UploadPage.jsx      # Drag-and-drop upload
    │   ├── Dashboard.jsx       # 6-card analysis grid
    │   └── CoverLetterPage.jsx # Cover letter form & output
    └── components/
        ├── Navbar.jsx
        ├── Spinner.jsx
        └── dashboard/
            ├── ATSScoreCard.jsx
            ├── CandidateCard.jsx
            ├── SkillsCard.jsx
            ├── JobsCard.jsx
            ├── MissingSkillsCard.jsx
            └── CareerSummaryCard.jsx
```

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **Google Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com/apikey)

## Setup

### 1. Backend

```bash
cd server

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set API key
set GEMINI_API_KEY=your_key_here    # Windows
# export GEMINI_API_KEY=your_key    # macOS/Linux

# Start server
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
# From project root
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and opens automatically in the browser.

> **Without a Gemini key:** The app still works — analysis falls back to regex-based extraction. No AI features, but all endpoints function.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check, reports AI status |
| `POST` | `/upload` | Upload PDF/DOCX, extracts text |
| `POST` | `/analyze` | Analyze last uploaded resume |
| `POST` | `/generate-cover-letter` | Generate cover letter from candidate details |

### POST /analyze — Response Shape

```json
{
  "status": "success",
  "results": {
    "candidate": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+91 98765 43210",
      "education": "B.Tech CS - IIT Delhi",
      "experience": "SDE at Google; Lead at Meta",
      "projects": ["Project Alpha", "Project Beta"]
    },
    "skills": ["python", "react", "sql", "docker"],
    "ats_score": {
      "overall": 78,
      "breakdown": {
        "formatting": 85,
        "keywords": 72,
        "structure": 80,
        "relevance": 75
      },
      "feedback": {
        "formatting": "Contact info is complete and well-formatted; bullet points improve readability.",
        "keywords": "Strong Python and React coverage but missing cloud platform keywords.",
        "structure": "All major sections present; projects section lacks descriptions.",
        "relevance": "Good ATS compatibility but no quantified achievements found."
      }
    },
    "recommended_jobs": [
      { "title": "Full Stack Engineer", "company": "StartupXYZ", "match": 85 }
    ],
    "missing_skills": [
      { "skill": "kubernetes", "priority": "high" }
    ],
    "career_summary": {
      "summary": "Software engineer with 5 years...",
      "highlights": ["5 years experience", "Python expert"],
      "years_of_experience": "5",
      "education": "B.Tech CS - IIT Delhi"
    }
  }
}
```

## How It Works

1. **Upload** — User drops a PDF or DOCX onto the upload zone
2. **Parse** — Backend extracts raw text using PyPDF2 or python-docx
3. **Analyze** — `analyzer.py` sends the text to Gemini with a structured prompt demanding valid JSON
4. **Validate** — Response is validated against the expected schema; every field has type checks
5. **Retry** — If Gemini returns invalid JSON or the API errors, it retries once
6. **Fallback** — If both attempts fail, regex-based extraction takes over (skills, ATS scoring, job matching, candidate details)
7. **Display** — Frontend renders 6 cards: candidate info, ATS score with feedback bars, skills, jobs, missing skills, career summary

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | No | Google Gemini API key. App works without it using regex fallback. |

## Notes

- **In-memory state** — The backend stores the last uploaded resume in a global variable. Not suitable for production multi-user use.
- **Hardcoded API URLs** — Frontend uses `http://127.0.0.1:8000` / `http://localhost:8000`. Change in `UploadPage.jsx` and `CoverLetterPage.jsx` if deploying elsewhere.
- **Legacy Flask app** — `app.py` at the root is an early prototype. The active backend is `server/main.py` (FastAPI).
