"""
Duplicate Candidate Detection Agent — Prevents same candidate
from being submitted by multiple suppliers for the same requirement.

Uses fuzzy matching on name, email, phone, and LinkedIn URL.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DuplicateResult:
    """Result of duplicate detection."""
    candidate_id: int
    is_duplicate: bool
    confidence: float  # 0-100
    matched_with: Optional[int] = None  # ID of the matching candidate
    match_fields: List[str] = None  # Which fields matched
    recommendation: str = "UNIQUE"  # UNIQUE, POTENTIAL_DUPLICATE, CONFIRMED_DUPLICATE

    def __post_init__(self):
        if self.match_fields is None:
            self.match_fields = []


class DuplicateDetectorAgent:
    """
    Detects duplicate candidates across supplier submissions.
    Prevents the same person from being submitted by multiple suppliers.
    """

    FIELD_WEIGHTS = {
        "email": 40,
        "phone": 25,
        "name": 20,
        "linkedin": 15,
    }

    THRESHOLDS = {
        "CONFIRMED_DUPLICATE": 80,
        "POTENTIAL_DUPLICATE": 50,
    }

    def check_for_duplicates(
        self,
        candidate: Dict[str, Any],
        existing_candidates: List[Dict[str, Any]],
    ) -> DuplicateResult:
        """
        Check if a candidate is a duplicate of any existing candidates.
        
        Args:
            candidate: dict with keys: id, email, phone, first_name, last_name, linkedin_url
            existing_candidates: list of dicts with same keys
        """
        best_match = None
        best_score = 0
        best_fields = []

        for existing in existing_candidates:
            if existing.get("id") == candidate.get("id"):
                continue  # Skip self

            score, fields = self._compare_candidates(candidate, existing)

            if score > best_score:
                best_score = score
                best_match = existing.get("id")
                best_fields = fields

        # Determine result
        if best_score >= self.THRESHOLDS["CONFIRMED_DUPLICATE"]:
            recommendation = "CONFIRMED_DUPLICATE"
            is_duplicate = True
        elif best_score >= self.THRESHOLDS["POTENTIAL_DUPLICATE"]:
            recommendation = "POTENTIAL_DUPLICATE"
            is_duplicate = True
        else:
            recommendation = "UNIQUE"
            is_duplicate = False

        result = DuplicateResult(
            candidate_id=candidate.get("id", 0),
            is_duplicate=is_duplicate,
            confidence=round(best_score, 1),
            matched_with=best_match if is_duplicate else None,
            match_fields=best_fields,
            recommendation=recommendation,
        )

        if is_duplicate:
            logger.warning(
                f"Duplicate detected: candidate {candidate.get('id')} "
                f"matches {best_match} ({recommendation}, confidence={best_score}%)"
            )

        return result

    def _compare_candidates(
        self, a: Dict[str, Any], b: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Compare two candidates and return similarity score and matching fields."""
        score = 0
        matched_fields = []

        # Email match (exact)
        if self._normalize_email(a) and self._normalize_email(a) == self._normalize_email(b):
            score += self.FIELD_WEIGHTS["email"]
            matched_fields.append("email")

        # Phone match (normalized)
        if self._normalize_phone(a) and self._normalize_phone(a) == self._normalize_phone(b):
            score += self.FIELD_WEIGHTS["phone"]
            matched_fields.append("phone")

        # Name match (fuzzy)
        name_sim = self._name_similarity(a, b)
        if name_sim >= 0.85:
            score += self.FIELD_WEIGHTS["name"]
            matched_fields.append("name")
        elif name_sim >= 0.7:
            score += self.FIELD_WEIGHTS["name"] * 0.5
            matched_fields.append("name_partial")

        # LinkedIn match
        if self._normalize_linkedin(a) and self._normalize_linkedin(a) == self._normalize_linkedin(b):
            score += self.FIELD_WEIGHTS["linkedin"]
            matched_fields.append("linkedin")

        return score, matched_fields

    def _normalize_email(self, candidate: Dict) -> Optional[str]:
        """Normalize email for comparison."""
        email = candidate.get("email", "")
        if not email:
            return None
        return email.lower().strip()

    def _normalize_phone(self, candidate: Dict) -> Optional[str]:
        """Normalize phone number — strip non-digits."""
        phone = candidate.get("phone", "")
        if not phone:
            return None
        digits = re.sub(r'\D', '', phone)
        if len(digits) > 10:
            digits = digits[-10:]  # Take last 10 digits
        return digits if len(digits) >= 7 else None

    def _normalize_linkedin(self, candidate: Dict) -> Optional[str]:
        """Normalize LinkedIn URL."""
        url = candidate.get("linkedin_url", "")
        if not url:
            return None
        # Extract the profile path
        match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-]+)', url)
        return match.group(1).lower() if match else None

    def _name_similarity(self, a: Dict, b: Dict) -> float:
        """Calculate name similarity using simple token overlap."""
        name_a = f"{a.get('first_name', '')} {a.get('last_name', '')}".lower().strip()
        name_b = f"{b.get('first_name', '')} {b.get('last_name', '')}".lower().strip()

        if not name_a or not name_b:
            return 0

        tokens_a = set(name_a.split())
        tokens_b = set(name_b.split())

        if not tokens_a or not tokens_b:
            return 0

        overlap = len(tokens_a.intersection(tokens_b))
        total = max(len(tokens_a), len(tokens_b))

        return overlap / total if total > 0 else 0

    def batch_check(
        self, candidates: List[Dict[str, Any]]
    ) -> List[DuplicateResult]:
        """Check a batch of candidates for duplicates among themselves."""
        results = []

        for i, candidate in enumerate(candidates):
            others = candidates[:i] + candidates[i+1:]
            result = self.check_for_duplicates(candidate, others)
            results.append(result)

        return results
