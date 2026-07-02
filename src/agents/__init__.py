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
from agents import parse_user_request

KNOWLEDGE_SOURCES = [
    {
        "name": "parse_user_request",
        "precondition": parse_user_request.precondition,
        "agent": parse_user_request.agent,
    },
]

__all__ = ["KNOWLEDGE_SOURCES"]
