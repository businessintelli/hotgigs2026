"""Detailed Interview Feedback API — structured Q&A questionnaires,
persistent candidate scoring, recruiter visibility controls,
and score-to-job match computation.

Provides:
- Question bank management (technical + non-technical)
- Detailed feedback session collection with per-question answers
- Recruiter visibility controls for submission sharing
- Persistent candidate skill/tech scores aggregated across interviews
- Job match score computation using accumulated feedback
- Score-based candidate recommendations for future jobs
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(prefix="/interview-feedback")


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Question Bank
# ══════════════════════════════════════════════════════════════

_mock_questions = [
    # ── Technical Questions ──
    {"id": 1, "question_text": "Rate the candidate's proficiency in Python programming", "category": "technical", "question_type": "rating_1_5", "technology": "Python", "skill_tag": "backend", "difficulty_level": "medium", "scoring_guide": {"1": "No knowledge", "2": "Basic syntax", "3": "Working knowledge", "4": "Advanced (decorators, generators, async)", "5": "Expert (metaclasses, C extensions, optimization)"}, "weight": 1.5, "is_required": True, "is_eliminatory": False, "min_passing_score": 3, "is_active": True, "usage_count": 156},
    {"id": 2, "question_text": "Evaluate SQL and database design skills", "category": "technical", "question_type": "rating_1_5", "technology": "SQL", "skill_tag": "database", "difficulty_level": "medium", "scoring_guide": {"1": "Cannot write basic queries", "2": "Simple SELECT/INSERT", "3": "JOINs, subqueries, indexing", "4": "Query optimization, stored procedures", "5": "Database architecture, sharding, replication"}, "weight": 1.3, "is_required": True, "is_eliminatory": False, "min_passing_score": 3, "is_active": True, "usage_count": 142},
    {"id": 3, "question_text": "Rate experience with React/frontend frameworks", "category": "framework", "question_type": "rating_1_5", "technology": "React", "skill_tag": "frontend", "difficulty_level": "medium", "scoring_guide": {"1": "No experience", "2": "Basic components", "3": "Hooks, state management", "4": "Performance optimization, testing", "5": "Architecture, custom hooks, advanced patterns"}, "weight": 1.2, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 98},
    {"id": 4, "question_text": "Evaluate AWS/cloud infrastructure knowledge", "category": "technical", "question_type": "rating_1_5", "technology": "AWS", "skill_tag": "devops", "difficulty_level": "hard", "scoring_guide": {"1": "No cloud experience", "2": "Basic S3/EC2", "3": "Lambda, RDS, VPC", "4": "Multi-region, cost optimization", "5": "Solutions architect level"}, "weight": 1.2, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 87},
    {"id": 5, "question_text": "System design: Design a URL shortener (or similar)", "category": "system_design", "question_type": "rating_1_10", "technology": None, "skill_tag": "architecture", "difficulty_level": "hard", "scoring_guide": {"1-3": "Incomplete, missing key components", "4-6": "Basic design with some gaps", "7-8": "Solid design with scalability", "9-10": "Exceptional with trade-off analysis"}, "weight": 2.0, "is_required": False, "is_eliminatory": False, "min_passing_score": 5, "is_active": True, "usage_count": 64},
    {"id": 6, "question_text": "Rate Java/Spring Boot proficiency", "category": "technical", "question_type": "rating_1_5", "technology": "Java", "skill_tag": "backend", "difficulty_level": "medium", "scoring_guide": {"1": "No knowledge", "2": "Basic syntax", "3": "Spring Boot basics", "4": "Microservices, JPA, security", "5": "Performance tuning, custom starters"}, "weight": 1.3, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 112},
    {"id": 7, "question_text": "Evaluate Docker/Kubernetes experience", "category": "technical", "question_type": "rating_1_5", "technology": "Docker", "skill_tag": "devops", "difficulty_level": "medium", "scoring_guide": {"1": "No experience", "2": "Can use Docker", "3": "Dockerfile, compose", "4": "K8s deployments, services", "5": "Helm, operators, service mesh"}, "weight": 1.0, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 73},
    {"id": 8, "question_text": "Rate data engineering skills (ETL, pipelines, data warehousing)", "category": "technical", "question_type": "rating_1_5", "technology": "Data Engineering", "skill_tag": "data", "difficulty_level": "hard", "scoring_guide": {"1": "No experience", "2": "Basic SQL ETL", "3": "Spark/Airflow basics", "4": "Production pipelines", "5": "Data lake architecture"}, "weight": 1.2, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 45},

    # ── Immigration & Work Authorization ──
    {"id": 20, "question_text": "What is the candidate's current work authorization status?", "category": "work_authorization", "question_type": "select", "technology": None, "skill_tag": "visa", "difficulty_level": None, "options": ["US Citizen", "Green Card", "H1B", "H1B Transfer", "OPT", "CPT", "L1", "TN", "EAD", "Requires Sponsorship", "Other"], "weight": 1.0, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 189},
    {"id": 21, "question_text": "If on H1B/OPT, what is the visa expiry date?", "category": "immigration", "question_type": "date", "technology": None, "skill_tag": "visa", "difficulty_level": None, "weight": 0.8, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 134},
    {"id": 22, "question_text": "Is the candidate willing to transfer H1B if currently employed elsewhere?", "category": "immigration", "question_type": "yes_no", "technology": None, "skill_tag": "visa", "difficulty_level": None, "weight": 0.8, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 98},
    {"id": 23, "question_text": "Does the candidate need future immigration sponsorship (Green Card)?", "category": "immigration", "question_type": "yes_no", "technology": None, "skill_tag": "visa", "difficulty_level": None, "weight": 0.6, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 156},
    {"id": 24, "question_text": "Rate confidence in candidate's immigration timeline and stability", "category": "immigration", "question_type": "rating_1_5", "technology": None, "skill_tag": "visa", "scoring_guide": {"1": "High risk — expiring soon, no path", "2": "Moderate risk — needs transfer/renewal", "3": "Manageable — pending renewal with good chances", "4": "Stable — valid long-term visa", "5": "No risk — citizen/green card"}, "difficulty_level": None, "weight": 1.0, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 112},

    # ── Location & Relocation ──
    {"id": 30, "question_text": "Where is the candidate currently located?", "category": "location", "question_type": "free_text", "technology": None, "skill_tag": "location", "difficulty_level": None, "weight": 0.8, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 198},
    {"id": 31, "question_text": "Is the candidate willing to relocate if required?", "category": "relocation", "question_type": "select", "technology": None, "skill_tag": "location", "options": ["Yes — anywhere", "Yes — within same state", "Yes — within region", "Only for the right opportunity", "No — remote only", "Already local"], "difficulty_level": None, "weight": 0.8, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 167},
    {"id": 32, "question_text": "Can the candidate work the required schedule/time zone?", "category": "availability", "question_type": "yes_no", "technology": None, "skill_tag": "availability", "difficulty_level": None, "weight": 0.7, "is_required": True, "is_eliminatory": True, "min_passing_score": None, "is_active": True, "usage_count": 145},
    {"id": 33, "question_text": "What is the candidate's preferred work arrangement?", "category": "availability", "question_type": "select", "technology": None, "skill_tag": "availability", "options": ["On-site only", "Hybrid (2-3 days)", "Hybrid (1 day)", "Remote only", "Flexible"], "difficulty_level": None, "weight": 0.6, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 178},

    # ── Availability & Compensation ──
    {"id": 40, "question_text": "When is the candidate available to start?", "category": "availability", "question_type": "select", "technology": None, "skill_tag": "availability", "options": ["Immediately", "1 week", "2 weeks", "30 days", "60+ days"], "difficulty_level": None, "weight": 0.8, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 192},
    {"id": 41, "question_text": "What is the candidate's expected hourly rate ($/hr)?", "category": "compensation", "question_type": "numeric", "technology": None, "skill_tag": "compensation", "difficulty_level": None, "weight": 1.0, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 201},
    {"id": 42, "question_text": "Is the rate negotiable?", "category": "compensation", "question_type": "yes_no", "technology": None, "skill_tag": "compensation", "difficulty_level": None, "weight": 0.5, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 167},

    # ── Communication & Culture ──
    {"id": 50, "question_text": "Rate the candidate's English communication skills", "category": "communication", "question_type": "rating_1_5", "technology": None, "skill_tag": "soft_skills", "scoring_guide": {"1": "Significant language barrier", "2": "Basic communication, some difficulty", "3": "Functional, can work in English", "4": "Good — clear and articulate", "5": "Excellent — native or near-native"}, "difficulty_level": None, "weight": 1.2, "is_required": True, "is_eliminatory": False, "min_passing_score": 3, "is_active": True, "usage_count": 187},
    {"id": 51, "question_text": "Rate the candidate's professionalism and presentation", "category": "culture_fit", "question_type": "rating_1_5", "technology": None, "skill_tag": "soft_skills", "scoring_guide": {"1": "Unprofessional", "2": "Below average", "3": "Adequate", "4": "Professional", "5": "Exceptional presence"}, "difficulty_level": None, "weight": 0.8, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 145},
    {"id": 52, "question_text": "Would this candidate be client-facing ready?", "category": "culture_fit", "question_type": "yes_no", "technology": None, "skill_tag": "soft_skills", "difficulty_level": None, "weight": 0.7, "is_required": False, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 123},

    # ── Project Experience ──
    {"id": 60, "question_text": "Years of relevant experience in the required technology stack", "category": "project_experience", "question_type": "numeric", "technology": None, "skill_tag": "experience", "difficulty_level": None, "weight": 1.0, "is_required": True, "is_eliminatory": False, "min_passing_score": None, "is_active": True, "usage_count": 198},
    {"id": 61, "question_text": "Rate depth of hands-on project experience", "category": "project_experience", "question_type": "rating_1_5", "technology": None, "skill_tag": "experience", "scoring_guide": {"1": "No real projects", "2": "Academic/personal only", "3": "1-2 professional projects", "4": "Multiple enterprise projects", "5": "Led architecture of major systems"}, "difficulty_level": None, "weight": 1.3, "is_required": True, "is_eliminatory": False, "min_passing_score": 2, "is_active": True, "usage_count": 176},
]

# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Feedback Sessions (detailed)
# ══════════════════════════════════════════════════════════════

_mock_feedback_sessions = [
    {
        "id": 1, "interview_id": 101, "candidate_id": 1, "candidate_name": "Rajesh Kumar",
        "requirement_id": 201, "requirement_title": "Senior Python Developer — TechCorp",
        "evaluator_name": "Sarah Mitchell", "evaluator_email": "sarah.m@hotgigs.com",
        "feedback_source": "recruiter",
        "overall_rating": 4.2, "overall_recommendation": "hire",
        "summary_notes": "Strong Python developer with solid SQL skills. Good communication. H1B visa needs transfer but timeline is manageable. Willing to relocate to Bay Area.",
        "strengths": ["Deep Python expertise", "Strong SQL/database skills", "Good communicator", "Available in 2 weeks"],
        "concerns": ["H1B transfer needed", "Rate slightly above budget", "No React experience"],
        "technical_score": 85, "communication_score": 80, "culture_fit_score": 75,
        "immigration_score": 65, "location_score": 80, "availability_score": 90,
        "job_fit_score": 82, "technology_match_score": 78,
        "visibility": "internal_only", "share_technical_scores": True, "share_immigration_details": False,
        "share_compensation_details": False, "share_detailed_notes": False, "shared_with_submission": False,
        "started_at": "2026-03-10T10:00:00Z", "completed_at": "2026-03-10T10:45:00Z", "duration_minutes": 45,
        "is_draft": False,
        "answers": [
            {"question_id": 1, "answer_rating": 4, "score": 80, "evaluator_notes": "Strong Python. Uses decorators and async well. Good understanding of GIL."},
            {"question_id": 2, "answer_rating": 4, "score": 80, "evaluator_notes": "Solid SQL. Can optimize queries. Familiar with PostgreSQL."},
            {"question_id": 3, "answer_rating": 2, "score": 40, "evaluator_notes": "Limited React. Mostly backend focused."},
            {"question_id": 4, "answer_rating": 3, "score": 60, "evaluator_notes": "Basic AWS — EC2, S3, Lambda. No multi-region experience."},
            {"question_id": 20, "answer_choice": "H1B", "evaluator_notes": "Currently on H1B with another employer."},
            {"question_id": 22, "answer_choice": "Yes", "evaluator_notes": "Willing to transfer. Current visa valid until 2028."},
            {"question_id": 24, "answer_rating": 3, "score": 60, "evaluator_notes": "H1B transfer needed but visa is stable."},
            {"question_id": 30, "answer_text": "Houston, TX", "evaluator_notes": ""},
            {"question_id": 31, "answer_choice": "Yes — within region", "evaluator_notes": "Prefers Texas but open to Bay Area."},
            {"question_id": 40, "answer_choice": "2 weeks", "evaluator_notes": "Needs to give notice."},
            {"question_id": 41, "answer_numeric": 85, "evaluator_notes": "Asking $85/hr. Budget is $80."},
            {"question_id": 50, "answer_rating": 4, "score": 80, "evaluator_notes": "Clear communication, slight accent but very articulate."},
            {"question_id": 60, "answer_numeric": 7, "evaluator_notes": "7 years Python, 5 years SQL."},
            {"question_id": 61, "answer_rating": 4, "score": 80, "evaluator_notes": "Led backend redesign at previous company."},
        ],
    },
    {
        "id": 2, "interview_id": 102, "candidate_id": 2, "candidate_name": "Emily Chen",
        "requirement_id": 201, "requirement_title": "Senior Python Developer — TechCorp",
        "evaluator_name": "AI Interview Bot", "evaluator_email": "ai-bot@hotgigs.com",
        "feedback_source": "ai_bot",
        "overall_rating": 4.5, "overall_recommendation": "strong_hire",
        "summary_notes": "Exceptional Python skills with strong system design thinking. US Citizen, no immigration concerns. Located in SF Bay Area — ideal for the role. Excellent communicator.",
        "strengths": ["Expert Python (metaclasses, C extensions)", "Strong system design", "US Citizen", "Bay Area local", "Excellent communicator"],
        "concerns": ["Rate at top of budget", "Limited AWS experience"],
        "technical_score": 92, "communication_score": 90, "culture_fit_score": 85,
        "immigration_score": 100, "location_score": 100, "availability_score": 85,
        "job_fit_score": 91, "technology_match_score": 88,
        "visibility": "internal_only", "share_technical_scores": True, "share_immigration_details": True,
        "share_compensation_details": False, "share_detailed_notes": True, "shared_with_submission": True,
        "started_at": "2026-03-11T14:00:00Z", "completed_at": "2026-03-11T14:35:00Z", "duration_minutes": 35,
        "is_draft": False,
        "answers": [
            {"question_id": 1, "answer_rating": 5, "score": 100, "evaluator_notes": "Expert-level Python. Discussed metaclass patterns, async generators, and CPython internals."},
            {"question_id": 2, "answer_rating": 4, "score": 80, "evaluator_notes": "Strong SQL with query optimization experience."},
            {"question_id": 3, "answer_rating": 3, "score": 60, "evaluator_notes": "Working knowledge of React. Built a few internal tools."},
            {"question_id": 4, "answer_rating": 2, "score": 40, "evaluator_notes": "Basic AWS. Uses S3 and EC2 but limited serverless."},
            {"question_id": 5, "answer_rating": 8, "score": 80, "evaluator_notes": "Solid URL shortener design with caching, consistent hashing."},
            {"question_id": 20, "answer_choice": "US Citizen", "evaluator_notes": "No immigration issues."},
            {"question_id": 30, "answer_text": "San Francisco, CA", "evaluator_notes": ""},
            {"question_id": 31, "answer_choice": "Already local", "evaluator_notes": "Lives in SF."},
            {"question_id": 40, "answer_choice": "30 days", "evaluator_notes": "Currently employed, needs notice period."},
            {"question_id": 41, "answer_numeric": 95, "evaluator_notes": "Asking $95/hr. At top of $80-95 budget range."},
            {"question_id": 50, "answer_rating": 5, "score": 100, "evaluator_notes": "Exceptional communicator. Clear, concise, well-structured responses."},
            {"question_id": 60, "answer_numeric": 9, "evaluator_notes": "9 years Python experience."},
            {"question_id": 61, "answer_rating": 5, "score": 100, "evaluator_notes": "Led microservices migration serving 10M+ users."},
        ],
    },
    {
        "id": 3, "interview_id": 103, "candidate_id": 3, "candidate_name": "Marcus Johnson",
        "requirement_id": 202, "requirement_title": "Full Stack Developer — MedFirst Health",
        "evaluator_name": "Tom Richards", "evaluator_email": "tom.r@hotgigs.com",
        "feedback_source": "recruiter",
        "overall_rating": 3.6, "overall_recommendation": "maybe",
        "summary_notes": "Decent full stack skills but gaps in backend architecture. Good React but Python is intermediate. On OPT — timeline concern. Remote preference may conflict with hybrid requirement.",
        "strengths": ["Strong React/frontend", "Good UI/UX sense", "Eager to learn"],
        "concerns": ["Python intermediate only", "OPT expiring in 6 months", "Wants remote — role is hybrid", "Limited system design skills"],
        "technical_score": 68, "communication_score": 72, "culture_fit_score": 70,
        "immigration_score": 40, "location_score": 50, "availability_score": 75,
        "job_fit_score": 58, "technology_match_score": 62,
        "visibility": "internal_only", "share_technical_scores": True, "share_immigration_details": False,
        "share_compensation_details": False, "share_detailed_notes": False, "shared_with_submission": False,
        "started_at": "2026-03-12T09:00:00Z", "completed_at": "2026-03-12T09:50:00Z", "duration_minutes": 50,
        "is_draft": False,
        "answers": [
            {"question_id": 1, "answer_rating": 3, "score": 60, "evaluator_notes": "Intermediate Python. Can write scripts but limited OOP."},
            {"question_id": 2, "answer_rating": 3, "score": 60, "evaluator_notes": "Basic SQL. Can write JOINs but no optimization."},
            {"question_id": 3, "answer_rating": 4, "score": 80, "evaluator_notes": "Strong React. Hooks, context, custom hooks."},
            {"question_id": 20, "answer_choice": "OPT", "evaluator_notes": "OPT expires in 6 months. Needs H1B sponsorship."},
            {"question_id": 23, "answer_choice": "Yes", "evaluator_notes": "Needs H1B and eventually Green Card sponsorship."},
            {"question_id": 24, "answer_rating": 2, "score": 40, "evaluator_notes": "OPT expiring, no H1B petitioned yet. High risk."},
            {"question_id": 30, "answer_text": "Chicago, IL", "evaluator_notes": ""},
            {"question_id": 31, "answer_choice": "No — remote only", "evaluator_notes": "Insists on remote. Role requires hybrid."},
            {"question_id": 33, "answer_choice": "Remote only", "evaluator_notes": "Conflict with job requirement."},
            {"question_id": 40, "answer_choice": "Immediately", "evaluator_notes": "Available now."},
            {"question_id": 41, "answer_numeric": 65, "evaluator_notes": "$65/hr — within budget."},
            {"question_id": 50, "answer_rating": 4, "score": 80, "evaluator_notes": "Good communicator."},
            {"question_id": 60, "answer_numeric": 3, "evaluator_notes": "3 years experience — meets minimum but not ideal."},
            {"question_id": 61, "answer_rating": 3, "score": 60, "evaluator_notes": "Worked on 2 professional projects. No architecture experience."},
        ],
    },
    {
        "id": 4, "interview_id": 104, "candidate_id": 1, "candidate_name": "Rajesh Kumar",
        "requirement_id": 203, "requirement_title": "Backend Engineer — DataFlow Analytics",
        "evaluator_name": "AI Interview Bot", "evaluator_email": "ai-bot@hotgigs.com",
        "feedback_source": "ai_bot",
        "overall_rating": 4.4, "overall_recommendation": "hire",
        "summary_notes": "Second interview for Rajesh — consistent strong performance on Python and SQL. Demonstrates improving system design skills. H1B transfer still pending from last assessment.",
        "strengths": ["Consistent Python performance", "Improved system design thinking", "Strong data pipeline experience"],
        "concerns": ["H1B transfer still pending"],
        "technical_score": 88, "communication_score": 82, "culture_fit_score": 78,
        "immigration_score": 65, "location_score": 90, "availability_score": 85,
        "job_fit_score": 85, "technology_match_score": 84,
        "visibility": "share_with_client", "share_technical_scores": True, "share_immigration_details": False,
        "share_compensation_details": False, "share_detailed_notes": True, "shared_with_submission": True,
        "started_at": "2026-03-14T11:00:00Z", "completed_at": "2026-03-14T11:40:00Z", "duration_minutes": 40,
        "is_draft": False,
        "answers": [
            {"question_id": 1, "answer_rating": 5, "score": 100, "evaluator_notes": "Showed improvement — discussed advanced async patterns and performance profiling."},
            {"question_id": 2, "answer_rating": 4, "score": 80, "evaluator_notes": "Consistent SQL performance. Added knowledge of query plans."},
            {"question_id": 5, "answer_rating": 7, "score": 70, "evaluator_notes": "Good system design. Addressed caching and load balancing."},
            {"question_id": 8, "answer_rating": 4, "score": 80, "evaluator_notes": "Good data engineering skills. Experience with Airflow and Spark."},
            {"question_id": 20, "answer_choice": "H1B Transfer", "evaluator_notes": "Transfer in progress."},
            {"question_id": 24, "answer_rating": 3, "score": 60, "evaluator_notes": "Transfer pending — medium risk."},
            {"question_id": 30, "answer_text": "Houston, TX", "evaluator_notes": ""},
            {"question_id": 31, "answer_choice": "Yes — anywhere", "evaluator_notes": "Open to relocation now."},
            {"question_id": 40, "answer_choice": "2 weeks", "evaluator_notes": ""},
            {"question_id": 41, "answer_numeric": 82, "evaluator_notes": "Reduced ask to $82/hr from $85."},
            {"question_id": 50, "answer_rating": 4, "score": 80, "evaluator_notes": "Consistent good communication."},
            {"question_id": 61, "answer_rating": 4, "score": 80, "evaluator_notes": "Discussed new data pipeline project at current role."},
        ],
    },
]


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Persistent Candidate Scores (aggregated)
# ══════════════════════════════════════════════════════════════

_mock_persistent_scores = [
    # Rajesh Kumar — 2 interviews contributing
    {"id": 1, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "skill_or_technology": "Python", "category": "technical", "current_score": 90, "score_count": 2, "highest_score": 100, "lowest_score": 80, "confidence_level": 0.85, "trend": "improving", "last_assessed_at": "2026-03-14", "score_history": [{"date": "2026-03-10", "score": 80, "interview_id": 101}, {"date": "2026-03-14", "score": 100, "interview_id": 104}]},
    {"id": 2, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "skill_or_technology": "SQL", "category": "technical", "current_score": 80, "score_count": 2, "highest_score": 80, "lowest_score": 80, "confidence_level": 0.80, "trend": "stable", "last_assessed_at": "2026-03-14", "score_history": [{"date": "2026-03-10", "score": 80, "interview_id": 101}, {"date": "2026-03-14", "score": 80, "interview_id": 104}]},
    {"id": 3, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "skill_or_technology": "React", "category": "framework", "current_score": 40, "score_count": 1, "highest_score": 40, "lowest_score": 40, "confidence_level": 0.45, "trend": "stable", "last_assessed_at": "2026-03-10", "score_history": [{"date": "2026-03-10", "score": 40, "interview_id": 101}]},
    {"id": 4, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "skill_or_technology": "AWS", "category": "technical", "current_score": 60, "score_count": 1, "highest_score": 60, "lowest_score": 60, "confidence_level": 0.45, "trend": "stable", "last_assessed_at": "2026-03-10", "score_history": [{"date": "2026-03-10", "score": 60, "interview_id": 101}]},
    {"id": 5, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "skill_or_technology": "Data Engineering", "category": "technical", "current_score": 80, "score_count": 1, "highest_score": 80, "lowest_score": 80, "confidence_level": 0.50, "trend": "stable", "last_assessed_at": "2026-03-14", "score_history": [{"date": "2026-03-14", "score": 80, "interview_id": 104}]},
    {"id": 6, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "skill_or_technology": "Communication", "category": "communication", "current_score": 80, "score_count": 2, "highest_score": 80, "lowest_score": 80, "confidence_level": 0.82, "trend": "stable", "last_assessed_at": "2026-03-14", "score_history": [{"date": "2026-03-10", "score": 80, "interview_id": 101}, {"date": "2026-03-14", "score": 80, "interview_id": 104}]},
    {"id": 7, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "skill_or_technology": "Immigration (H1B)", "category": "immigration", "current_score": 60, "score_count": 2, "highest_score": 60, "lowest_score": 60, "confidence_level": 0.75, "trend": "stable", "last_assessed_at": "2026-03-14", "score_history": [{"date": "2026-03-10", "score": 60, "interview_id": 101}, {"date": "2026-03-14", "score": 60, "interview_id": 104}]},

    # Emily Chen — 1 interview contributing
    {"id": 10, "candidate_id": 2, "candidate_name": "Emily Chen", "skill_or_technology": "Python", "category": "technical", "current_score": 100, "score_count": 1, "highest_score": 100, "lowest_score": 100, "confidence_level": 0.55, "trend": "stable", "last_assessed_at": "2026-03-11", "score_history": [{"date": "2026-03-11", "score": 100, "interview_id": 102}]},
    {"id": 11, "candidate_id": 2, "candidate_name": "Emily Chen", "skill_or_technology": "SQL", "category": "technical", "current_score": 80, "score_count": 1, "highest_score": 80, "lowest_score": 80, "confidence_level": 0.50, "trend": "stable", "last_assessed_at": "2026-03-11", "score_history": [{"date": "2026-03-11", "score": 80, "interview_id": 102}]},
    {"id": 12, "candidate_id": 2, "candidate_name": "Emily Chen", "skill_or_technology": "React", "category": "framework", "current_score": 60, "score_count": 1, "highest_score": 60, "lowest_score": 60, "confidence_level": 0.45, "trend": "stable", "last_assessed_at": "2026-03-11", "score_history": [{"date": "2026-03-11", "score": 60, "interview_id": 102}]},
    {"id": 13, "candidate_id": 2, "candidate_name": "Emily Chen", "skill_or_technology": "System Design", "category": "system_design", "current_score": 80, "score_count": 1, "highest_score": 80, "lowest_score": 80, "confidence_level": 0.50, "trend": "stable", "last_assessed_at": "2026-03-11", "score_history": [{"date": "2026-03-11", "score": 80, "interview_id": 102}]},
    {"id": 14, "candidate_id": 2, "candidate_name": "Emily Chen", "skill_or_technology": "Communication", "category": "communication", "current_score": 100, "score_count": 1, "highest_score": 100, "lowest_score": 100, "confidence_level": 0.55, "trend": "stable", "last_assessed_at": "2026-03-11", "score_history": [{"date": "2026-03-11", "score": 100, "interview_id": 102}]},
    {"id": 15, "candidate_id": 2, "candidate_name": "Emily Chen", "skill_or_technology": "Immigration", "category": "immigration", "current_score": 100, "score_count": 1, "highest_score": 100, "lowest_score": 100, "confidence_level": 0.55, "trend": "stable", "last_assessed_at": "2026-03-11", "score_history": [{"date": "2026-03-11", "score": 100, "interview_id": 102}]},

    # Marcus Johnson — 1 interview
    {"id": 20, "candidate_id": 3, "candidate_name": "Marcus Johnson", "skill_or_technology": "Python", "category": "technical", "current_score": 60, "score_count": 1, "highest_score": 60, "lowest_score": 60, "confidence_level": 0.45, "trend": "stable", "last_assessed_at": "2026-03-12", "score_history": [{"date": "2026-03-12", "score": 60, "interview_id": 103}]},
    {"id": 21, "candidate_id": 3, "candidate_name": "Marcus Johnson", "skill_or_technology": "SQL", "category": "technical", "current_score": 60, "score_count": 1, "highest_score": 60, "lowest_score": 60, "confidence_level": 0.45, "trend": "stable", "last_assessed_at": "2026-03-12", "score_history": [{"date": "2026-03-12", "score": 60, "interview_id": 103}]},
    {"id": 22, "candidate_id": 3, "candidate_name": "Marcus Johnson", "skill_or_technology": "React", "category": "framework", "current_score": 80, "score_count": 1, "highest_score": 80, "lowest_score": 80, "confidence_level": 0.50, "trend": "stable", "last_assessed_at": "2026-03-12", "score_history": [{"date": "2026-03-12", "score": 80, "interview_id": 103}]},
    {"id": 23, "candidate_id": 3, "candidate_name": "Marcus Johnson", "skill_or_technology": "Immigration (OPT)", "category": "immigration", "current_score": 40, "score_count": 1, "highest_score": 40, "lowest_score": 40, "confidence_level": 0.45, "trend": "stable", "last_assessed_at": "2026-03-12", "score_history": [{"date": "2026-03-12", "score": 40, "interview_id": 103}]},
]


# ══════════════════════════════════════════════════════════════
#  MOCK DATA — Job Match Scores
# ══════════════════════════════════════════════════════════════

_mock_job_matches = [
    # Rajesh vs Senior Python Developer
    {"id": 1, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "requirement_id": 201, "requirement_title": "Senior Python Developer — TechCorp", "overall_match_score": 82, "technical_match_score": 85, "experience_match_score": 80, "immigration_match_score": 65, "location_match_score": 80, "availability_match_score": 90, "culture_match_score": 75, "compensation_match_score": 75,
     "matched_skills": [{"skill": "Python", "required_level": 80, "candidate_level": 90, "gap": 10}, {"skill": "SQL", "required_level": 70, "candidate_level": 80, "gap": 10}, {"skill": "AWS", "required_level": 60, "candidate_level": 60, "gap": 0}],
     "missing_skills": ["React (limited)"], "exceeding_skills": ["Python", "SQL"],
     "risk_factors": ["H1B transfer needed"], "recommendation": "good_fit"},
    # Emily vs Senior Python Developer
    {"id": 2, "candidate_id": 2, "candidate_name": "Emily Chen", "requirement_id": 201, "requirement_title": "Senior Python Developer — TechCorp", "overall_match_score": 91, "technical_match_score": 92, "experience_match_score": 88, "immigration_match_score": 100, "location_match_score": 100, "availability_match_score": 85, "culture_match_score": 85, "compensation_match_score": 70,
     "matched_skills": [{"skill": "Python", "required_level": 80, "candidate_level": 100, "gap": 20}, {"skill": "SQL", "required_level": 70, "candidate_level": 80, "gap": 10}, {"skill": "System Design", "required_level": 60, "candidate_level": 80, "gap": 20}],
     "missing_skills": ["AWS (limited)"], "exceeding_skills": ["Python", "System Design", "Communication"],
     "risk_factors": ["Rate at top of budget"], "recommendation": "strong_fit"},
    # Marcus vs Full Stack Developer
    {"id": 3, "candidate_id": 3, "candidate_name": "Marcus Johnson", "requirement_id": 202, "requirement_title": "Full Stack Developer — MedFirst Health", "overall_match_score": 58, "technical_match_score": 62, "experience_match_score": 55, "immigration_match_score": 40, "location_match_score": 50, "availability_match_score": 75, "culture_match_score": 70, "compensation_match_score": 90,
     "matched_skills": [{"skill": "React", "required_level": 70, "candidate_level": 80, "gap": 10}, {"skill": "Python", "required_level": 70, "candidate_level": 60, "gap": -10}, {"skill": "SQL", "required_level": 60, "candidate_level": 60, "gap": 0}],
     "missing_skills": ["Python (below requirement)", "System Design"], "exceeding_skills": ["React"],
     "risk_factors": ["OPT expiring in 6 months", "Wants remote — role is hybrid", "Needs H1B sponsorship"], "recommendation": "partial_fit"},
    # Rajesh vs Backend Engineer (second job)
    {"id": 4, "candidate_id": 1, "candidate_name": "Rajesh Kumar", "requirement_id": 203, "requirement_title": "Backend Engineer — DataFlow Analytics", "overall_match_score": 85, "technical_match_score": 88, "experience_match_score": 82, "immigration_match_score": 65, "location_match_score": 90, "availability_match_score": 85, "culture_match_score": 78, "compensation_match_score": 80,
     "matched_skills": [{"skill": "Python", "required_level": 85, "candidate_level": 90, "gap": 5}, {"skill": "SQL", "required_level": 75, "candidate_level": 80, "gap": 5}, {"skill": "Data Engineering", "required_level": 70, "candidate_level": 80, "gap": 10}],
     "missing_skills": [], "exceeding_skills": ["Python", "Data Engineering"],
     "risk_factors": ["H1B transfer pending"], "recommendation": "good_fit"},
]

# ── Recommended future jobs based on persistent scores ──
_mock_recommended_jobs = [
    {"candidate_id": 1, "candidate_name": "Rajesh Kumar", "recommendations": [
        {"requirement_id": 204, "title": "Data Engineer — CloudScale", "match_score": 87, "reason": "Strong Python (90) and Data Engineering (80) scores match well. SQL (80) exceeds requirement."},
        {"requirement_id": 205, "title": "Backend Lead — FinTech Corp", "match_score": 83, "reason": "Python expertise (90) and system design growth (70→improving). Leadership potential."},
        {"requirement_id": 206, "title": "Python Developer — AI Startup", "match_score": 79, "reason": "Python (90) is strong match. AWS (60) may need assessment for cloud-heavy role."},
    ]},
    {"candidate_id": 2, "candidate_name": "Emily Chen", "recommendations": [
        {"requirement_id": 207, "title": "Staff Engineer — TechGiant", "match_score": 93, "reason": "Expert Python (100), strong system design (80), excellent communication (100). Perfect fit."},
        {"requirement_id": 204, "title": "Data Engineer — CloudScale", "match_score": 78, "reason": "Strong Python but no data engineering score yet. Recommend assessment."},
    ]},
    {"candidate_id": 3, "candidate_name": "Marcus Johnson", "recommendations": [
        {"requirement_id": 208, "title": "Frontend Developer — Remote Co", "match_score": 82, "reason": "Strong React (80), good communication. Remote role matches preference. Immigration risk for non-remote roles."},
    ]},
]


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Question Bank
# ══════════════════════════════════════════════════════════════

@router.get("/questions")
async def get_questions(
    category: Optional[str] = None,
    technology: Optional[str] = None,
    skill_tag: Optional[str] = None,
    is_required: Optional[bool] = None,
):
    """Get question bank with filters."""
    results = _mock_questions
    if category:
        results = [q for q in results if q["category"] == category]
    if technology:
        results = [q for q in results if q.get("technology") and technology.lower() in q["technology"].lower()]
    if skill_tag:
        results = [q for q in results if q.get("skill_tag") and skill_tag.lower() in q["skill_tag"].lower()]
    if is_required is not None:
        results = [q for q in results if q.get("is_required") == is_required]
    return {"items": results, "total": len(results)}


@router.get("/questions/{question_id}")
async def get_question(question_id: int):
    item = next((q for q in _mock_questions if q["id"] == question_id), None)
    return item or {"error": "Not found"}


@router.post("/questions")
async def create_question(question_text: str, category: str, question_type: str = "rating_1_5"):
    return {"id": 70, "question_text": question_text, "category": category, "question_type": question_type, "created": True}


@router.put("/questions/{question_id}")
async def update_question(question_id: int):
    return {"id": question_id, "updated": True}


@router.delete("/questions/{question_id}")
async def deactivate_question(question_id: int):
    return {"id": question_id, "is_active": False}


@router.get("/questions/categories/summary")
async def get_question_categories():
    """Get summary of questions by category."""
    cats: dict = {}
    for q in _mock_questions:
        c = q["category"]
        if c not in cats:
            cats[c] = {"count": 0, "technologies": set()}
        cats[c]["count"] += 1
        if q.get("technology"):
            cats[c]["technologies"].add(q["technology"])
    return {k: {"count": v["count"], "technologies": list(v["technologies"])} for k, v in cats.items()}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Feedback Sessions
# ══════════════════════════════════════════════════════════════

@router.get("/sessions")
async def get_feedback_sessions(
    candidate_id: Optional[int] = None,
    requirement_id: Optional[int] = None,
    feedback_source: Optional[str] = None,
):
    results = _mock_feedback_sessions
    if candidate_id:
        results = [s for s in results if s["candidate_id"] == candidate_id]
    if requirement_id:
        results = [s for s in results if s.get("requirement_id") == requirement_id]
    if feedback_source:
        results = [s for s in results if s["feedback_source"] == feedback_source]
    # Strip answers for list view
    return {"items": [{k: v for k, v in s.items() if k != "answers"} for s in results], "total": len(results)}


@router.get("/sessions/{session_id}")
async def get_feedback_session(session_id: int):
    """Get full feedback session with all answers."""
    item = next((s for s in _mock_feedback_sessions if s["id"] == session_id), None)
    return item or {"error": "Not found"}


@router.post("/sessions")
async def create_feedback_session(
    interview_id: int, candidate_id: int, evaluator_name: str,
    feedback_source: str = "recruiter", requirement_id: Optional[int] = None,
):
    return {"id": 5, "interview_id": interview_id, "candidate_id": candidate_id, "status": "draft", "created": True}


@router.put("/sessions/{session_id}")
async def update_feedback_session(session_id: int):
    return {"id": session_id, "updated": True}


@router.post("/sessions/{session_id}/complete")
async def complete_feedback_session(session_id: int):
    """Mark session complete, compute scores, update persistent scores."""
    return {
        "id": session_id, "is_draft": False, "completed_at": datetime.utcnow().isoformat(),
        "scores_computed": True, "persistent_scores_updated": True,
    }


@router.post("/sessions/{session_id}/answers")
async def submit_answer(session_id: int, question_id: int, answer_rating: Optional[float] = None, answer_text: Optional[str] = None, answer_choice: Optional[str] = None, answer_numeric: Optional[float] = None):
    return {"session_id": session_id, "question_id": question_id, "saved": True}


@router.put("/sessions/{session_id}/answers/{question_id}")
async def update_answer(session_id: int, question_id: int):
    return {"session_id": session_id, "question_id": question_id, "updated": True}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Visibility Controls (Recruiter)
# ══════════════════════════════════════════════════════════════

@router.put("/sessions/{session_id}/visibility")
async def update_visibility(
    session_id: int, visibility: str = "internal_only",
    share_technical_scores: bool = True, share_immigration_details: bool = False,
    share_compensation_details: bool = False, share_detailed_notes: bool = False,
):
    """Recruiter controls what feedback is shared during submission."""
    return {"id": session_id, "visibility": visibility, "share_technical_scores": share_technical_scores, "share_immigration_details": share_immigration_details, "share_compensation_details": share_compensation_details, "share_detailed_notes": share_detailed_notes, "updated": True}


@router.post("/sessions/{session_id}/attach-to-submission")
async def attach_to_submission(session_id: int, submission_id: int):
    """Attach feedback (with visibility controls applied) to a candidate submission."""
    session = next((s for s in _mock_feedback_sessions if s["id"] == session_id), None)
    if not session:
        return {"error": "Session not found"}
    return {
        "session_id": session_id, "submission_id": submission_id,
        "attached": True,
        "shared_fields": {
            "technical_score": session.get("share_technical_scores", True),
            "immigration_details": session.get("share_immigration_details", False),
            "compensation_details": session.get("share_compensation_details", False),
            "detailed_notes": session.get("share_detailed_notes", False),
        },
    }


@router.get("/sessions/{session_id}/shareable-view")
async def get_shareable_view(session_id: int):
    """Get the filtered view of feedback based on visibility settings — what gets shared externally."""
    session = next((s for s in _mock_feedback_sessions if s["id"] == session_id), None)
    if not session:
        return {"error": "Session not found"}
    view: dict = {
        "candidate_name": session["candidate_name"],
        "overall_rating": session["overall_rating"],
        "overall_recommendation": session["overall_recommendation"],
        "strengths": session["strengths"],
    }
    if session.get("share_technical_scores"):
        view["technical_score"] = session["technical_score"]
        view["communication_score"] = session["communication_score"]
        view["job_fit_score"] = session["job_fit_score"]
    if session.get("share_immigration_details"):
        view["immigration_score"] = session["immigration_score"]
    if session.get("share_compensation_details"):
        view["compensation_details"] = True
    if session.get("share_detailed_notes"):
        view["summary_notes"] = session["summary_notes"]
        view["concerns"] = session["concerns"]
    return view


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Persistent Candidate Scores
# ══════════════════════════════════════════════════════════════

@router.get("/persistent-scores")
async def get_persistent_scores(
    candidate_id: Optional[int] = None,
    category: Optional[str] = None,
    technology: Optional[str] = None,
    min_score: Optional[float] = None,
):
    results = _mock_persistent_scores
    if candidate_id:
        results = [s for s in results if s["candidate_id"] == candidate_id]
    if category:
        results = [s for s in results if s["category"] == category]
    if technology:
        results = [s for s in results if technology.lower() in s["skill_or_technology"].lower()]
    if min_score is not None:
        results = [s for s in results if s["current_score"] >= min_score]
    return {"items": results, "total": len(results)}


@router.get("/persistent-scores/candidate/{candidate_id}")
async def get_candidate_score_profile(candidate_id: int):
    """Full score profile for a candidate — all accumulated skill scores."""
    scores = [s for s in _mock_persistent_scores if s["candidate_id"] == candidate_id]
    if not scores:
        return {"error": "No scores found", "candidate_id": candidate_id}
    name = scores[0]["candidate_name"]
    by_category: dict = {}
    for s in scores:
        cat = s["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(s)
    return {
        "candidate_id": candidate_id, "candidate_name": name,
        "total_skills_assessed": len(scores),
        "avg_score": round(sum(s["current_score"] for s in scores) / len(scores), 1),
        "avg_confidence": round(sum(s["confidence_level"] for s in scores) / len(scores), 2),
        "scores_by_category": by_category,
        "all_scores": scores,
    }


@router.post("/persistent-scores/recalculate/{candidate_id}")
async def recalculate_persistent_scores(candidate_id: int):
    """Recalculate all persistent scores from interview feedback history."""
    return {"candidate_id": candidate_id, "recalculated": True, "scores_updated": 7}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Job Match Scores
# ══════════════════════════════════════════════════════════════

@router.get("/job-match")
async def get_job_matches(
    candidate_id: Optional[int] = None,
    requirement_id: Optional[int] = None,
    min_score: Optional[float] = None,
):
    results = _mock_job_matches
    if candidate_id:
        results = [m for m in results if m["candidate_id"] == candidate_id]
    if requirement_id:
        results = [m for m in results if m["requirement_id"] == requirement_id]
    if min_score is not None:
        results = [m for m in results if m["overall_match_score"] >= min_score]
    results.sort(key=lambda x: x["overall_match_score"], reverse=True)
    return {"items": results, "total": len(results)}


@router.get("/job-match/{candidate_id}/{requirement_id}")
async def get_specific_match(candidate_id: int, requirement_id: int):
    item = next((m for m in _mock_job_matches if m["candidate_id"] == candidate_id and m["requirement_id"] == requirement_id), None)
    return item or {"error": "No match score found"}


@router.post("/job-match/compute/{candidate_id}/{requirement_id}")
async def compute_job_match(candidate_id: int, requirement_id: int):
    """Compute/recompute job match score from persistent scores and feedback."""
    return {"candidate_id": candidate_id, "requirement_id": requirement_id, "computed": True, "overall_match_score": 82}


@router.get("/recommendations/{candidate_id}")
async def get_job_recommendations(candidate_id: int, min_score: float = 70):
    """Get recommended jobs for a candidate based on accumulated persistent scores."""
    rec = next((r for r in _mock_recommended_jobs if r["candidate_id"] == candidate_id), None)
    if not rec:
        return {"candidate_id": candidate_id, "recommendations": []}
    filtered = [r for r in rec["recommendations"] if r["match_score"] >= min_score]
    return {"candidate_id": candidate_id, "candidate_name": rec["candidate_name"], "recommendations": filtered}


@router.get("/recommendations/for-job/{requirement_id}")
async def get_candidate_recommendations(requirement_id: int, min_score: float = 60):
    """Get recommended candidates for a job based on their persistent scores."""
    matches = [m for m in _mock_job_matches if m["requirement_id"] == requirement_id and m["overall_match_score"] >= min_score]
    matches.sort(key=lambda x: x["overall_match_score"], reverse=True)
    return {"requirement_id": requirement_id, "candidates": matches, "total": len(matches)}


# ══════════════════════════════════════════════════════════════
#  ENDPOINTS — Dashboard
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def get_feedback_dashboard():
    return {
        "total_feedback_sessions": 4,
        "by_source": {"recruiter": 2, "ai_bot": 2},
        "by_recommendation": {"strong_hire": 1, "hire": 2, "maybe": 1},
        "avg_overall_rating": 4.18,
        "avg_job_fit_score": 79,
        "candidates_assessed": 3,
        "unique_skills_tracked": 12,
        "total_persistent_scores": len(_mock_persistent_scores),
        "avg_confidence": 0.58,
        "top_scorers": [
            {"candidate": "Emily Chen", "avg_score": 87, "skills_assessed": 6},
            {"candidate": "Rajesh Kumar", "avg_score": 74, "skills_assessed": 7},
            {"candidate": "Marcus Johnson", "avg_score": 60, "skills_assessed": 4},
        ],
        "immigration_risk_summary": {
            "no_risk": 1, "moderate_risk": 1, "high_risk": 1,
        },
    }
