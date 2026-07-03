from langchain_core.runnables import RunnableConfig
from state import BookingState


def policy(state: BookingState, config: RunnableConfig) -> dict:
    """Final gate: decide whether the booking can proceed or needs human review."""
    shared_parameters = config["configurable"]["params"]

    if state["technical_issues"]:
        return "stop_due_to_technical_issues"
    if state["risk_score"] > shared_parameters["risk_threshold"]:
        return "escalate_to_human"
    if state["documents_status"] == "missing_fields":
        return "request_missing_documents"
    if state["confidence_score"] < shared_parameters["confidence_threshold"]:
        return "ask_clarifying_questions"
    if state["candidate_hotels"] is None or len(state["candidate_hotels"]) == 0:
        return "ask_to_relax_constraints"
    return "proceed"


POLICY_ROUTING_MAP: dict[str, str] = {
    "stop_due_to_technical_issues": "stop_technical",
    "escalate_to_human": "human_gate",
    "request_missing_documents": "request_documents",
    "ask_clarifying_questions": "request_clarification",
    "ask_to_relax_constraints": "request_clarification",
    "proceed": "finalize",
}
