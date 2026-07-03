from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from state import BookingState
from agents import KNOWLEDGE_SOURCES
from policy import policy, POLICY_ROUTING_MAP
from audit import audit_entry


def iterations_increment(state: BookingState) -> dict:
    """Bookkeeping node: advances the iteration counter used by the loop guard."""
    return {"iterations": state["iterations"] + 1}


def controller_route(state: BookingState, config: RunnableConfig) -> str:
    """Pick the first eligible knowledge source, else hand off to the Policy.

    A `max_iterations` guard (Shared Parameter) bails out to the Policy if a
    mis-specified precondition would otherwise loop forever.
    """
    params = config["configurable"]["params"]
    max_iterations = params["max_iterations"]

    if state["iterations"] >= max_iterations * len(KNOWLEDGE_SOURCES):
        return "policy"

    for knowledge_source in KNOWLEDGE_SOURCES:
        if knowledge_source["precondition"](state):
            return knowledge_source["name"]

    return "policy"


# --------------------------------------------------------------------------- #
# Terminal nodes
# --------------------------------------------------------------------------- #
def finalize(state: BookingState) -> BookingState:
    print(f"[ACTION] Booking confirmed for {state['destination']} "
          f"({len(state['candidate_hotels'])} candidate hotels).")

    new_state = {**state, "booking_status": "ready_to_book"}
    return {
        "booking_status": "ready_to_book",
        "audit_log": [audit_entry("finalize", "proceed_to_booking", new_state)],
    }


def request_documents(state: BookingState) -> dict:
    print(
        f"[ACTION] Requesting missing documents from customer: {state['missing_fields']}")
    new_state = {**state, "booking_status": "waiting_for_missing_documents"}
    return {
        "booking_status": "waiting_for_missing_documents",
        "audit_log": [audit_entry("request_documents", "request_missing_documents", new_state)],
    }


def request_clarification(state: BookingState) -> dict:
    print("[ACTION] Asking the customer a clarifying question.")
    new_state = {**state, "booking_status": "waiting_for_clarification"}
    return {
        "booking_status": "waiting_for_clarification",
        "audit_log": [audit_entry("request_clarification", "ask_clarifying_question", new_state)],
    }


def stop_due_to_technical_issues(state: BookingState) -> dict:
    print(
        f"[ACTION] Stopping: technical issues detected: {state['technical_issues']}")
    new_state = {**state, "booking_status": "stopped_technical_issue"}
    return {
        "booking_status": "stopped_technical_issue",
        "audit_log": [audit_entry("stop_technical", "stop_due_to_technical_issue", new_state)],
    }


def human_gate(state: BookingState) -> dict:
    """Human-in-the-Loop: Escalation feeding an Approval Gate.
    `interrupt()` genuinely halts execution (checkpointer + thread_id come from
    the compiled graph and invoke config) until a human resumes with
    `Command(resume=<decision>)`.
    """
    decision = interrupt({
        "reason": "risk_score exceeded risk_threshold",
        "booking_status": state["booking_status"],
        "risk_score": state["risk_score"],
        "missing_fields": state["missing_fields"],
    })

    approved = decision == "approve"
    new_state = {
        **state,
        "booking_status": "ready_to_book" if approved else "rejected_by_human",
        "requires_human_approval": False,
    }
    return {
        "booking_status": new_state["booking_status"],
        "requires_human_approval": False,
        "audit_log": [audit_entry("human_gate", str(decision), new_state,
                                  {"decision": decision})],
    }


# --------------------------------------------------------------------------- #
# Graph construction.
# --------------------------------------------------------------------------- #
def create_graph() -> StateGraph:
    graph = StateGraph(BookingState)

    ROUTING_MAP: dict[str, str] = {
        "policy": "policy",
    }

    # Add the knowledge sources to the graph and to the routing map
    for knowledge_source in KNOWLEDGE_SOURCES:
        ROUTING_MAP[knowledge_source["name"]] = knowledge_source["name"]
        graph.add_node(knowledge_source["name"], knowledge_source["agent"])
        graph.add_edge(knowledge_source["name"], "controller")

    graph.add_edge(START, "controller")
    graph.add_node("controller", iterations_increment)
    graph.add_conditional_edges("controller", controller_route, ROUTING_MAP)

    graph.add_node("policy", lambda state: {})
    graph.add_conditional_edges("policy", policy, POLICY_ROUTING_MAP)

    # Terminal outcome nodes
    graph.add_node("finalize", finalize)
    graph.add_node("human_gate", human_gate)
    graph.add_node("request_documents", request_documents)
    graph.add_node("request_clarification", request_clarification)
    graph.add_node("stop_technical", stop_due_to_technical_issues)
    for terminal in ("finalize", "human_gate", "request_documents",
                     "request_clarification", "stop_technical"):
        graph.add_edge(terminal, END)

    return graph.compile(checkpointer=MemorySaver())
