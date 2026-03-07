"""
Requirement Matching Agent — AI-powered candidate-to-requirement matching.

Scores supplier-submitted candidates against client requirements using
skill overlap, experience alignment, location, rate, and availability.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of matching a candidate to a requirement."""
    overall_score: float  # 0-100
    recommendation: str   # STRONG_MATCH, MODERATE_MATCH, WEAK_MATCH, AUTO_REJECT
    skill_score: float
    experience_score: float
    location_score: float
    rate_score: float
    availability_score: float
    details: Dict[str, Any] = field(default_factory=dict)


class RequirementMatchingAgent:
    """
    Scores candidates against requirements using weighted criteria.
    
    Weights:
      - Skills: 35%
      - Experience: 25%
      - Rate: 15%
      - Location: 15%
      - Availability: 10%
    """

    WEIGHTS = {
        "skills": 0.35,
        "experience": 0.25,
        "rate": 0.15,
        "location": 0.15,
        "availability": 0.10,
    }

    THRESHOLDS = {
        "STRONG_MATCH": 75,
        "MODERATE_MATCH": 50,
        "WEAK_MATCH": 25,
    }

    def match(
        self,
        candidate_data: Dict[str, Any],
        requirement_data: Dict[str, Any],
    ) -> MatchResult:
        """
        Score a candidate against a requirement.
        
        Args:
            candidate_data: dict with keys: skills, experience_years, location,
                           expected_rate, availability_date, education, certifications
            requirement_data: dict with keys: required_skills, nice_to_have_skills,
                             min_experience, max_experience, location, remote_ok,
                             budget_min, budget_max, start_date
        """
        skill_score = self._score_skills(candidate_data, requirement_data)
        exp_score = self._score_experience(candidate_data, requirement_data)
        rate_score = self._score_rate(candidate_data, requirement_data)
        loc_score = self._score_location(candidate_data, requirement_data)
        avail_score = self._score_availability(candidate_data, requirement_data)

        overall = (
            skill_score * self.WEIGHTS["skills"]
            + exp_score * self.WEIGHTS["experience"]
            + rate_score * self.WEIGHTS["rate"]
            + loc_score * self.WEIGHTS["location"]
            + avail_score * self.WEIGHTS["availability"]
        )

        # Determine recommendation
        if overall >= self.THRESHOLDS["STRONG_MATCH"]:
            recommendation = "STRONG_MATCH"
        elif overall >= self.THRESHOLDS["MODERATE_MATCH"]:
            recommendation = "MODERATE_MATCH"
        elif overall >= self.THRESHOLDS["WEAK_MATCH"]:
            recommendation = "WEAK_MATCH"
        else:
            recommendation = "AUTO_REJECT"

        # Check hard disqualifiers
        missing_must_haves = self._get_missing_must_haves(candidate_data, requirement_data)
        if len(missing_must_haves) > 2:
            recommendation = "AUTO_REJECT"
            overall = min(overall, 20)

        result = MatchResult(
            overall_score=round(overall, 1),
            recommendation=recommendation,
            skill_score=round(skill_score, 1),
            experience_score=round(exp_score, 1),
            location_score=round(loc_score, 1),
            rate_score=round(rate_score, 1),
            availability_score=round(avail_score, 1),
            details={
                "missing_must_haves": missing_must_haves,
                "matching_skills": self._get_matching_skills(candidate_data, requirement_data),
            },
        )

        logger.info(
            f"Match result: score={result.overall_score}, rec={result.recommendation}"
        )
        return result

    def _normalize_skills(self, skills: List[str]) -> set:
        """Normalize skill names for comparison."""
        return {s.lower().strip() for s in skills if s}

    def _score_skills(self, candidate: Dict, requirement: Dict) -> float:
        """Score skill overlap (0-100)."""
        cand_skills = self._normalize_skills(candidate.get("skills", []))
        req_skills = self._normalize_skills(requirement.get("required_skills", []))
        nice_skills = self._normalize_skills(requirement.get("nice_to_have_skills", []))

        if not req_skills:
            return 70  # No requirements = neutral score

        # Must-have coverage (70% weight)
        must_have_matches = len(cand_skills.intersection(req_skills))
        must_have_score = (must_have_matches / len(req_skills)) * 100 if req_skills else 0

        # Nice-to-have bonus (30% weight)
        nice_matches = len(cand_skills.intersection(nice_skills))
        nice_score = (nice_matches / len(nice_skills)) * 100 if nice_skills else 50

        return must_have_score * 0.7 + nice_score * 0.3

    def _score_experience(self, candidate: Dict, requirement: Dict) -> float:
        """Score experience level alignment (0-100)."""
        cand_exp = candidate.get("experience_years", 0)
        min_exp = requirement.get("min_experience", 0)
        max_exp = requirement.get("max_experience", 20)

        if min_exp <= cand_exp <= max_exp:
            return 100
        elif cand_exp < min_exp:
            gap = min_exp - cand_exp
            return max(0, 100 - gap * 20)  # Lose 20 points per year under
        else:
            over = cand_exp - max_exp
            return max(60, 100 - over * 5)  # Minor penalty for overqualified

    def _score_rate(self, candidate: Dict, requirement: Dict) -> float:
        """Score rate alignment (0-100)."""
        cand_rate = candidate.get("expected_rate", 0)
        budget_min = requirement.get("budget_min", 0)
        budget_max = requirement.get("budget_max", 999999)

        if not cand_rate or not budget_max:
            return 70  # No rate info = neutral

        if budget_min <= cand_rate <= budget_max:
            return 100
        elif cand_rate < budget_min:
            return 90  # Under budget is fine
        else:
            over_pct = ((cand_rate - budget_max) / budget_max) * 100 if budget_max else 0
            return max(0, 100 - over_pct * 2)

    def _score_location(self, candidate: Dict, requirement: Dict) -> float:
        """Score location compatibility (0-100)."""
        if requirement.get("remote_ok", False):
            return 100

        cand_loc = (candidate.get("location") or "").lower()
        req_loc = (requirement.get("location") or "").lower()

        if not cand_loc or not req_loc:
            return 60

        if cand_loc == req_loc:
            return 100
        elif any(part in cand_loc for part in req_loc.split(",")):
            return 80
        else:
            return 30

    def _score_availability(self, candidate: Dict, requirement: Dict) -> float:
        """Score availability alignment (0-100)."""
        cand_avail = candidate.get("availability_date")
        req_start = requirement.get("start_date")

        if not cand_avail or not req_start:
            return 70

        # If candidate is available before or on start date
        if str(cand_avail) <= str(req_start):
            return 100
        else:
            return 50

    def _get_missing_must_haves(self, candidate: Dict, requirement: Dict) -> List[str]:
        """Get list of required skills candidate is missing."""
        cand_skills = self._normalize_skills(candidate.get("skills", []))
        req_skills = self._normalize_skills(requirement.get("required_skills", []))
        return list(req_skills - cand_skills)

    def _get_matching_skills(self, candidate: Dict, requirement: Dict) -> List[str]:
        """Get list of matching skills."""
        cand_skills = self._normalize_skills(candidate.get("skills", []))
        req_skills = self._normalize_skills(requirement.get("required_skills", []))
        nice_skills = self._normalize_skills(requirement.get("nice_to_have_skills", []))
        all_req = req_skills | nice_skills
        return list(cand_skills.intersection(all_req))
