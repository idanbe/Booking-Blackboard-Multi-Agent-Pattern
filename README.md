# Booking – Blackboard Multi-Agent Pattern

A booking system built with [LangGraph](https://github.com/langchain-ai/langgraph) that demonstrates the **Blackboard architecture pattern**: independent agents (parsing, risk, document verification, code review, booking) communicate indirectly by reading from and writing to a shared state — the "blackboard" — rather than calling each other directly.

## Agents

- `parse_request_agent` – parses the raw user request off the blackboard
- `risk_agent` – aggregates a risk score from what other agents posted
- `document_verification_agent` – verifies supporting documents
- `code_review_agent` – reviews generated code/output
- `booking_agent` – finalizes the booking decision

## Running

```bash
uv run app
```
