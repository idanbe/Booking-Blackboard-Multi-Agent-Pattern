"""Knowledge Sources (agent nodes) registry.

Each agent is an independent specialist living in its own module in this
package. It receives the blackboard (`BookingState`), reads the read-only
Shared Parameters from `config`, and returns a *partial* update containing
only the fields it owns plus an audit entry. Agents never reference one
another -- all communication is indirect, through the blackboard.

Every agent module exposes a `precondition` function and an `agent`
function. This file imports each of them and wires them into the
`KNOWLEDGE_SOURCE` dicts that make up the single `KNOWLEDGE_SOURCES` list
consumed by the graph.
"""
from agents import parse_request_agent
from agents import booking_agent
from agents import document_verification_agent
from agents import code_review_agent
from agents import risk_agent

KNOWLEDGE_SOURCES = [
    {
        "name": "parse_request_agent",
        "precondition": parse_request_agent.precondition,
        "agent": parse_request_agent.run,
    },
    {
        "name": "booking_agent",
        "precondition": booking_agent.precondition,
        "agent": booking_agent.run,
    },
    {
        "name": "document_verification_agent",
        "precondition": document_verification_agent.precondition,
        "agent": document_verification_agent.run,
    },
    {
        "name": "code_review_agent",
        "precondition": code_review_agent.precondition,
        "agent": code_review_agent.run,
    },
    {
        "name": "risk_agent",
        "precondition": risk_agent.precondition,
        "agent": risk_agent.run,
    },
]

__all__ = ["KNOWLEDGE_SOURCES"]
