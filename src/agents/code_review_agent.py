""" Code review agent: technical/system check before committing the booking.
"""
from datetime import datetime
from state import BookingState
from audit import audit_entry


def precondition(state: BookingState) -> bool:
    return state["booking_status"] == "documents_checked"


def run(state: BookingState) -> BookingState:
    """Review the code before committing the booking."""
    issues = []

    check_in = datetime.strptime(state["check_in"], "%Y-%m-%d")
    check_out = datetime.strptime(state["check_out"], "%Y-%m-%d")
    if check_out <= check_in:
        issues.append("Check-out date must be after check-in date")

    if state["adults"] <= 0:
        issues.append("At least one adult must be specified")

    if state["children"] is not None and state["children"] < 0:
        issues.append("Children count must be non-negative")

    if state["budget_per_night"] <= 0:
        issues.append("Budget per night must be positive")

    if state["candidate_hotels"] is None or len(state["candidate_hotels"]) == 0:
        issues.append("No candidate hotels found")

    new_state = {
        **state,
        "technical_issues": issues,
        "booking_status": "technical_issues_found" if issues else "code_reviewed",
    }

    return {**new_state, "audit_log": [audit_entry("agent_code_review", "code_reviewed", new_state)]}
