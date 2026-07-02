"""The Blackboard: shared global state + read-only Shared Parameters.

`BookingState` is the single source of truth. Knowledge sources (agents) never
talk to each other directly; they only read from and write to this state.

`shared_parameters` are *control* values, not blackboard data. They live in
`config["configurable"]["params"]` so agents can read them but never mutate
them.
"""

import operator
from typing import Annotated, Optional, TypedDict

"""
BookingState is the blackboard. It contains the state of the booking process.
"""


class BookingState(TypedDict):
    # raw input
    user_request: str

    # parsed booking request
    destination: Optional[str]
    check_in: Optional[str]
    check_out: Optional[str]
    adults: Optional[int]
    budget_per_night: Optional[int]
    preferences: list[str]

    # solution / partial results posted to the blackboard
    booking_status: str
    candidate_hotels: list[dict]
    documents_status: str
    missing_fields: list[str]
    technical_issues: list[str]
    support_response: Optional[str]
    risk_score: float
    confidence_score: float
    requires_human_approval: bool

    # append-only audit trail;
    audit_log: Annotated[list[dict], operator.add]

    # How many dispatch loops have happened in this run
    iterations: int

    # customer information fields
    full_name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]


# Shared Parameters -- read-only control values shared by all agents + policy.
shared_parameters: dict = {
    "confidence_threshold": 0.75,
    "risk_threshold": 0.6,
    "max_iterations": 3,
    "approval_required_for_payment": True,
    "free_cancellation_required": True,
    "currency": "EUR"
}


def initial_state(user_request: str) -> BookingState:
    """Build a fresh blackboard."""

    initial_booking_state: BookingState = {
        "user_request": user_request,
        "destination": None,
        "check_in": None,
        "check_out": None,
        "adults": None,
        "budget_per_night": None,
        "preferences": [],
        "booking_status": "new_request",
        "candidate_hotels": [],
        "documents_status": "pending",
        "missing_fields": [],
        "technical_issues": [],
        "support_response": None,
        "risk_score": 0.0,
        "confidence_score": 0.0,
        "requires_human_approval": False,
        "audit_log": [],
        "iterations": 0,
        "full_name": None,
        "email": None,
        "phone_number": None,
    }

    return initial_booking_state
