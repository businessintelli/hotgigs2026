import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResumeParserAgent(BaseAgent):
    """Agent for parsing resume files and extracting structured data using NLP."""

    def __init__(self):
        """Initialize the resume parser agent."""
        super().__init__(agent_name="ResumeParserAgent", agent_version="1.0.0")
        self._init_nlp_models()

    def _init_nlp_models(self) -> None:
        """Initialize NLP models for entity extraction."""
        try:
            import spacy

            self.nlp = spacy.load("en_core_web_sm")
        except (ImportError, OSError):
            logger.warning("spaCy model not available, using regex-based parsing only")
            self.nlp = None

    async def on_start(self) -> None:
        """Initialize resume parser agent."""
        logger.info("Resume Parser Agent started")

    async def on_stop(self) -> None:
        """Cleanup resume parser agent resources."""
        logger.info("Resume Parser Agent stopped")

    async def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from resume file (PDF or DOCX).

        Args:
            file_path: Path to resume file

        Returns:
            Extracted text content
        """
        file_ext = Path(file_path).suffix.lower()

        try:
            if file_ext == ".pdf":
                return await self._extract_text_from_pdf(file_path)
            elif file_ext in [".docx", ".doc"]:
                return await self._extract_text_from_docx(file_path)
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            import pdfplumber

            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.error("pdfplumber not installed")
            raise
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise

    async def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document

            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.error("python-docx not installed")
            raise
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """
        Extract contact information from resume text.

        Extracts: name, email, phone, LinkedIn URL, location

        Args:
            text: Resume text

        Returns:
            Dictionary with contact information
        """
        contact = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "location": None,
            "confidence": {},
        }

        # Extract email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            contact["email"] = emails[0]
            contact["confidence"]["email"] = 0.95

        # Extract phone
        phone_pattern = r"(?:\+1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?[2-9]\d{2}[-.\s]?\d{4}\b"
        phones = re.findall(phone_pattern, text)
        if phones:
            contact["phone"] = phones[0]
            contact["confidence"]["phone"] = 0.9

        # Extract LinkedIn
        linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+"
        linkedin_urls = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_urls:
            contact["linkedin"] = linkedin_urls[0]
            contact["confidence"]["linkedin"] = 0.95

        # Extract name (usually first few meaningful lines)
        lines = text.split("\n")[:10]
        for line in lines:
            line = line.strip()
            if line and len(line) < 50 and not any(char.isdigit() for char in line[:10]):
                # Potential name line
                if self._is_likely_name(line):
                    contact["name"] = line
                    contact["confidence"]["name"] = 0.7
                    break

        # Extract location
        location_pattern = r"\b(?:Location|Located in|Based in|From|Address):?\s*([A-Z][a-z]+(?:\s*,\s*[A-Z]{2})?)(?:\s|$)"
        location_match = re.search(location_pattern, text, re.MULTILINE)
        if location_match:
            contact["location"] = location_match.group(1)
            contact["confidence"]["location"] = 0.8

        return contact

    def _is_likely_name(self, text: str) -> bool:
        """Check if text is likely a person's name."""
        # Names typically have 1-3 words, no numbers, no special chars except hyphens/apostrophes
        words = text.split()
        if len(words) > 3:
            return False
        if any(char.isdigit() for char in text):
            return False
        if any(char in "!@#$%^&*()_+=[]{}|;:,<>?" for char in text):
            return False
        return True

    def extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract skills from resume text.

        Uses regex patterns and keyword matching. Infers proficiency levels.

        Args:
            text: Resume text

        Returns:
            List of skills with proficiency levels
        """
        skills = []
        text_lower = text.lower()

        # Define skill categories with common terms
        skill_categories = {
            "programming_languages": [
                "python",
                "javascript",
                "java",
                "c#",
                "c++",
                "ruby",
                "php",
                "go",
                "rust",
                "scala",
                "kotlin",
                "swift",
                "typescript",
            ],
            "frontend_frameworks": [
                "react",
                "angular",
                "vue",
                "ember",
                "backbone",
                "next.js",
                "gatsby",
            ],
            "backend_frameworks": [
                "django",
                "flask",
                "fastapi",
                "spring",
                "spring boot",
                "express",
                "nest.js",
                "laravel",
                "rails",
            ],
            "databases": [
                "sql",
                "mysql",
                "postgresql",
                "mongodb",
                "redis",
                "cassandra",
                "elasticsearch",
                "dynamodb",
                "oracle",
            ],
            "cloud_platforms": [
                "aws",
                "azure",
                "gcp",
                "google cloud",
                "heroku",
                "digitalocean",
            ],
            "devops_tools": [
                "docker",
                "kubernetes",
                "jenkins",
                "gitlab ci",
                "github actions",
                "terraform",
                "ansible",
            ],
            "data_science": [
                "machine learning",
                "tensorflow",
                "pytorch",
                "pandas",
                "numpy",
                "scikit-learn",
                "data science",
            ],
            "testing": [
                "pytest",
                "jest",
                "mocha",
                "jasmine",
                "rspec",
                "unittest",
            ],
            "other": [
                "rest api",
                "graphql",
                "microservices",
                "linux",
                "git",
                "agile",
                "scrum",
            ],
        }

        # Look for skill sections first
        skill_section_pattern = r"(?:Skills?|Technical\s+Skills?|Competencies?)[\s:]*(.*?)(?=\n\n|[A-Z][a-z]+\s+(?:Experience|Education|Projects)|$)"
        skill_sections = re.findall(skill_section_pattern, text, re.MULTILINE | re.IGNORECASE)

        found_skills = set()

        # Extract skills from dedicated sections
        for section in skill_sections:
            for category, skill_list in skill_categories.items():
                for skill in skill_list:
                    if skill.lower() in section.lower() and skill not in found_skills:
                        proficiency = self._infer_proficiency(skill, text)
                        skills.append(
                            {
                                "skill": skill,
                                "category": category,
                                "proficiency": proficiency,
                                "extracted_from": "skills_section",
                                "confidence": 0.9,
                            }
                        )
                        found_skills.add(skill)

        # Extract skills from experience section with context
        experience_pattern = r"(?:Experience|Work History)[\s:]*(.*?)(?=\n\n|Education|$)"
        experience_sections = re.findall(experience_pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)

        for section in experience_sections:
            for category, skill_list in skill_categories.items():
                for skill in skill_list:
                    if skill.lower() in section.lower() and skill not in found_skills:
                        proficiency = self._infer_proficiency(skill, text)
                        skills.append(
                            {
                                "skill": skill,
                                "category": category,
                                "proficiency": proficiency,
                                "extracted_from": "experience_section",
                                "confidence": 0.7,
                            }
                        )
                        found_skills.add(skill)

        return skills

    def _infer_proficiency(self, skill: str, text: str) -> str:
        """Infer skill proficiency level from context."""
        skill_lower = skill.lower()
        text_lower = text.lower()

        # Find context around skill mention
        pattern = rf".{{0,100}}{re.escape(skill_lower)}.{{0,100}}"
        contexts = re.findall(pattern, text_lower)

        proficiency_indicators = {
            "expert": ["expert", "mastery", "deep", "advanced", "principal", "lead", "architect"],
            "proficient": ["proficient", "strong", "solid", "experienced", "proven", "extensive"],
            "intermediate": ["intermediate", "familiar", "working", "comfortable"],
            "beginner": ["basic", "introductory", "learning", "exposure"],
        }

        for level, indicators in proficiency_indicators.items():
            for context in contexts:
                if any(indicator in context for indicator in indicators):
                    return level

        return "intermediate"

    def extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience from resume text.

        Extracts: company, title, dates, responsibilities

        Args:
            text: Resume text

        Returns:
            List of work experience entries
        """
        experiences = []

        # Pattern for work experience entries
        experience_pattern = r"(?:Experience|Work|Employment|Professional)[\s:]*(.*?)(?=\n\n[A-Z]|Education|Projects|$)"
        exp_section = re.search(experience_pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)

        if not exp_section:
            return experiences

        exp_text = exp_section.group(1)

        # Split by company/title patterns
        job_pattern = r"(?:^|\n)([^,\n]{10,100})\s*-?\s*([^,\n]{5,50})\s*[|•-]\s*(?:([A-Z][a-z]+\s+\d{4})\s*-?\s*([A-Z][a-z]+\s+\d{4}|Present)|([\d/]+)\s*-?\s*([\d/]+|Present)))"

        for match in re.finditer(job_pattern, exp_text, re.MULTILINE):
            company = match.group(1).strip()
            title = match.group(2).strip()
            start_date = match.group(3) or match.group(5)
            end_date = match.group(4) or match.group(6)

            # Extract responsibilities (bullet points following the job entry)
            start_pos = match.end()
            end_pos = exp_text.find("\n\n", start_pos) or len(exp_text)
            resp_text = exp_text[start_pos:end_pos]

            responsibilities = []
            resp_pattern = r"[•\-*]\s*(.{10,200}?)(?=\n[•\-*]|\n|$)"
            for resp_match in re.finditer(resp_pattern, resp_text):
                responsibility = resp_match.group(1).strip()
                if responsibility:
                    responsibilities.append(responsibility)

            experiences.append(
                {
                    "company": company,
                    "title": title,
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": end_date and end_date.lower() in ["present", "current", "ongoing"],
                    "responsibilities": responsibilities,
                    "confidence": 0.7,
                }
            )

        return experiences

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract education information from resume text.

        Extracts: degree, field, institution, year, GPA

        Args:
            text: Resume text

        Returns:
            List of education entries
        """
        education = []

        # Pattern for education section
        education_pattern = r"(?:Education|Academic|Certifications?)[\s:]*(.*?)(?=\n\n[A-Z][a-z]+|Skills|Projects|$)"
        edu_section = re.search(education_pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)

        if not edu_section:
            return education

        edu_text = edu_section.group(1)

        # Extract degree information
        degree_pattern = r"(Bachelor|Master|Ph\.?D|Associate|Diploma|Certificate|B\.S\.|B\.A\.|M\.S\.|M\.A\.|MBA|M\.B\.A)\s+(?:of|in|–|-)?\s*([^,•\n]{5,50})"

        for match in re.finditer(degree_pattern, edu_text, re.IGNORECASE):
            degree = match.group(1).strip()
            field = match.group(2).strip()

            # Find institution (typically on same or previous line)
            start = max(0, match.start() - 100)
            context = edu_text[start : match.start()]
            institution_match = re.search(r"([A-Z][a-zA-Z\s&]+(?:University|College|Institute|School))", context)
            institution = institution_match.group(1).strip() if institution_match else None

            # Extract year
            year_match = re.search(r"(\d{4})", edu_text[match.start() : match.end() + 50])
            year = year_match.group(1) if year_match else None

            # Extract GPA if present
            gpa_match = re.search(r"GPA\s*:?\s*([\d.]+)", edu_text[match.start() : match.end() + 50], re.IGNORECASE)
            gpa = float(gpa_match.group(1)) if gpa_match else None

            education.append(
                {
                    "degree": degree,
                    "field": field,
                    "institution": institution,
                    "graduation_year": year,
                    "gpa": gpa,
                    "confidence": 0.75,
                }
            )

        return education

    def extract_certifications(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract certifications from resume text.

        Args:
            text: Resume text

        Returns:
            List of certifications
        """
        certifications = []

        # Common certification keywords
        cert_keywords = [
            "AWS Certified",
            "Google Cloud",
            "Azure Certified",
            "Kubernetes",
            "Docker",
            "PMP",
            "CISSP",
            "Security+",
            "CompTIA",
            "Scrum Master",
            "PRINCE2",
            "ITIL",
        ]

        cert_pattern = r"(?:Certifications?|Licenses?|Credentials?)[\s:]*(.*?)(?=\n\n[A-Z]|$)"
        cert_section = re.search(cert_pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)

        cert_text = cert_section.group(1) if cert_section else text

        for cert_keyword in cert_keywords:
            if cert_keyword.lower() in cert_text.lower():
                # Extract the full certification name
                pattern = rf"{re.escape(cert_keyword)}[^•\n]*"
                matches = re.findall(pattern, cert_text, re.IGNORECASE)
                for match in matches:
                    certifications.append(
                        {
                            "certification": match.strip(),
                            "confidence": 0.85,
                        }
                    )

        return certifications

    async def parse_resume(self, text: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse resume text and extract all structured information.

        Args:
            text: Resume text content
            file_name: Optional file name for context

        Returns:
            Parsed resume data with confidence scores
        """
        try:
            logger.info(f"Parsing resume: {file_name or 'unnamed'}")

            parsed = {
                "raw_text": text,
                "parsed_data": {},
                "extraction_stats": {},
                "parsing_confidence": 0.0,
                "parser_version": "1.0.0",
                "parsed_at": datetime.utcnow().isoformat(),
            }

            # Extract sections
            contact_info = self.extract_contact_info(text)
            skills = self.extract_skills(text)
            experience = self.extract_work_experience(text)
            education = self.extract_education(text)
            certifications = self.extract_certifications(text)

            # Build parsed data
            parsed["parsed_data"] = {
                "contact": contact_info,
                "skills": skills,
                "experience": experience,
                "education": education,
                "certifications": certifications,
            }

            # Statistics
            parsed["extraction_stats"] = {
                "skills_extracted": len(skills),
                "experiences_extracted": len(experience),
                "education_entries": len(education),
                "certifications_found": len(certifications),
                "contact_fields_found": sum(1 for v in contact_info["confidence"].values() if v),
            }

            # Calculate overall parsing confidence
            confidence_scores = []
            confidence_scores.extend(contact_info.get("confidence", {}).values())
            confidence_scores.extend([s.get("confidence", 0.5) for s in skills])
            confidence_scores.extend([e.get("confidence", 0.5) for e in experience])
            confidence_scores.extend([e.get("confidence", 0.5) for e in education])

            if confidence_scores:
                parsed["parsing_confidence"] = round(sum(confidence_scores) / len(confidence_scores), 3)
            else:
                parsed["parsing_confidence"] = 0.5

            logger.info(f"Resume parsing completed: {parsed['extraction_stats']}")

            return parsed

        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise

    async def check_duplicate_candidate(
        self,
        email: str,
        name: str,
        existing_candidates: List[Dict[str, Any]],
        fuzzy_threshold: float = 0.85,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check for duplicate candidate using fuzzy matching.

        Uses email exact match first, then name fuzzy matching.

        Args:
            email: Candidate email
            name: Candidate name
            existing_candidates: List of existing candidates
            fuzzy_threshold: Threshold for fuzzy name matching (0-1)

        Returns:
            Tuple of (is_duplicate, matching_candidate)
        """
        if not email and not name:
            return False, None

        # Exact email match
        if email:
            for candidate in existing_candidates:
                if candidate.get("email", "").lower() == email.lower():
                    return True, candidate

        # Fuzzy name match
        if name:
            try:
                from difflib import SequenceMatcher

                for candidate in existing_candidates:
                    candidate_name = candidate.get("name", "")
                    if candidate_name:
                        similarity = SequenceMatcher(None, name.lower(), candidate_name.lower()).ratio()
                        if similarity >= fuzzy_threshold:
                            return True, candidate
            except ImportError:
                logger.warning("difflib not available, skipping fuzzy name matching")

        return False, None
