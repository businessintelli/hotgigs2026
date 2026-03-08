"""Auto interview scheduling agent — recommends optimal interview slots."""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


@dataclass
class InterviewSlotRecommendation:
    recommended_slots: List[Dict[str, Any]] = field(default_factory=list)
    timezone_match_score: float = 0.0
    urgency_score: float = 0.0
    top_recommendation: Optional[Dict[str, Any]] = None
    details: Dict[str, Any] = field(default_factory=dict)


class AutoInterviewSchedulingAgent:
    BUSINESS_HOURS = (9, 17)  # 9am - 5pm
    MIN_BUFFER_MINUTES = 30
    SLOT_DURATION_MINUTES = 60

    def recommend_slots(
        self,
        candidate_availability: List[Dict[str, Any]],
        interviewer_timezone: str = "America/New_York",
        candidate_timezone: str = "America/New_York",
        urgency_level: str = "normal",
        existing_interviews: Optional[List[Dict[str, Any]]] = None,
        num_slots: int = 5,
    ) -> InterviewSlotRecommendation:
        if not candidate_availability:
            return InterviewSlotRecommendation(
                details={"error": "No candidate availability provided"})

        # Calculate timezone offset penalty
        tz_offsets = {"America/New_York": -5, "America/Chicago": -6, "America/Denver": -7,
                      "America/Los_Angeles": -8, "Europe/London": 0, "Europe/Berlin": 1,
                      "Asia/Kolkata": 5.5, "Asia/Tokyo": 9, "Australia/Sydney": 11}

        i_offset = tz_offsets.get(interviewer_timezone, 0)
        c_offset = tz_offsets.get(candidate_timezone, 0)
        tz_diff = abs(i_offset - c_offset)
        tz_score = max(0, 100 - tz_diff * 15)

        # Urgency scoring
        urgency_scores = {"critical": 100, "high": 75, "normal": 50, "low": 25}
        urgency = urgency_scores.get(urgency_level, 50)

        # Generate candidate slots
        slots = []
        for avail in candidate_availability:
            date_str = avail.get("date", "")
            start_hour = avail.get("start_hour", self.BUSINESS_HOURS[0])
            end_hour = avail.get("end_hour", self.BUSINESS_HOURS[1])

            for hour in range(max(start_hour, self.BUSINESS_HOURS[0]),
                            min(end_hour, self.BUSINESS_HOURS[1])):
                slot = {
                    "date": date_str,
                    "start_time": f"{hour:02d}:00",
                    "end_time": f"{hour+1:02d}:00",
                    "timezone": candidate_timezone,
                    "score": 0,
                }

                # Prefer morning (10-12) and early afternoon (14-16)
                if 10 <= hour <= 12:
                    slot["score"] += 30
                elif 14 <= hour <= 16:
                    slot["score"] += 25
                else:
                    slot["score"] += 15

                # Sooner is better for urgent
                slot["score"] += urgency * 0.3

                # Timezone overlap bonus
                slot["score"] += tz_score * 0.2

                # Check buffer against existing interviews
                if existing_interviews:
                    has_conflict = False
                    for ei in existing_interviews:
                        if ei.get("date") == date_str:
                            ei_hour = int(ei.get("start_time", "00:00").split(":")[0])
                            if abs(hour - ei_hour) < 1:
                                has_conflict = True
                                break
                    if has_conflict:
                        continue

                slots.append(slot)

        # Sort by score descending, take top N
        slots.sort(key=lambda s: s["score"], reverse=True)
        top_slots = slots[:num_slots]

        return InterviewSlotRecommendation(
            recommended_slots=top_slots,
            timezone_match_score=round(tz_score, 1),
            urgency_score=urgency,
            top_recommendation=top_slots[0] if top_slots else None,
            details={"total_available_slots": len(slots), "timezone_diff_hours": tz_diff},
        )
