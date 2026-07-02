from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from state import BookingState
from agents import KNOWLEDGE_SOURCES
from policy import policy


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


def create_graph() -> StateGraph:
    graph = StateGraph(BookingState)

    ROUTING_MAP: dict[str, str] = {
        "policy": "policy",
    }

    # graph.add_node("dispatcher", dispatcher)
    # graph.add_node("iterations_increment", iterations_increment)
    # graph.add_node("policy", policy)

    # Add the knowledge sources to the graph and to the routing map
    for knowledge_source in KNOWLEDGE_SOURCES:
        ROUTING_MAP[knowledge_source["name"]] = knowledge_source["name"]
        graph.add_node(knowledge_source["name"], knowledge_source["agent"])
        graph.add_edge(knowledge_source["name"], "controller")

    graph.add_edge(START, "controller")
    graph.add_node("controller", iterations_increment)
    graph.add_conditional_edges("controller", controller_route, ROUTING_MAP)

    graph.add_node("policy", policy)
    graph.add_edge("policy", END)

    return graph.compile(checkpointer=MemorySaver())
