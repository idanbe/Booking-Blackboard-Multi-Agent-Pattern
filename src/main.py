import json
import uuid
from pathlib import Path

from langgraph.types import Command

from state import initial_state, shared_parameters
from controller import create_graph

OUTPUT_PATH = Path(__file__).parent / "outputs" / "run_output.json"


def write_result_to_file(result: dict, output_path: Path = OUTPUT_PATH) -> None:
    """save the result state to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, default=str))


def main():
    user_request = "I want to book a hotel in Jerusalem for 2 nights in July"
    state = initial_state(user_request)
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "params": shared_parameters,
        }
    }
    app = create_graph()
    result = app.invoke(state, config=config)

    if "__interrupt__" in result:
        print(f"[HUMAN GATE] {result['__interrupt__'][0].value}")
        decision = input("Approve booking? (approve/reject): ").strip()
        result = app.invoke(Command(resume=decision), config=config)

    write_result_to_file(result)

    print(result)


if __name__ == "__main__":
    main()
