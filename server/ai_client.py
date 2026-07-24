"""
ai_client.py - Gemini API Client

Wraps the Google Gemini API (free tier) for:
  - Resume analysis (skills, ATS scoring, job matching)
  - Cover letter generation

Setup:
  1. Get a free API key from https://aistudio.google.com/apikey
  2. Set it as GEMINI_API_KEY environment variable, or
     pass it directly when creating the client.

Free tier: 15 requests/minute, 1M tokens/day (gemini-1.5-flash).
"""

import os
import json
import google.generativeai as genai


# ──────────────────────────────────────────────
# 1. CONFIGURATION
# ──────────────────────────────────────────────

def configure_api(api_key: str = None) -> None:
    """
    Set up the Gemini API key.
    Priority: parameter > environment variable.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise ValueError(
            "Gemini API key not found. Set GEMINI_API_KEY "
            "environment variable or pass api_key parameter."
        )
    genai.configure(api_key=key)


def get_model():
    """
    Return a configured Gemini 1.5 Flash model instance.
    Flash is the fastest and cheapest model (free tier friendly).
    """
    return genai.GenerativeModel("gemini-1.5-flash")


# ──────────────────────────────────────────────
# 2. RESUME ANALYSIS
# ──────────────────────────────────────────────

def analyze_resume_with_ai(resume_text: str) -> dict:
    """
    Send the resume text to Gemini and get a structured
    JSON analysis back.

    Returns the same shape as the rule-based analyzer
    so the frontend doesn't need to change.
    """
    model = get_model()

    prompt = f"""You are an expert HR analyst and ATS (Applicant Tracking System) specialist.

Analyze the following resume text and return a JSON object with EXACTLY this structure:

{{
  "skills": ["skill1", "skill2"],
  "ats_score": {{
    "overall": 75,
    "breakdown": {{
      "formatting": 80,
      "keywords": 70,
      "structure": 75,
      "relevance": 72
    }}
  }},
  "recommended_jobs": [
    {{"title": "Job Title", "company": "Company Name", "match": 85}}
  ],
  "missing_skills": [
    {{"skill": "Skill Name", "priority": "high"}}
  ],
  "career_summary": {{
    "summary": "A 2-3 sentence professional summary of the candidate.",
    "highlights": ["highlight1", "highlight2", "highlight3"],
    "years_of_experience": 3,
    "education": "degree info if found"
  }}
}}

RULES:
- skills: Extract ALL technical skills, tools, frameworks, and programming languages mentioned. No duplicates.
- ats_score.overall: Score 0-100 based on formatting, keywords, section structure, and content depth.
- ats_score.breakdown: Score each category 0-100.
- recommended_jobs: Suggest exactly 4 job roles that match this candidate's skills. Include realistic company names. Sort by match percentage (highest first).
- missing_skills: List 5-8 important skills the candidate is missing that would improve their profile. Mark priority as "high", "medium", or "low".
- career_summary.summary: Write a genuine 2-3 sentence summary based on the actual resume content.
- career_summary.highlights: 3-4 key strengths based on the actual resume.
- career_summary.years_of_experience: Extract from resume or estimate from context. Use null if unknown.
- career_summary.education: Extract education details or use null.

IMPORTANT: Return ONLY valid JSON. No markdown, no explanation, no code fences.

Resume text:
---
{resume_text[:8000]}
---
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if the AI wrapped the JSON
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        # Parse the JSON response
        result = json.loads(text)

        # Validate and sanitize the result
        return _sanitize_analysis(result)

    except json.JSONDecodeError:
        # If Gemini returns malformed JSON, fall back gracefully
        return None
    except Exception:
        return None


def _sanitize_analysis(result: dict) -> dict:
    """
    Ensure all expected keys exist and have correct types.
    Prevents frontend crashes from partial AI responses.
    """
    return {
        "skills": result.get("skills", []),
        "ats_score": {
            "overall": result.get("ats_score", {}).get("overall", 0),
            "breakdown": {
                "formatting": result.get("ats_score", {}).get("breakdown", {}).get("formatting", 0),
                "keywords": result.get("ats_score", {}).get("breakdown", {}).get("keywords", 0),
                "structure": result.get("ats_score", {}).get("breakdown", {}).get("structure", 0),
                "relevance": result.get("ats_score", {}).get("breakdown", {}).get("relevance", 0),
            },
        },
        "recommended_jobs": result.get("recommended_jobs", []),
        "missing_skills": result.get("missing_skills", []),
        "career_summary": {
            "summary": result.get("career_summary", {}).get("summary", ""),
            "highlights": result.get("career_summary", {}).get("highlights", []),
            "years_of_experience": result.get("career_summary", {}).get("years_of_experience"),
            "education": result.get("career_summary", {}).get("education"),
        },
    }


# ──────────────────────────────────────────────
# 3. COVER LETTER GENERATION
# ──────────────────────────────────────────────

def generate_cover_letter_with_ai(
    name: str,
    email: str,
    phone: str,
    skills: list,
    education: str,
    experience: str,
    job_role: str,
    tone: str = "professional",
) -> str:
    """
    Generate a professional cover letter using Gemini.
    Returns the full cover letter text.
    """
    model = get_model()

    skill_text = ", ".join(skills) if skills else "various technologies"

    prompt = f"""Write a professional cover letter for the following candidate.

CANDIDATE DETAILS:
- Name: {name}
- Email: {email}
- Phone: {phone}
- Education: {education or 'Not specified'}
- Experience: {experience or 'Not specified'}
- Skills: {skill_text}

TARGET ROLE: {job_role}

TONE: {tone}

RULES:
- Write a complete, professional cover letter (300-400 words).
- Include: greeting, introduction, skills & experience paragraph, why they're a good fit, and closing.
- Make it sound genuine and specific to this candidate's actual profile.
- Do NOT use placeholder text or generic filler.
- Format with the candidate's contact info at the top, followed by the letter body.
- End with "Sincerely," followed by the candidate's name.

Return ONLY the cover letter text. No JSON, no markdown, no code fences."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return None
