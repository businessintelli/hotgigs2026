import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from agents.base_agent import BaseAgent
from config import settings

logger = logging.getLogger(__name__)


class ResumeTailoringAgent(BaseAgent):
    """Agent for tailoring resumes to job descriptions using AI-powered rewriting."""

    def __init__(self):
        """Initialize the resume tailoring agent."""
        super().__init__(agent_name="ResumeTailoringAgent", agent_version="1.0.0")
        self.anthropic_api_key = settings.anthropic_api_key

    async def on_start(self) -> None:
        """Initialize resume tailoring agent."""
        logger.info("Resume Tailoring Agent started")

    async def on_stop(self) -> None:
        """Cleanup resume tailoring agent resources."""
        logger.info("Resume Tailoring Agent stopped")

    def extract_keywords_from_jd(self, job_description: str) -> Dict[str, List[str]]:
        """
        Extract key information from job description.

        Args:
            job_description: Full job description text

        Returns:
            Dictionary with extracted keywords by category
        """
        keywords = {
            "hard_skills": [],
            "soft_skills": [],
            "tools": [],
            "experience_keywords": [],
            "responsibilities": [],
            "achievements": [],
        }

        text_lower = job_description.lower()

        # Common hard skills patterns
        hard_skills_patterns = [
            r"\b(python|javascript|java|c\+\+|sql|ruby|php|go|rust|scala|kotlin)\b",
            r"\b(react|angular|vue|node\.?js?|express|django|flask|spring)\b",
            r"\b(aws|azure|gcp|google cloud|docker|kubernetes|jenkins)\b",
            r"\b(machine learning|deep learning|tensorflow|pytorch|ai|nlp)\b",
            r"\b(rest api|graphql|soap|microservices|distributed systems)\b",
        ]

        for pattern in hard_skills_patterns:
            matches = re.findall(pattern, text_lower)
            keywords["hard_skills"].extend(matches)

        # Common soft skills patterns
        soft_skills_patterns = [
            r"\b(communication|leadership|collaboration|problem.?solving|analytical)\b",
            r"\b(team.*?work|interpersonal|attention to detail|time management)\b",
            r"\b(critical thinking|creativity|adaptability|initiative)\b",
        ]

        for pattern in soft_skills_patterns:
            matches = re.findall(pattern, text_lower)
            keywords["soft_skills"].extend(matches)

        # Remove duplicates and keep unique
        keywords["hard_skills"] = list(set(keywords["hard_skills"]))
        keywords["soft_skills"] = list(set(keywords["soft_skills"]))

        return keywords

    def analyze_keyword_gaps(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:
        """
        Analyze keyword gaps between resume and job description.

        Args:
            resume_text: Parsed resume text
            job_description: Job description text

        Returns:
            Dictionary with gap analysis
        """
        jd_keywords = self.extract_keywords_from_jd(job_description)
        resume_lower = resume_text.lower()

        gaps = {
            "missing_hard_skills": [],
            "missing_soft_skills": [],
            "covered_hard_skills": [],
            "covered_soft_skills": [],
            "keyword_density": 0.0,
            "total_jd_keywords": 0,
            "matched_keywords": 0,
        }

        # Check hard skills coverage
        for skill in jd_keywords["hard_skills"]:
            if skill.lower() in resume_lower:
                gaps["covered_hard_skills"].append(skill)
            else:
                gaps["missing_hard_skills"].append(skill)

        # Check soft skills coverage
        for skill in jd_keywords["soft_skills"]:
            if skill.lower() in resume_lower:
                gaps["covered_soft_skills"].append(skill)
            else:
                gaps["missing_soft_skills"].append(skill)

        gaps["total_jd_keywords"] = len(jd_keywords["hard_skills"]) + len(jd_keywords["soft_skills"])
        gaps["matched_keywords"] = len(gaps["covered_hard_skills"]) + len(gaps["covered_soft_skills"])

        if gaps["total_jd_keywords"] > 0:
            gaps["keyword_density"] = round((gaps["matched_keywords"] / gaps["total_jd_keywords"]) * 100, 1)

        return gaps

    async def generate_tailored_resume(
        self,
        resume_text: str,
        job_description: str,
        candidate_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI-tailored resume using Claude API.

        Uses Anthropic Claude to intelligently rewrite resume bullets
        and reorganize experience for better alignment with JD.

        Args:
            resume_text: Original resume text
            job_description: Target job description
            candidate_name: Candidate name (for context)

        Returns:
            Dictionary with tailored resume and metadata
        """
        if not self.anthropic_api_key:
            logger.warning("Anthropic API key not configured, returning analysis only")
            return {
                "original_resume": resume_text,
                "tailored_resume": None,
                "error": "Anthropic API key not configured",
                "analysis": self.analyze_keyword_gaps(resume_text, job_description),
            }

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.anthropic_api_key)

            prompt = f"""You are an expert resume writer and HR consultant. Your task is to tailor a resume to better match a specific job description.

IMPORTANT: The tailoring must be TRUTHFUL and not add false information. Only emphasize and reorganize existing skills and experiences.

Original Resume:
{resume_text}

---

Target Job Description:
{job_description}

---

Please:
1. Analyze the job description to identify key skills, responsibilities, and achievements valued
2. Reorder work experience bullets to emphasize relevance to the job
3. Rewrite achievement bullets to highlight keywords from the JD (only if truthfully applicable)
4. Emphasize any transferable skills that match the JD requirements
5. Suggest where missing skills/keywords could be truthfully added

Return the response in this format:
[TAILORED_RESUME]
{resume_text}
[/TAILORED_RESUME]

[ANALYSIS]
- Key matches: [list of skills/experiences that align well]
- Missing skills: [list of JD requirements not in resume]
- Recommendations: [how to better position existing experience]
[/ANALYSIS]

[KEYWORDS_ADDED]
[list of important JD keywords now emphasized in tailored resume]
[/KEYWORDS_ADDED]"""

            message = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Parse response sections
            tailored_resume = self._extract_section(response_text, "TAILORED_RESUME")
            analysis = self._extract_section(response_text, "ANALYSIS")
            keywords_added = self._extract_section(response_text, "KEYWORDS_ADDED")

            gap_analysis = self.analyze_keyword_gaps(resume_text, job_description)

            return {
                "original_resume": resume_text,
                "tailored_resume": tailored_resume or resume_text,
                "analysis": analysis,
                "keywords_added": keywords_added,
                "gap_analysis": gap_analysis,
                "generated_at": datetime.utcnow().isoformat(),
                "model": "claude-opus-4-6",
            }

        except Exception as e:
            logger.error(f"Error generating tailored resume: {str(e)}")
            return {
                "original_resume": resume_text,
                "tailored_resume": None,
                "error": f"Error generating tailored resume: {str(e)}",
                "analysis": self.analyze_keyword_gaps(resume_text, job_description),
            }

    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract a marked section from response text."""
        pattern = f"\\[{section_name}\\](.*?)\\[/{section_name}\\]"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else None

    def calculate_ats_compatibility_score(self, resume_text: str) -> Dict[str, Any]:
        """
        Calculate ATS compatibility score for a resume.

        Checks:
        - Keyword density
        - Format validation
        - Section structure
        - Readability metrics

        Args:
            resume_text: Resume text to analyze

        Returns:
            Dictionary with ATS score (0-100) and detailed breakdown
        """
        score_components = {
            "formatting": self._score_formatting(resume_text),
            "keywords": self._score_keywords(resume_text),
            "structure": self._score_structure(resume_text),
            "length": self._score_length(resume_text),
            "readability": self._score_readability(resume_text),
        }

        # Weighted average
        weights = {
            "formatting": 0.25,
            "keywords": 0.25,
            "structure": 0.20,
            "length": 0.15,
            "readability": 0.15,
        }

        overall_score = sum(score_components[k] * weights[k] for k in score_components)

        return {
            "overall_score": round(overall_score, 1),
            "max_score": 100,
            "components": {k: round(v, 1) for k, v in score_components.items()},
            "recommendations": self._generate_ats_recommendations(score_components, resume_text),
        }

    def _score_formatting(self, resume_text: str) -> float:
        """Score resume formatting for ATS compatibility."""
        score = 100.0
        lines = resume_text.split("\n")

        # Check for common ATS-incompatible elements
        if any(char in resume_text for char in ["•", "◾", "▪", "○", "■"]):
            score -= 10  # Non-standard bullets

        if re.search(r"[^\x00-\x7F]", resume_text):  # Non-ASCII characters
            score -= 5

        # Check for excessive special characters
        special_char_count = sum(1 for c in resume_text if c in "!@#$%^&*")
        if special_char_count > 20:
            score -= 10

        return max(0, score)

    def _score_keywords(self, resume_text: str) -> float:
        """Score keyword presence and density."""
        score = 50.0  # Base score

        # Count common job-related keywords
        keywords = [
            "experience",
            "responsible",
            "managed",
            "developed",
            "designed",
            "implemented",
            "achieved",
            "improved",
            "led",
            "created",
            "technical",
            "skills",
        ]

        resume_lower = resume_text.lower()
        keyword_count = sum(1 for kw in keywords if kw in resume_lower)

        # Bonus for diverse keywords
        score += min(50, (keyword_count / len(keywords)) * 50)

        return min(100, score)

    def _score_structure(self, resume_text: str) -> float:
        """Score resume structure and section presence."""
        score = 70.0

        # Check for key sections
        sections = ["experience", "skills", "education", "work"]
        resume_lower = resume_text.lower()

        for section in sections:
            if section in resume_lower:
                score += 5

        # Check for consistent formatting
        lines = resume_text.split("\n")
        if len(lines) > 5:
            score += 10

        return min(100, score)

    def _score_length(self, resume_text: str) -> float:
        """Score resume length (1-2 pages is optimal for ATS)."""
        word_count = len(resume_text.split())

        # Optimal: 250-600 words (half page to 1 page)
        # Acceptable: 600-1000 words (1-2 pages)
        if 250 <= word_count <= 1000:
            return 100.0
        elif 150 <= word_count < 250:
            return 80.0
        elif 1000 < word_count <= 1500:
            return 80.0
        else:
            return 50.0

    def _score_readability(self, resume_text: str) -> float:
        """Score resume readability for ATS scanning."""
        score = 100.0
        lines = resume_text.split("\n")

        # Check line length (too long lines hurt ATS)
        long_lines = sum(1 for line in lines if len(line) > 100)
        if long_lines > len(lines) * 0.5:
            score -= 20

        # Check for whitespace and structure
        empty_lines = sum(1 for line in lines if line.strip() == "")
        if empty_lines < len(lines) * 0.1:
            score -= 10

        return max(0, score)

    def _generate_ats_recommendations(
        self,
        scores: Dict[str, float],
        resume_text: str,
    ) -> List[str]:
        """Generate specific ATS improvement recommendations."""
        recommendations = []

        if scores["formatting"] < 80:
            recommendations.append("Use standard bullet points (-) instead of special characters")
            recommendations.append("Remove tables, graphics, or non-standard formatting")
            recommendations.append("Use standard fonts (Arial, Calibri, Times New Roman)")

        if scores["keywords"] < 60:
            recommendations.append("Add more action verbs and industry-specific keywords")
            recommendations.append("Include keywords from target job descriptions")

        if scores["structure"] < 75:
            recommendations.append("Ensure clear section headers: Experience, Skills, Education")
            recommendations.append("Organize information in reverse chronological order")

        if scores["length"] < 80:
            word_count = len(resume_text.split())
            if word_count < 250:
                recommendations.append("Expand resume content - aim for 250-600 words minimum")
            else:
                recommendations.append("Condense resume content - aim for under 1000 words")

        if scores["readability"] < 80:
            recommendations.append("Break long paragraphs into bullet points")
            recommendations.append("Ensure consistent spacing and formatting")
            recommendations.append("Use short, scannable bullet points")

        if not recommendations:
            recommendations.append("Resume is well-optimized for ATS parsing")

        return recommendations

    async def get_ats_score(self, resume_text: str) -> Dict[str, Any]:
        """
        Get ATS compatibility score for a resume.

        Args:
            resume_text: Resume text to analyze

        Returns:
            ATS score details
        """
        return self.calculate_ats_compatibility_score(resume_text)

    async def tailor_resume_for_requirement(
        self,
        resume_text: str,
        requirement_title: str,
        requirement_description: str,
        candidate_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Main method to tailor a resume for a specific job requirement.

        Combines gap analysis, AI rewriting, and ATS scoring.

        Args:
            resume_text: Original resume text
            requirement_title: Job title
            requirement_description: Job description
            candidate_name: Candidate name

        Returns:
            Complete tailoring analysis and recommendations
        """
        # Create full job description context
        job_context = f"Job Title: {requirement_title}\n\n{requirement_description}"

        # Generate tailored resume
        tailored = await self.generate_tailored_resume(
            resume_text,
            job_context,
            candidate_name,
        )

        # Get ATS score for original and tailored
        original_ats = self.calculate_ats_compatibility_score(resume_text)
        tailored_ats = self.calculate_ats_compatibility_score(tailored.get("tailored_resume", resume_text))

        return {
            "job_title": requirement_title,
            "original_resume": resume_text,
            "tailored_resume": tailored.get("tailored_resume"),
            "tailoring_analysis": tailored.get("analysis"),
            "keywords_emphasized": tailored.get("keywords_added"),
            "gap_analysis": tailored.get("gap_analysis"),
            "ats_scores": {
                "original": original_ats["overall_score"],
                "tailored": tailored_ats["overall_score"],
                "improvement": round(tailored_ats["overall_score"] - original_ats["overall_score"], 1),
            },
            "ats_recommendations": tailored_ats.get("recommendations", []),
            "generated_at": datetime.utcnow().isoformat(),
        }
