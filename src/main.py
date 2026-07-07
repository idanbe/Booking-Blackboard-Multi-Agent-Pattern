import json
import uuid
from pathlib import Path
from typing import Optional

from langgraph.types import Command

from state import initial_state, shared_parameters, BookingState
from controller import create_graph

OUTPUT_PATH = Path(__file__).parent / "outputs" / "run_output.json"


def write_result_to_file(result: dict, output_path: Path = OUTPUT_PATH) -> None:
    """save the result state to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, default=str))


BASE_REQUEST = "I want to book a hotel in Jerusalem for 2 nights in July"

SCENARIOS: list[dict] = [
    {
        "label": "Missing phone",
        "state_overrides": {"phone_number": None},
        "param_overrides": {},
    },
    {
        "label": "Happy path",
        "state_overrides": {"phone_number": "+351 912 345 678"},
        "param_overrides": {},
    },
    {
        "label": "Low risk tolerance (escalates to human)",
        "state_overrides": {"phone_number": None},
        "param_overrides": {"risk_threshold": 0.3},
    },
]


def render_menu() -> str:
    """Build the printable, numbered scenario menu."""
    lines = ["Select a scenario:"]
    for index, scenario in enumerate(SCENARIOS, start=1):
        lines.append(f"  {index}. {scenario['label']}")
    return "\n".join(lines)


def parse_menu_choice(raw: str, num_options: int) -> Optional[int]:
    """Return the 0-based scenario index for valid input, else None."""
    raw = raw.strip()
    if not raw.isdecimal():
        return None
    choice = int(raw)
    if 1 <= choice <= num_options:
        return choice - 1
    return None


def build_scenario_inputs(scenario: dict) -> tuple[BookingState, dict]:
    """Build the (state, config) pair for a scenario, applying its overrides."""
    state = initial_state(BASE_REQUEST)
    state.update(scenario["state_overrides"])
    params = {**shared_parameters, **scenario["param_overrides"]}
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "params": params,
        }
    }
    return state, config


def run_scenario(scenario: dict) -> dict:
    """Run a single scenario end to end and return the final result."""
    print(f"\n=== Running: {scenario['label']} ===")
    state, config = build_scenario_inputs(scenario)
    app = create_graph()
    result = app.invoke(state, config=config)

    if "__interrupt__" in result:
        print(f"[HUMAN GATE] {result['__interrupt__'][0].value}")
        decision = input("Approve booking? (approve/reject): ").strip()
        result = app.invoke(Command(resume=decision), config=config)

    write_result_to_file(result)
    print(result)
    return result


def main() -> None:
    print(render_menu())
    choice = parse_menu_choice(
        input("Enter scenario number: "), len(SCENARIOS))
    if choice is None:
        print("Invalid selection. Exiting.")
        return
    run_scenario(SCENARIOS[choice])


if __name__ == "__main__":
    main()
