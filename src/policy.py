from langchain_core.runnables import RunnableConfig
from state import BookingState


def policy(state: BookingState, config: RunnableConfig) -> dict:
    """Final gate: decide whether the booking can proceed or needs human review."""
    params = config["configurable"]["params"]
    confidence_threshold = params["confidence_threshold"]
    risk_threshold = params["risk_threshold"]

    requires_approval = (
        state["confidence_score"] < confidence_threshold
        or state["risk_score"] > risk_threshold
        or params["approval_required_for_payment"]
    )

    return {
        "requires_human_approval": requires_approval,
        "booking_status": "pending_approval" if requires_approval else "ready",
    }
