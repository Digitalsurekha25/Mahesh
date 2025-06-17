import numpy as np

def extract_sequences(numbers_history: list[int], window_size: int) -> tuple[list[list[int]], list[int]]:
    """
    Extracts sequences of numbers (features) and their corresponding next number (label).

    Args:
        numbers_history: A list of all historical roulette numbers in order.
        window_size: The number of past spins to use as features for predicting the next.

    Returns:
        A tuple containing:
        - X_data (list of lists): Each inner list is a sequence of 'window_size' numbers.
        - y_data (list): Each element is the number that followed the corresponding sequence in X_data.
    """
    X_data = []
    y_data = []

    if not numbers_history or len(numbers_history) <= window_size:
        # Not enough data to create any sequences
        return X_data, y_data

    for i in range(len(numbers_history) - window_size):
        sequence = numbers_history[i : i + window_size]
        label = numbers_history[i + window_size]

        X_data.append(sequence)
        y_data.append(label)

    return X_data, y_data

if __name__ == '__main__':
    # Example usage for illustration and basic testing
    sample_history_1 = [10, 20, 5, 0, 15, 30, 10, 25, 3, 12, 18, 7]
    window_1 = 5
    print(f"Sample History 1: {sample_history_1}, Window: {window_1}")
    X1, y1 = extract_sequences(sample_history_1, window_1)
    for i in range(len(X1)):
        print(f"  Sequence: {X1[i]} -> Label: {y1[i]}")
    # Expected output:
    # Sequence: [10, 20, 5, 0, 15] -> Label: 30
    # Sequence: [20, 5, 0, 15, 30] -> Label: 10
    # ... and so on

    sample_history_2 = [1, 2, 3, 4, 5]
    window_2 = 3
    print(f"\nSample History 2: {sample_history_2}, Window: {window_2}")
    X2, y2 = extract_sequences(sample_history_2, window_2)
    for i in range(len(X2)):
        print(f"  Sequence: {X2[i]} -> Label: {y2[i]}")
    # Expected output:
    # Sequence: [1, 2, 3] -> Label: 4
    # Sequence: [2, 3, 4] -> Label: 5

    sample_history_3 = [1, 2, 3] # Not enough data for window_size 3
    window_3 = 3
    print(f"\nSample History 3 (too short): {sample_history_3}, Window: {window_3}")
    X3, y3 = extract_sequences(sample_history_3, window_3)
    if not X3:
        print("  Correctly returned empty X_data and y_data.")
    else:
        print(f"  Incorrectly found data: X={X3}, y={y3}")

    sample_history_4 = [] # Empty history
    window_4 = 3
    print(f"\nSample History 4 (empty): {sample_history_4}, Window: {window_4}")
    X4, y4 = extract_sequences(sample_history_4, window_4)
    if not X4:
        print("  Correctly returned empty X_data and y_data for empty history.")
    else:
        print(f"  Incorrectly found data for empty history: X={X4}, y={y4}")
