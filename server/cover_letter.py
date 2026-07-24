"""
cover_letter.py - Cover Letter Generator

Generates professional cover letters using rule-based templates.
No AI APIs needed - just string formatting with predefined patterns.

Each template targets a different tone:
  - professional : formal corporate language
  - enthusiastic : energetic and passionate
  - concise     : short and to the point

The generator fills in candidate details and job-specific content
automatically.
"""

from typing import Dict, List, Any


# ──────────────────────────────────────────────
# 1. TEMPLATE COMPONENTS
# ──────────────────────────────────────────────
# Break the cover letter into reusable pieces so we can
# mix and match without duplicating entire paragraphs.

# ── Greetings ─────────────────────────────────
GREETINGS: Dict[str, str] = {
    "professional": "Dear Hiring Manager,",
    "enthusiastic": "Dear Hiring Team,",
    "concise": "Dear Hiring Manager,",
}

# ── Introduction paragraphs ───────────────────
# {name}, {job_role}, {education} are filled in at runtime.
INTRODUCTIONS: Dict[str, str] = {
    "professional": (
        "I am writing to express my strong interest in the {job_role} "
        "position. With a background in {education} and hands-on "
        "experience in my field, I am confident in my ability to "
        "contribute meaningfully to your team."
    ),
    "enthusiastic": (
        "I am thrilled to apply for the {job_role} role. As a "
        "passionate {education} graduate with real-world project "
        "experience, I am eager to bring my energy and skills to "
        "your organization."
    ),
    "concise": (
        "I am interested in the {job_role} position. My {education} "
        "background and practical experience make me a strong "
        "candidate for this role."
    ),
}

# ── Skills & experience paragraphs ────────────
# {skill_list} and {experience} are filled in at runtime.
SKILLS_PARAGRAPHS: Dict[str, str] = {
    "professional": (
        "Throughout my career, I have developed strong proficiency "
        "in {skill_list}. {experience_context} These experiences "
        "have equipped me with both the technical depth and "
        "problem-solving mindset needed to excel in this role."
    ),
    "enthusiastic": (
        "I have worked extensively with {skill_list}, and I genuinely "
        "enjoy building solutions with these technologies. "
        "{experience_context} Every project has sharpened my "
        "ability to learn quickly and deliver results."
    ),
    "concise": (
        "My key skills include {skill_list}. {experience_context} "
        "I am comfortable working in fast-paced environments and "
        "adapting to new challenges."
    ),
}

# ── "Why suitable" paragraphs ─────────────────
# {job_role} and {company} are filled in at runtime.
WHY_SUITABLE: Dict[str, str] = {
    "professional": (
        "I am particularly drawn to {company} because of your "
        "commitment to innovation and excellence. I believe my "
        "skills align well with the requirements of the {job_role} "
        "role, and I am excited about the opportunity to contribute "
        "to your team's success."
    ),
    "enthusiastic": (
        "What excites me most about {company} is the chance to "
        "work alongside talented people on impactful {job_role} "
        "projects. I am confident that my passion and skill set "
        "would make me a valuable addition to your team."
    ),
    "concise": (
        "I believe my experience and skills are a strong match "
        "for the {job_role} role at {company}. I am ready to "
        "contribute from day one."
    ),
}

# ── Closing paragraphs ────────────────────────
CLOSINGS: Dict[str, str] = {
    "professional": (
        "Thank you for considering my application. I would welcome "
        "the opportunity to discuss how my background, skills, and "
        "enthusiasm align with the goals of your team. I look "
        "forward to hearing from you."
    ),
    "enthusiastic": (
        "Thank you so much for your time and consideration. I would "
        "love the chance to discuss this exciting opportunity further. "
        "I am looking forward to the possibility of joining your "
        "team!"
    ),
    "concise": (
        "Thank you for your time. I look forward to discussing "
        "how I can contribute to {company}."
    ),
}


# ──────────────────────────────────────────────
# 2. HELPER FUNCTIONS
# ──────────────────────────────────────────────

def _format_skills(skills_list: List[str]) -> str:
    """
    Convert a list of skills into a natural-language string.

    ["Python", "React", "SQL"]  →  "Python, React, and SQL"
    ["Git"]                     →  "Git"
    []                          →  "relevant technologies"
    """
    if not skills_list:
        return "relevant technologies"

    # Title-case each skill for readability
    formatted = [s.title() for s in skills_list]

    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"

    # Oxford comma: "A, B, and C"
    return ", ".join(formatted[:-1]) + f", and {formatted[-1]}"


def _build_experience_context(experience: str) -> str:
    """
    Turn the raw experience string into a sentence fragment
    suitable for embedding in a paragraph.

    If experience is empty, return a generic fallback.
    """
    if not experience or not experience.strip():
        return "Through various projects and internships,"

    # Capitalise the first letter
    exp = experience.strip()
    return f"In my experience, {exp[0].lower() + exp[1:]} has given me practical insight into real-world development."


# ──────────────────────────────────────────────
# 3. MAIN GENERATOR
# ──────────────────────────────────────────────

def generate_cover_letter(
    name: str,
    email: str,
    phone: str,
    skills: List[str],
    education: str,
    experience: str,
    job_role: str,
    tone: str = "professional",
) -> Dict[str, Any]:
    """
    Assemble a full cover letter from template parts.

    Args:
        name:        Candidate's full name.
        email:       Candidate's email address.
        phone:       Candidate's phone number.
        skills:      List of technical skills.
        education:   Education string (e.g. "B.Tech Computer Science").
        experience:  Experience description string.
        job_role:    Target job title.
        tone:        One of "professional", "enthusiastic", "concise".

    Returns:
        {
            "cover_letter": str,   # The full formatted letter
            "tone": str,
            "job_role": str,
        }
    """
    # Validate tone, fall back to professional
    if tone not in GREETINGS:
        tone = "professional"

    # Format the skill list into a readable string
    skill_text = _format_skills(skills)

    # Build the experience context sentence
    exp_context = _build_experience_context(experience)

    # Get the company name from the job role if possible,
    # otherwise use a generic placeholder
    company = "your organization"

    # ── Assemble each section ────────────────
    greeting = GREETINGS[tone]

    introduction = INTRODUCTIONS[tone].format(
        job_role=job_role,
        education=education or "computer science",
    )

    skills_para = SKILLS_PARAGRAPHS[tone].format(
        skill_list=skill_text,
        experience_context=exp_context,
    )

    suitable = WHY_SUITABLE[tone].format(
        job_role=job_role,
        company=company,
    )

    closing = CLOSINGS[tone].format(company=company)

    # ── Put it all together ──────────────────
    # Use double newlines between paragraphs for standard
    # business letter formatting.
    cover_letter = (
        f"{name}\n"
        f"{email} | {phone}\n"
        f"\n"
        f"{greeting}\n"
        f"\n"
        f"{introduction}\n"
        f"\n"
        f"{skills_para}\n"
        f"\n"
        f"{suitable}\n"
        f"\n"
        f"{closing}\n"
        f"\n"
        f"Sincerely,\n"
        f"{name}"
    )

    return {
        "cover_letter": cover_letter,
        "tone": tone,
        "job_role": job_role,
    }
