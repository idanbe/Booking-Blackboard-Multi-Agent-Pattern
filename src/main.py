from state import initial_state


def main():
    print("Hello from booking-lab!")
    state = initial_state(
        "I want to book a hotel in Paris for 2 nights in July")
    print(state)


if __name__ == "__main__":
    main()
