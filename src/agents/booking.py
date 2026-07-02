""" Booking Agent: knowledge source that books a hotel based on the parsed fields.
"""
from langchain_core.runnables import RunnableConfig
from state import BookingState
from audit import audit_entry

MOCK_HOTELS: list[dict] = [
    {"name": "Hotel Aurora", "price_per_night": 90, "free_cancellation": True},
    {"name": "Hotel Borealis", "price_per_night": 120, "free_cancellation": True},
    {"name": "Hotel Celeste", "price_per_night": 150, "free_cancellation": False},
]


def precondition(state: BookingState) -> bool:
    return state["booking_status"] == "request_parsed" and state["destination"] is not None


def agent(state: BookingState, config: RunnableConfig) -> BookingState:
    """filter hotels based on the parsed fields and shared_parameters"""
    shared_parameters = config["configurable"]["params"]

    filtered_hotels: list[dict] = []
    for hotel in MOCK_HOTELS:
        if (hotel["price_per_night"] <= state["budget_per_night"]
                and (hotel["free_cancellation"] == shared_parameters["free_cancellation_required"]
                     or shared_parameters["free_cancellation"] is None)):
            filtered_hotels.append(hotel)

    return {
        **state,
        "candidate_hotels": filtered_hotels,
        "booking_status": "hotels_found",
        "confidence_score": (0.82 if filtered_hotels else 0.45),
        "audit_log": [
            audit_entry("agent_booking", "hotels_found", state)
        ],
    }
