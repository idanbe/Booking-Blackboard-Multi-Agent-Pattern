""" Booking Agent: knowledge source that books a hotel based on the parsed fields.
"""
from langchain_core.runnables import RunnableConfig
from state import BookingState
from audit import audit_entry


def precondition(state: BookingState) -> bool:
    return state["booking_status"] == "hotels_found" and state["documents_status"] == "not_checked"


def run(state: BookingState) -> BookingState:
    """Verify the customer documents required to book."""
    required_fields = [
        "full_name",
        "email",
        "phone_number",
    ]

    missing_fields = [
        field for field in required_fields if state.get(field) is None]

    if missing_fields:
        return {
            **state,
            "missing_fields": missing_fields,
            "documents_status": "missing_fields",
            "booking_status": "documents_incomplete",
            "audit_log": [
                audit_entry("agent_document_verification",
                            "documents_incomplete", state)
            ],
        }
    else:
        return {
            **state,
            "missing_fields": [],
            "documents_status": "verified",
            "booking_status": "documents_checked",
            "audit_log": [
                audit_entry("agent_document_verification",
                            "documents_checked", state)
            ],
        }
