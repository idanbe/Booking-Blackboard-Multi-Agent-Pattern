"""Decentralized audit logging.

Each knowledge source returns its own audit entry *inside* its state update,
"""

from datetime import datetime, timezone


def audit_entry(actor: str, action: str, state: dict) -> dict:
    """Snapshot the decision-relevant slice of the blackboard at action time."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "action": action,
        "booking_status": state.get("booking_status"),
        "confidence_score": state.get("confidence_score"),
        "risk_score": state.get("risk_score"),
    }
