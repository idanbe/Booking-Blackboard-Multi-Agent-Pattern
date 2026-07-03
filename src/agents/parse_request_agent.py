"""Parse User Request: knowledge source that extracts structured booking
fields (destination, dates, party size, preferences, ...) from the raw free
text `user_request` on the blackboard.
"""
from state import BookingState
from audit import audit_entry


def precondition(state: BookingState) -> bool:
    return state["booking_status"] == "new_request"


def run(state: BookingState) -> BookingState:
    """Parse the user request and return a partial update containing the parsed fields."""

    mock_user_request_parsed_fields = {
        "destination": "Jerusalem",
        "check_in": "2026-07-02",
        "check_out": "2026-07-05",
        "adults": 2,
        "budget_per_night": 100,
        "preferences": ["breakfast", "wifi"],
        "confidence_score": 0.85,
        "booking_status": "request_parsed",
    }

    new_state = {**state, **mock_user_request_parsed_fields}
    details = {
        "destination": new_state["destination"],
        "check_in": new_state["check_in"],
        "check_out": new_state["check_out"],
        "adults": new_state["adults"],
        "budget_per_night": new_state["budget_per_night"],
        "preferences": new_state["preferences"],
    }

    return {
        **mock_user_request_parsed_fields,
        "audit_log": [
            audit_entry("agent_parse_user_request",
                        "user_request_parsed", new_state, details)
        ],
    }
