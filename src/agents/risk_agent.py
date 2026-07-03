""" Risk Agent: Aggregate a risk score from what the other sources posted to the blackboard.
"""
from langchain_core.runnables import RunnableConfig
from state import BookingState
from audit import audit_entry


def precondition(state: BookingState) -> bool:
    return state["booking_status"] == "code_reviewed"


def run(state: BookingState, config: RunnableConfig) -> BookingState:
    """Aggregate a risk score from what the other sources posted to the blackboard."""
    shared_parameters = config["configurable"]["params"]
    risk_score = 0.0

    if state["documents_status"] == "missing_fields":
        risk_score += 0.4
    if not state["candidate_hotels"]:
        risk_score += 0.3
    if state["confidence_score"] < shared_parameters["confidence_threshold"]:
        risk_score += 0.2
    if state["technical_issues"]:
        risk_score += 0.3

    risk_score = round(risk_score, 2)
    requires_human_approval = risk_score >= shared_parameters["risk_threshold"]

    new_state = {**state, "risk_score": risk_score,
                 "requires_human_approval": requires_human_approval,
                 "booking_status": "risk_scored"}
    return {**new_state, "audit_log": [audit_entry("agent_risk", "risk_scored", new_state)]}
