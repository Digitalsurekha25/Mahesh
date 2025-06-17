# Handles data input logic for Roulette Analyzer.

def get_manual_input() -> list[int]:
    """
    Prompts the user to enter roulette numbers one by one,
    validates the input, and returns a list of valid numbers.

    The user can type 'done' or press Enter on an empty line to finish.
    """
    numbers = []
    print("Enter roulette numbers one by one (0-36). Type 'done' or press Enter to finish.")
    while True:
        try:
            user_input = input(f"Enter number {len(numbers) + 1}: ").strip().lower()
            if user_input == 'done' or user_input == '':
                break

            number = int(user_input)
            if 0 <= number <= 36:
                numbers.append(number)
            else:
                print("Invalid input: Number must be between 0 and 36.")
        except ValueError:
            print("Invalid input: Please enter a valid number or 'done'.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Optionally, re-raise or log the error if needed for debugging
            # raise

    if not numbers:
        print("No numbers were entered.")
    else:
        print(f"Input complete. Collected numbers: {numbers}")
    return numbers

if __name__ == '__main__':
    # Example usage for testing
    print("Testing get_manual_input():")
    collected_numbers = get_manual_input()
    if collected_numbers:
        print("\nCollected numbers in test:")
        print(collected_numbers)
    else:
        print("\nNo numbers collected in test.")
