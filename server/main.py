"""
main.py - CareerPilot AI Backend

FastAPI application that exposes endpoints:
  GET  /health               → Liveness check
  POST /upload               → Accept resume file (PDF/DOCX)
  POST /analyze              → AI-powered resume analysis
  POST /generate-cover-letter → AI-powered cover letter

Uses Google Gemini API (free tier) for real AI analysis.

Run with:
    set GEMINI_API_KEY=your_key_here
    uvicorn main:app --reload --port 8000
"""

import os
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parser import extract_text
from analyzer import analyze_resume, extract_candidate_details
from ai_client import generate_cover_letter_with_ai


# ──────────────────────────────────────────────
# 1. APP INITIALISATION
# ──────────────────────────────────────────────

app = FastAPI(
    title="CareerPilot AI",
    version="2.0.0",
    description="AI-powered resume analysis backend using Gemini",
)


# ──────────────────────────────────────────────
# 2. CORS MIDDLEWARE
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# 3. STARTUP: Configure Gemini API
# ──────────────────────────────────────────────

@app.on_event("startup")
def startup():
    """Log startup status."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        print("[CareerPilot] Gemini API key detected - AI analysis enabled")
    else:
        print("[CareerPilot] WARNING: GEMINI_API_KEY not set. Using regex fallback.")
        print("  Set it with: set GEMINI_API_KEY=your_key")


# ──────────────────────────────────────────────
# 4. IN-MEMORY STATE
# ──────────────────────────────────────────────

_last_resume_text: Optional[str] = None


# ──────────────────────────────────────────────
# 5. REQUEST MODELS
# ──────────────────────────────────────────────

class CoverLetterRequest(BaseModel):
    name: str
    email: str
    phone: str
    skills: list[str]
    education: str
    experience: str
    job_role: str
    tone: str = "professional"


# ──────────────────────────────────────────────
# 6. ROUTES
# ──────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Liveness probe."""
    api_key_set = bool(os.environ.get("GEMINI_API_KEY"))
    return {
        "status": "healthy",
        "service": "CareerPilot AI",
        "version": "2.0.0",
        "ai_enabled": api_key_set,
    }


@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF/DOCX). Extracts text and stores
    it in memory for the /analyze endpoint.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    allowed = (".pdf", ".docx")
    if not file.filename.lower().endswith(allowed):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed)}",
        )

    global _last_resume_text

    try:
        file_bytes = await file.read()
        text = extract_text(file_bytes, file.filename)

        if text is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse the file. It may be empty or corrupted.",
            )

        if len(text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="The file appears to be empty or contains too little text.",
            )

        _last_resume_text = text

        return {
            "status": "success",
            "message": "Resume uploaded and parsed successfully",
            "filename": file.filename,
            "characters_extracted": len(text),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/analyze")
def analyze_resume_endpoint():
    """
    Analyze the last uploaded resume.
    analyze_resume() tries Gemini AI first, then falls back
    to the regex-based local analyzer automatically.
    """
    global _last_resume_text

    if _last_resume_text is None:
        raise HTTPException(
            status_code=400,
            detail="No resume uploaded yet. Please call POST /upload first.",
        )

    try:
        results = analyze_resume(_last_resume_text)
        return {"status": "success", "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/generate-cover-letter")
def generate_cover_letter_endpoint(req: CoverLetterRequest):
    """
    Generate a cover letter using Gemini AI.
    Falls back to template-based generation if API key is not set.
    """
    if not req.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    if not req.job_role.strip():
        raise HTTPException(status_code=400, detail="Job role is required")

    try:
        # Try AI-powered generation first
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            letter = generate_cover_letter_with_ai(
                name=req.name.strip(),
                email=req.email.strip(),
                phone=req.phone.strip(),
                skills=req.skills,
                education=req.education.strip(),
                experience=req.experience.strip(),
                job_role=req.job_role.strip(),
                tone=req.tone,
            )
            if letter:
                return {
                    "status": "success",
                    "result": {
                        "cover_letter": letter,
                        "tone": req.tone,
                        "job_role": req.job_role,
                    },
                }

        # Fallback to template-based generation
        from cover_letter import generate_cover_letter
        result = generate_cover_letter(
            name=req.name.strip(),
            email=req.email.strip(),
            phone=req.phone.strip(),
            skills=req.skills,
            education=req.education.strip(),
            experience=req.experience.strip(),
            job_role=req.job_role.strip(),
            tone=req.tone,
        )
        return {"status": "success", "result": result}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cover letter generation failed: {str(e)}",
        )
