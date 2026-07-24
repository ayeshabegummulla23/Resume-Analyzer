"""
analyzer.py - Resume Analysis Engine (AI + Regex Fallback)

Primary analysis uses Google Gemini AI for accurate, context-aware
extraction of candidate details, skills, ATS scoring, job matching,
and career summaries.

If Gemini fails (invalid JSON, API error, timeout), the engine
retries once. If the retry also fails, it falls back to the
built-in regex-based analyzer so the app never crashes.

Public API:
    analyze_resume(text) -> dict   # Main entry point
    extract_candidate_details(text) -> dict  # Used by main.py
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────

logger = logging.getLogger("careerPilot.analyzer")


# ══════════════════════════════════════════════
# PART 1: GEMINI AI ANALYSIS
# ══════════════════════════════════════════════

# The exact JSON schema we demand from Gemini.
# This is embedded in the prompt so Gemini knows exactly
# what structure to return.

_GEMINI_SCHEMA = """{
  "candidate": {
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+91 98765 43210",
    "education": "Degree - Institution",
    "experience": "Job Title at Company; Job Title at Company",
    "projects": ["Project Name 1", "Project Name 2"]
  },
  "skills": ["python", "react", "sql"],
  "ats_score": {
    "overall": 75,
    "breakdown": {
      "formatting": 80,
      "keywords": 70,
      "structure": 75,
      "relevance": 72
    },
    "feedback": {
      "formatting": "One sentence explaining why formatting got this score.",
      "keywords": "One sentence explaining why keywords got this score.",
      "structure": "One sentence explaining why structure got this score.",
      "relevance": "One sentence explaining why relevance got this score."
    }
  },
  "recommended_jobs": [
    {"title": "Job Title", "company": "Company Name", "match": 85}
  ],
  "missing_skills": [
    {"skill": "Skill Name", "priority": "high"}
  ],
  "career_summary": {
    "summary": "2-3 sentence professional summary.",
    "highlights": ["strength1", "strength2", "strength3"],
    "years_of_experience": "5",
    "education": "B.Tech CS - IIT Delhi"
  }
}"""


def _build_gemini_prompt(resume_text: str) -> str:
    """
    Construct the prompt sent to Gemini.
    Instructs it to return ONLY valid JSON matching our schema.
    """
    return f"""You are an expert HR analyst and ATS (Applicant Tracking System) specialist.

Read the following resume carefully and extract ALL information.

Return a JSON object with EXACTLY this structure (no markdown, no code fences, no explanation):

{_GEMINI_SCHEMA}

RULES for each field:

candidate.name: Extract the person's full real name from the resume.
candidate.email: Extract the email address.
candidate.phone: Extract the phone number. If Indian, format as "+91 XXXXX XXXXX".
candidate.education: Extract the highest degree and institution (e.g. "B.Tech Computer Science - IIT Delhi").
candidate.experience: List job roles with companies separated by semicolons (e.g. "Senior Dev at Google; Lead Engineer at Meta").
candidate.projects: Array of project names only (no descriptions).

skills: Extract ALL technical skills, programming languages, frameworks, tools, and platforms. No duplicates. Lowercase.

ats_score - THIS IS THE MOST IMPORTANT SECTION. Score accurately based on REAL evaluation.

You must evaluate these 7 criteria from the resume, then MAP them to the 4 breakdown categories:

  1. FORMATTING evaluation (maps to breakdown.formatting):
     - Is contact info (email, phone) present and properly formatted?
     - Are there bullet points, consistent spacing, clean layout?
     - Is the resume free of typos and grammatical errors?
     - Score 90-100: Perfect formatting, all contact info, clean bullets
     - Score 70-89: Good formatting, minor issues
     - Score 50-69: Adequate but needs improvement
     - Score below 50: Poor formatting, missing info, messy layout

  2. KEYWORDS evaluation (maps to breakdown.keywords):
     - Are technical keywords relevant to the candidate's field present?
     - Does the resume use industry-standard terminology?
     - Are there enough skill keywords for ATS parsing?
     - Score 90-100: Rich, relevant keyword coverage
     - Score 70-89: Good keywords, some gaps
     - Score 50-69: Moderate keyword presence
     - Score below 50: Very few relevant keywords

  3. STRUCTURE evaluation (maps to breakdown.structure):
     - Are experience, education, skills, and projects sections present?
     - Is the information well-organized with clear section headers?
     - Does the resume follow a logical flow?
     - Also evaluate: experience quality, education completeness, project descriptions
     - Score 90-100: All sections present, well-organized, detailed
     - Score 70-89: Most sections present, good organization
     - Score 50-69: Some sections missing or poorly organized
     - Score below 50: Major sections missing, disorganized

  4. RELEVANCE evaluation (maps to breakdown.relevance):
     - Overall ATS compatibility score
     - Would this resume pass automated ATS screening?
     - Does the content depth match the candidate's stated experience level?
     - Are quantified achievements (numbers, percentages) present?
     - Score 90-100: Highly ATS-compatible, quantified, strong match
     - Score 70-89: Good ATS compatibility, mostly complete
     - Score 50-69: Moderate ATS compatibility, some issues
     - Score below 50: Poor ATS compatibility, likely filtered out

overall: Calculate as WEIGHTED AVERAGE:
  formatting (25%) + keywords (25%) + structure (25%) + relevance (25%)

feedback - Provide ONE clear, actionable sentence per category explaining WHY it got that score.
  - Be specific to THIS resume (not generic advice)
  - Mention what IS good and what NEEDS improvement
  - Example: "Contact info is present but phone number format is inconsistent; bullet points improve readability."

recommended_jobs: Exactly 4 job titles with realistic company names and match percentages (0-100). Sort by match highest first.

missing_skills: 5-8 important skills the candidate lacks that would strengthen their profile. Priority: "high", "medium", or "low".

career_summary.summary: Write a genuine 2-3 sentence professional summary based on the ACTUAL resume content. Be specific.
career_summary.highlights: 3-4 key strengths based on the ACTUAL resume.
career_summary.years_of_experience: Extract the number of years or estimate from context. Return as a string (e.g. "5") or "" if unknown.
career_summary.education: Extract education details as a string or "" if unknown.

IMPORTANT:
- Return ONLY the JSON object. Nothing else.
- No markdown formatting. No ```json fences. No explanation.
- If a value is not found, use "" (empty string) or [] (empty array).
- All skills must be lowercase and unique.
- ATS scores MUST be justified by the actual resume content. Do NOT give generic scores.

RESUME TEXT:
---
{resume_text[:10000]}
---"""


def _call_gemini(resume_text: str) -> Optional[dict]:
    """
    Send the resume to Gemini and attempt to parse the response
    as valid JSON.

    Returns the parsed dict on success, or None on failure.
    Does NOT raise exceptions — all errors are caught internally.
    """
    try:
        # Lazy import so the module works even if
        # google-generativeai isn't installed yet
        import google.generativeai as genai

        # Check if API is configured
        api_key = __import__("os").environ.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.info("GEMINI_API_KEY not set, skipping AI analysis")
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = _build_gemini_prompt(resume_text)
        response = model.generate_content(prompt)

        # Extract the raw text from the response
        raw = response.text.strip()

        # Strip markdown code fences if Gemini added them
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        # Parse JSON
        result = json.loads(raw)

        # Validate the structure
        return _validate_ai_result(result)

    except json.JSONDecodeError as e:
        logger.warning(f"Gemini returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.warning(f"Gemini API call failed: {e}")
        return None


def _validate_ai_result(result: dict) -> dict:
    """
    Ensure every expected key exists with the correct type.
    This prevents frontend crashes from partial AI responses.
    """
    candidate = result.get("candidate", {})
    ats = result.get("ats_score", {})
    breakdown = ats.get("breakdown", {})
    feedback = ats.get("feedback", {})
    summary = result.get("career_summary", {})

    return {
        "candidate": {
            "name": candidate.get("name", ""),
            "email": candidate.get("email", ""),
            "phone": candidate.get("phone", ""),
            "education": candidate.get("education", ""),
            "experience": candidate.get("experience", ""),
            "projects": candidate.get("projects", []) if isinstance(candidate.get("projects"), list) else [],
        },
        "skills": result.get("skills", []) if isinstance(result.get("skills"), list) else [],
        "ats_score": {
            "overall": ats.get("overall", 0) if isinstance(ats.get("overall"), (int, float)) else 0,
            "breakdown": {
                "formatting": breakdown.get("formatting", 0) if isinstance(breakdown.get("formatting"), (int, float)) else 0,
                "keywords": breakdown.get("keywords", 0) if isinstance(breakdown.get("keywords"), (int, float)) else 0,
                "structure": breakdown.get("structure", 0) if isinstance(breakdown.get("structure"), (int, float)) else 0,
                "relevance": breakdown.get("relevance", 0) if isinstance(breakdown.get("relevance"), (int, float)) else 0,
            },
            "feedback": {
                "formatting": feedback.get("formatting", "") if isinstance(feedback.get("formatting"), str) else "",
                "keywords": feedback.get("keywords", "") if isinstance(feedback.get("keywords"), str) else "",
                "structure": feedback.get("structure", "") if isinstance(feedback.get("structure"), str) else "",
                "relevance": feedback.get("relevance", "") if isinstance(feedback.get("relevance"), str) else "",
            },
        },
        "recommended_jobs": [
            {
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "match": j.get("match", 0) if isinstance(j.get("match"), (int, float)) else 0,
            }
            for j in (result.get("recommended_jobs", []) if isinstance(result.get("recommended_jobs"), list) else [])
        ],
        "missing_skills": [
            {
                "skill": m.get("skill", ""),
                "priority": m.get("priority", "low"),
            }
            for m in (result.get("missing_skills", []) if isinstance(result.get("missing_skills"), list) else [])
        ],
        "career_summary": {
            "summary": summary.get("summary", ""),
            "highlights": summary.get("highlights", []) if isinstance(summary.get("highlights"), list) else [],
            "years_of_experience": summary.get("years_of_experience", ""),
            "education": summary.get("education", ""),
        },
    }


def _analyze_with_gemini(text: str) -> Optional[dict]:
    """
    Try Gemini analysis with ONE retry.
    Returns the result dict on success, None on failure.
    """
    # First attempt
    result = _call_gemini(text)
    if result:
        logger.info("Gemini analysis succeeded on first attempt")
        return result

    # Retry once
    logger.info("Retrying Gemini analysis...")
    result = _call_gemini(text)
    if result:
        logger.info("Gemini analysis succeeded on retry")
        return result

    logger.warning("Gemini analysis failed after retry, will use regex fallback")
    return None


# ══════════════════════════════════════════════
# PART 2: REGEX-BASED FALLBACK ANALYZER
# ══════════════════════════════════════════════
# These functions are ONLY used when Gemini fails.
# They provide basic but functional analysis so the
# app never crashes.

TECH_SKILLS: List[str] = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin",
    "react", "angular", "vue.js", "next.js", "svelte", "html", "css", "sass", "tailwind",
    "node.js", "express", "django", "flask", "fastapi", "spring", "rails", "laravel",
    "sql", "nosql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
    "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
    "nlp", "computer vision", "data science", "data analysis",
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "github actions", "terraform", "ansible", "linux", "nginx",
    "git", "rest api", "graphql", "websocket",
    "agile", "scrum", "jira", "figma", "jest", "pytest", "selenium",
    "microservices", "system design", "design patterns",
]
TECH_SKILLS = list({s.lower().strip() for s in TECH_SKILLS})

JOB_TEMPLATES: List[Dict[str, Any]] = [
    {"title": "Senior Frontend Developer", "company": "TechCorp Inc.", "required_skills": ["javascript", "react", "typescript", "css", "html", "git", "rest api"]},
    {"title": "Full Stack Engineer", "company": "StartupXYZ", "required_skills": ["javascript", "react", "node.js", "sql", "git", "docker", "rest api"]},
    {"title": "Backend Developer", "company": "DataFlow Systems", "required_skills": ["python", "django", "sql", "rest api", "docker", "aws", "git"]},
    {"title": "Data Scientist", "company": "InsightAI Labs", "required_skills": ["python", "machine learning", "sql", "pandas", "numpy", "tensorflow", "data analysis"]},
    {"title": "DevOps Engineer", "company": "CloudScale Corp.", "required_skills": ["aws", "docker", "kubernetes", "ci/cd", "terraform", "linux", "python"]},
    {"title": "Software Engineer II", "company": "BigTech Labs", "required_skills": ["python", "java", "sql", "system design", "rest api", "git", "docker"]},
    {"title": "React Developer", "company": "Digital Agency Co.", "required_skills": ["react", "javascript", "typescript", "css", "html", "git", "rest api"]},
    {"title": "Machine Learning Engineer", "company": "NeuralNet Inc.", "required_skills": ["python", "machine learning", "deep learning", "pytorch", "tensorflow", "sql", "docker"]},
]


def _regex_extract_skills(text: str) -> List[str]:
    """Extract skills using regex pattern matching."""
    text_lower = text.lower()
    found = []
    for skill in TECH_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return sorted(set(found))


def _regex_compute_ats(text: str, skills: List[str]) -> Dict[str, Any]:
    """Compute ATS score using heuristic rules."""
    text_lower = text.lower()
    formatting = 0
    if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.\w+", text):
        formatting += 10
    if re.search(r"[\+]?\d[\d\s\-\(\)]{7,}", text):
        formatting += 8
    if len(text) > 300:
        formatting += 7
    if re.search(r"[•\-\*]\s", text):
        formatting += 5

    keywords = min(25, len(skills) * 4)
    sections = ["experience", "education", "skills", "summary", "objective", "projects", "certifications"]
    structure = min(25, sum(1 for kw in sections if kw in text_lower) * 5)
    word_count = len(text.split())
    relevance = 20 if word_count > 500 else 15 if word_count > 300 else 10 if word_count > 150 else 5
    overall = formatting + keywords + structure + relevance

    return {
        "overall": overall,
        "breakdown": {
            "formatting": formatting,
            "keywords": round(keywords * (100 / 25)),
            "structure": round(structure * (100 / 25)),
            "relevance": round(relevance * (100 / 20)),
        },
    }


def _regex_match_jobs(skills: List[str]) -> List[Dict[str, Any]]:
    """Match skills against job templates."""
    results = []
    for job in JOB_TEMPLATES:
        required = set(job["required_skills"])
        matched = required.intersection(set(skills))
        pct = round((len(matched) / len(required)) * 100) if required else 0
        results.append({"title": job["title"], "company": job["company"], "match": pct})
    results.sort(key=lambda j: j["match"], reverse=True)
    return results[:4]


def _regex_missing_skills(skills: List[str]) -> List[Dict[str, str]]:
    """Find missing skills from job templates."""
    freq: Dict[str, int] = {}
    for job in JOB_TEMPLATES:
        for s in job["required_skills"]:
            freq[s] = freq.get(s, 0) + 1
    candidate_set = {s.lower() for s in skills}
    missing = []
    for skill, f in freq.items():
        if skill not in candidate_set:
            priority = "high" if f >= 4 else "medium" if f >= 2 else "low"
            missing.append({"skill": skill, "priority": priority})
    order = {"high": 0, "medium": 1, "low": 2}
    missing.sort(key=lambda m: (order[m["priority"]], m["skill"]))
    return missing[:8]


def _regex_candidate_details(text: str) -> Dict[str, Any]:
    """Extract candidate details using regex."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    skip_words = {"resume", "cv", "curriculum vitae", "profile", "contact", "personal", "summary", "objective"}

    name = ""
    for line in lines[:5]:
        if line.lower().strip(":") in skip_words:
            continue
        if "@" in line or re.search(r"\d{5,}", line):
            continue
        name = line
        break

    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r"(\+91[\s\-]?)?\d{5}[\s\-]?\d{5}", text)
    phone = ""
    if phone_match:
        digits = re.sub(r"\D", "", phone_match.group(0))
        if len(digits) == 10:
            phone = f"+91 {digits[:5]} {digits[5:]}"
        elif len(digits) == 12 and digits.startswith("91"):
            phone = f"+91 {digits[2:7]} {digits[7:]}"
        else:
            phone = phone_match.group(0)

    text_lower = text.lower()
    education = ""
    edu_section = re.search(
        r"(?:education|academic)\s*(?:background| qualification)?\s*\n(.+?)(?:\n\s*\n|\n(?:experience|skills|projects|certifications|summary|objective)|$)",
        text_lower, re.DOTALL,
    )
    if edu_section:
        education = edu_section.group(1).strip()[:300]
    else:
        for kw in ["bachelor", "b.tech", "master", "m.tech", "mba", "ph.d", "phd"]:
            kw_match = re.search(rf"(.{{0,40}}\b{re.escape(kw)}\b.{{0,80}})", text_lower)
            if kw_match:
                education = text[max(0, kw_match.start(1)): kw_match.end(1)].strip()
                break

    experience_text = ""
    exp_section = re.search(
        r"(?:work\s+)?experience(?:\s+section)?\s*\n(.+?)(?:\n\s*\n|\n(?:education|skills|projects|certifications|summary|objective|awards)|$)",
        text_lower, re.DOTALL,
    )
    if exp_section:
        raw_exp = exp_section.group(1).strip()
        entries = []
        for ln in raw_exp.splitlines():
            ln = ln.strip()
            if not ln or len(ln) < 5:
                continue
            job_m = re.match(r"(.+?)\s*[|\-–]\s*(.+)", ln)
            if job_m:
                entries.append(f"{job_m.group(1).strip()} at {job_m.group(2).strip()}")
                continue
            at_m = re.match(r"(.+?)\s+at\s+(.+)", ln, re.IGNORECASE)
            if at_m:
                entries.append(f"{at_m.group(1).strip()} at {at_m.group(2).strip()}")
        experience_text = "; ".join(entries) if entries else raw_exp[:300]

    projects = []
    proj_section = re.search(
        r"projects?\s*\n(.+?)(?:\n\s*\n|\n(?:experience|skills|education|certifications|summary|objective|awards|references)|$)",
        text_lower, re.DOTALL,
    )
    if proj_section:
        for ln in proj_section.group(1).strip().splitlines():
            ln = ln.strip()
            if not ln or len(ln) < 3:
                continue
            cleaned = re.sub(r"^[\-\*•]\s*", "", ln)
            if not cleaned:
                continue
            name_m = re.match(r"^(.+?)\s+-\s+.+$", cleaned) or re.match(r"^(.+?)\s*[:|]\s+.+$", cleaned)
            if name_m and len(name_m.group(1).strip()) < 80:
                projects.append(name_m.group(1).strip())

    return {
        "candidate": {
            "name": name, "email": email, "phone": phone,
            "education": education, "experience": experience_text, "projects": projects,
        }
    }


def _regex_summary(text: str, skills: List[str]) -> Dict[str, Any]:
    """Generate career summary using regex extraction."""
    text_lower = text.lower()
    exp_match = re.search(r"(\d{1,2})\+?\s*years?\s*(of\s+)?experience", text_lower)
    years = str(int(exp_match.group(1))) if exp_match else ""

    edu_keywords = ["bachelor", "master", "ph.d", "phd", "b.s.", "m.s.", "mba", "b.tech", "m.tech"]
    education = ""
    for kw in edu_keywords:
        if kw in text_lower:
            idx = text_lower.index(kw)
            education = text[max(0, idx - 10): idx + 60].strip()
            break

    highlights = []
    if years:
        highlights.append(f"{years} years of professional experience")
    if skills:
        highlights.append(f"Proficient in {', '.join(skills[:5])}")
    if education:
        highlights.append(f"Education: {education}")
    if not highlights:
        highlights.append("Strong technical background")

    skill_list = ", ".join(skills[:6]) if skills else "various technologies"
    summary_text = (
        f"A driven professional with expertise in {skill_list}. "
        f"Demonstrated ability to deliver high-quality work across "
        f"multiple projects. Looking to leverage technical skills "
        f"and experience in a challenging new role."
    )

    return {
        "summary": summary_text,
        "highlights": highlights,
        "years_of_experience": years,
        "education": education,
    }


def _analyze_with_regex(text: str) -> dict:
    """
    Complete analysis using only regex heuristics.
    This is the fallback that runs when Gemini is unavailable.
    """
    logger.info("Running regex-based fallback analysis")
    candidate = _regex_candidate_details(text)
    skills = _regex_extract_skills(text)
    ats = _regex_compute_ats(text, skills)
    jobs = _regex_match_jobs(skills)
    missing = _regex_missing_skills(skills)
    summary = _regex_summary(text, skills)

    return {
        "candidate": candidate["candidate"],
        "skills": skills,
        "ats_score": ats,
        "recommended_jobs": jobs,
        "missing_skills": missing,
        "career_summary": summary,
    }


# ══════════════════════════════════════════════
# PART 3: PUBLIC API
# ══════════════════════════════════════════════

def analyze_resume(text: str) -> dict:
    """
    Main entry point. Runs the full analysis pipeline.

    Priority:
      1. Gemini AI (with one retry)
      2. Regex fallback (never fails)

    Returns a dict matching the exact structure the React
    frontend expects.
    """
    # Try Gemini first
    ai_result = _analyze_with_gemini(text)
    if ai_result:
        logger.info("Analysis completed using Gemini AI")
        return ai_result

    # Fall back to regex
    logger.info("Analysis completed using regex fallback")
    return _analyze_with_regex(text)


def extract_candidate_details(text: str) -> Dict[str, Any]:
    """
    Extract candidate details only.
    Used by main.py for the cover letter endpoint.
    Tries Gemini first, falls back to regex.
    """
    # Try Gemini for just the candidate section
    ai_result = _analyze_with_gemini(text)
    if ai_result and "candidate" in ai_result:
        return {"candidate": ai_result["candidate"]}

    # Regex fallback
    return _regex_candidate_details(text)
