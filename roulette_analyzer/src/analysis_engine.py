# Handles analysis logic for Roulette Analyzer.
from collections import Counter

# --- Helper Data ---
ROULETTE_WHEEL = {
    0: 'green',
    1: 'red', 2: 'black', 3: 'red', 4: 'black', 5: 'red', 6: 'black', 7: 'red', 8: 'black', 9: 'red',
    10: 'black', 11: 'black', 12: 'red', 13: 'black', 14: 'red', 15: 'black', 16: 'red', 17: 'black', 18: 'red',
    19: 'red', 20: 'black', 21: 'red', 22: 'black', 23: 'red', 24: 'black', 25: 'red', 26: 'black', 27: 'red',
    28: 'black', 29: 'black', 30: 'red', 31: 'black', 32: 'red', 33: 'black', 34: 'red', 35: 'black', 36: 'red'
}

NUMBER_TO_DOZEN = {n: ( (n-1)//12 ) + 1 for n in range(1, 37)} # 1st, 2nd, 3rd dozen
NUMBER_TO_DOZEN[0] = None # 0 is not in any dozen

NUMBER_TO_COLUMN = {n: ( (n-1)%3 ) + 1 for n in range(1, 37)} # 1st, 2nd, 3rd column
NUMBER_TO_COLUMN[0] = None # 0 is not in any column

# Simplified sections (halves and even/odd for now)
# More complex sections like Voisins, Tiers, Orphelins can be added later
NUMBER_TO_HALF = {n: 1 if 1 <= n <= 18 else (2 if 19 <= n <= 36 else None) for n in range(0, 37)} # 1st half (1-18), 2nd half (19-36)
NUMBER_TO_EVEN_ODD = {n: 'even' if n != 0 and n % 2 == 0 else ('odd' if n != 0 and n % 2 != 0 else None) for n in range(0, 37)}


def calculate_frequencies(results: list[int]) -> dict:
    """
    Calculates various frequencies from a list of roulette results.

    Args:
        results: A list of integers representing roulette numbers (0-36).

    Returns:
        A dictionary containing frequencies of numbers, colors, dozens,
        columns, and other defined sections.
    """
    if not results:
        return {
            "number_frequencies": Counter(),
            "color_frequencies": Counter(),
            "dozen_frequencies": Counter(),
            "column_frequencies": Counter(),
            "half_frequencies": Counter(),
            "even_odd_frequencies": Counter(),
            "total_spins": 0
        }

    total_spins = len(results)
    number_counts = Counter(results)

    color_counts = Counter(ROULETTE_WHEEL.get(n, None) for n in results)
    # Remove None if any number was out of ROULETTE_WHEEL range (should not happen with valid input)
    if None in color_counts: del color_counts[None]

    dozen_counts = Counter(NUMBER_TO_DOZEN.get(n) for n in results if n != 0)
    if None in dozen_counts: del dozen_counts[None] # Should be handled by n != 0

    column_counts = Counter(NUMBER_TO_COLUMN.get(n) for n in results if n != 0)
    if None in column_counts: del column_counts[None] # Should be handled by n != 0

    half_counts = Counter(NUMBER_TO_HALF.get(n) for n in results if n != 0)
    if None in half_counts: del half_counts[None]

    even_odd_counts = Counter(NUMBER_TO_EVEN_ODD.get(n) for n in results if n != 0)
    if None in even_odd_counts: del even_odd_counts[None]

    return {
        "number_frequencies": dict(number_counts),
        "color_frequencies": dict(color_counts),
        "dozen_frequencies": dict(dozen_counts),
        "column_frequencies": dict(column_counts),
        "half_frequencies": dict(half_counts),
        "even_odd_frequencies": dict(even_odd_counts),
        "total_spins": total_spins
    }

if __name__ == '__main__':
    # Example Usage for testing
    sample_results_1 = [0, 10, 20, 30, 36, 1, 2, 3, 1, 1, 13, 25, 13, 0, 19, 22]
    print(f"Sample Results 1: {sample_results_1}")
    frequencies_1 = calculate_frequencies(sample_results_1)
    import json
    print(json.dumps(frequencies_1, indent=4))

    sample_results_2 = []
    print(f"\nSample Results 2 (empty): {sample_results_2}")
    frequencies_2 = calculate_frequencies(sample_results_2)
    print(json.dumps(frequencies_2, indent=4))

    sample_results_3 = [1, 1, 1, 1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0] # Test dozen 1 and column coverage
    print(f"\nSample Results 3: {sample_results_3}")
    frequencies_3 = calculate_frequencies(sample_results_3)
    print(json.dumps(frequencies_3, indent=4))

# --- Trend Identification ---

# Expected probabilities for a standard European roulette wheel
EXPECTED_PROBABILITIES = {
    "number": 1/37,
    "red": 18/37,
    "black": 18/37,
    "green": 1/37,
    "dozen": 12/37,  # For a specific dozen
    "column": 12/37, # For a specific column
    "half": 18/37,   # For a specific half (1-18 or 19-36)
    "even": 18/37,
    "odd": 18/37,
}

# Thresholds for identifying "significant" deviation
# These are somewhat arbitrary and can be tuned.
# For numbers, a larger deviation might be needed due to lower individual expected frequencies.
HOT_COLD_NUMBER_THRESHOLD_PERCENTAGE = 0.50 # +/- 50% from expected count
CATEGORY_TREND_THRESHOLD_PERCENTAGE = 0.25 # +/- 25% from expected count for colors, dozens etc.
MIN_SPINS_FOR_TRENDS = 5 # Minimum number of spins to attempt trend analysis
LOW_SPIN_WARNING_THRESHOLD_TRENDS = 20 # Threshold for a low data warning

def identify_trends(frequencies: dict, total_spins: int) -> dict:
    """
    Identifies trends (significant deviations from expected frequencies)
    in roulette results.

    Args:
        frequencies: A dictionary of frequencies from calculate_frequencies.
        total_spins: The total number of spins.

    Returns:
        A dictionary summarizing identified trends.
    """
    trends = {
        "message": "",
        "hot_numbers": [],
        "cold_numbers": [],
        "number_deviations": {}, # Store actual vs expected for all numbers
        "category_trends": {} # For colors, dozens, etc.
    }

    if total_spins < MIN_SPINS_FOR_TRENDS:
        trends["message"] = f"Insufficient data for trend analysis (minimum {MIN_SPINS_FOR_TRENDS} spins required, got {total_spins})."
        return trends
    elif MIN_SPINS_FOR_TRENDS <= total_spins < LOW_SPIN_WARNING_THRESHOLD_TRENDS:
        trends["message"] = (
            f"Trend analysis performed, but results are based on a very small dataset ({total_spins} spins) "
            "and may not be statistically significant. Interpret with extreme caution."
        )
    else:
        # This will be set later if no specific trends are found or after successful analysis.
        trends["message"] = "Trend analysis performed." # Default message

    # 1. Number Trends
    expected_number_freq = EXPECTED_PROBABILITIES["number"] * total_spins
    num_freq_dict = frequencies.get("number_frequencies", {}) # Ensure it's a dict

    for num in range(37): # Iterate 0-36
        actual_freq = 0
        if num_freq_dict: # Check if the dictionary is not empty
            # Try accessing with int key first, then str key if that fails or if first key is str
            actual_freq = num_freq_dict.get(num, num_freq_dict.get(str(num), 0))

        deviation = actual_freq - expected_number_freq
        percent_deviation = (deviation / expected_number_freq) if expected_number_freq > 0 else float('inf') if actual_freq > 0 else 0

        trends["number_deviations"][num] = {
            "actual": actual_freq,
            "expected": round(expected_number_freq, 2),
            "deviation": round(deviation, 2),
            "percent_deviation": round(percent_deviation, 2)
        }

        if percent_deviation > HOT_COLD_NUMBER_THRESHOLD_PERCENTAGE:
            trends["hot_numbers"].append({"number": num, "actual": actual_freq, "expected": round(expected_number_freq, 2)})
        elif percent_deviation < -HOT_COLD_NUMBER_THRESHOLD_PERCENTAGE:
            # Ensure it's cold because it appeared less, not just because expected is low and it didn't appear
            if actual_freq < expected_number_freq :
                 trends["cold_numbers"].append({"number": num, "actual": actual_freq, "expected": round(expected_number_freq, 2)})


    # 2. Category Trends (Colors, Dozens, Columns, Halves, Even/Odd)
    def analyze_category(category_name: str, actual_freq_map: dict, expected_prob_key: str, items: list):
        category_trends = {}
        expected_overall_freq = EXPECTED_PROBABILITIES[expected_prob_key] * total_spins

        for item in items:
            actual_freq = actual_freq_map.get(item, 0)
            deviation = actual_freq - expected_overall_freq
            percent_deviation = (deviation / expected_overall_freq) if expected_overall_freq > 0 else float('inf') if actual_freq > 0 else 0

            trend_data = {
                "actual": actual_freq,
                "expected": round(expected_overall_freq, 2),
                "deviation": round(deviation, 2),
                "percent_deviation": round(percent_deviation, 2)
            }
            if abs(percent_deviation) > CATEGORY_TREND_THRESHOLD_PERCENTAGE:
                category_trends[item] = trend_data

        if category_trends: # Only add if there are significant trends
             trends["category_trends"][category_name] = category_trends

    analyze_category("colors", frequencies["color_frequencies"], "red", ['red', 'black', 'green']) # Green uses 'number' prob for expected
    # Adjust for green as its probability is different
    if "colors" in trends["category_trends"] and "green" in trends["category_trends"]["colors"]:
        expected_green_freq = EXPECTED_PROBABILITIES["green"] * total_spins
        actual_green_freq = frequencies["color_frequencies"].get('green',0)
        deviation_green = actual_green_freq - expected_green_freq
        percent_dev_green = (deviation_green / expected_green_freq) if expected_green_freq > 0 else float('inf') if actual_green_freq > 0 else 0
        trends["category_trends"]["colors"]["green"]["expected"] = round(expected_green_freq,2)
        trends["category_trends"]["colors"]["green"]["deviation"] = round(deviation_green,2)
        trends["category_trends"]["colors"]["green"]["percent_deviation"] = round(percent_dev_green,2)
        if abs(percent_dev_green) <= CATEGORY_TREND_THRESHOLD_PERCENTAGE : # if not significant, remove
            del trends["category_trends"]["colors"]["green"]
            if not trends["category_trends"]["colors"]: del trends["category_trends"]["colors"]


    analyze_category("dozens", frequencies["dozen_frequencies"], "dozen", [1, 2, 3])
    analyze_category("columns", frequencies["column_frequencies"], "column", [1, 2, 3])
    analyze_category("halves", frequencies["half_frequencies"], "half", [1, 2])
    analyze_category("even_odd", frequencies["even_odd_frequencies"], "even", ['even', 'odd']) # odd uses 'even' prob

    # Final message update if no specific trends found, but analysis was performed
    if not trends["hot_numbers"] and not trends["cold_numbers"] and not trends["category_trends"]:
        if total_spins >= LOW_SPIN_WARNING_THRESHOLD_TRENDS: # Only override if not already a low spin warning
            trends["message"] = "Trend analysis performed. No significant trends identified with current thresholds and data."
        # If it's a low spin count and no trends, the earlier low spin message is more appropriate and remains.
    elif total_spins >= LOW_SPIN_WARNING_THRESHOLD_TRENDS : # If trends were found and not low spin
        trends["message"] = "Trend analysis complete. Significant trends identified."


    return trends

if __name__ == '__main__':
    # Example Usage for testing
    sample_results_1 = [0, 10, 20, 30, 36, 1, 2, 3, 1, 1, 13, 25, 13, 0, 19, 22, 10, 10, 10, 10, 10, 5, 5] # Min spins = 20
    print(f"Sample Results 1: {sample_results_1} (Total: {len(sample_results_1)})")
    frequencies_1 = calculate_frequencies(sample_results_1)
    import json
    print("Frequencies 1:")
    print(json.dumps(frequencies_1, indent=4))
    trends_1 = identify_trends(frequencies_1, len(sample_results_1))
    print("\nTrends 1:")
    print(json.dumps(trends_1, indent=4))

    sample_results_2 = [1]*5 + [2]*5 + [19]*5 + [20]*5 # 20 spins
    print(f"\nSample Results 2: {sample_results_2} (Total: {len(sample_results_2)})")
    frequencies_2 = calculate_frequencies(sample_results_2)
    print("Frequencies 2:")
    print(json.dumps(frequencies_2, indent=4))
    trends_2 = identify_trends(frequencies_2, len(sample_results_2))
    print("\nTrends 2:")
    print(json.dumps(trends_2, indent=4))

    sample_results_short = [1,2,3,4,5]
    print(f"\nSample Results Short: {sample_results_short} (Total: {len(sample_results_short)})")
    frequencies_short = calculate_frequencies(sample_results_short)
    print("Frequencies Short:")
    print(json.dumps(frequencies_short, indent=4))
    trends_short = identify_trends(frequencies_short, len(sample_results_short))
    print("\nTrends Short:")
    print(json.dumps(trends_short, indent=4))

    # Test with a lot of one number
    sample_results_biased = [7]*15 + [1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26] # 40 spins
    print(f"\nSample Results Biased: {sample_results_biased} (Total: {len(sample_results_biased)})")
    frequencies_biased = calculate_frequencies(sample_results_biased)
    print("Frequencies Biased:")
    print(json.dumps(frequencies_biased, indent=4))
    trends_biased = identify_trends(frequencies_biased, len(sample_results_biased))
    print("\nTrends Biased:")
    print(json.dumps(trends_biased, indent=4))

# --- Pattern Detection ---
MIN_SPINS_FOR_PATTERNS = 5 # Minimum spins for some basic pattern detection

def detect_patterns(results: list[int], frequencies: dict) -> dict:
    """
    Detects specific patterns in a list of roulette results.

    Args:
        results: A list of integers representing roulette numbers (0-36).
        frequencies: The pre-calculated frequencies dictionary (can be used if helpful,
                     though direct iteration on results is primary for sequences).

    Returns:
        A dictionary summarizing detected patterns.
    """
    patterns = {
        "message": "",
        "number_repeats": {"counts": Counter(), "longest_streak": 0, "number_for_longest_streak": None, "total_immediate_repeats": 0},
        "alternating_color_streak": {"longest_streak": 0, "current_streak": 0, "last_color": None},
        "consecutive_dozen_streak": {"longest_streak": 0, "current_streak": 0, "dozen_for_longest_streak": None, "current_dozen": None},
        "consecutive_column_streak": {"longest_streak": 0, "current_streak": 0, "column_for_longest_streak": None, "current_column": None},
    }

    if len(results) < MIN_SPINS_FOR_PATTERNS:
        patterns["message"] = f"Insufficient data for pattern detection (minimum {MIN_SPINS_FOR_PATTERNS} spins required, got {len(results)})."
        # Return early with counts initialized to 0 or empty
        patterns["alternating_color_streak"] = 0
        patterns["consecutive_dozen_streak"] = {"longest_streak":0, "dozen": None}
        patterns["consecutive_column_streak"] = {"longest_streak":0, "column": None}
        patterns["number_repeats"] = {"longest_streak":0, "number":None, "total_immediate_repeats":0}
        return patterns

    # 1. Number Repeats and Longest Streak of a Single Number
    if not results: # Should be caught by MIN_SPINS_FOR_PATTERNS but good practice
        return patterns

    current_streak_val = results[0]
    current_streak_len = 0

    for i in range(len(results)):
        # Immediate repeats
        if i > 0 and results[i] == results[i-1]:
            patterns["number_repeats"]["total_immediate_repeats"] += 1
            patterns["number_repeats"]["counts"][results[i]] = patterns["number_repeats"]["counts"].get(results[i], 0) + 1

        # Longest streak of a single number
        if results[i] == current_streak_val:
            current_streak_len += 1
        else:
            if current_streak_len > patterns["number_repeats"]["longest_streak"]:
                patterns["number_repeats"]["longest_streak"] = current_streak_len
                patterns["number_repeats"]["number_for_longest_streak"] = current_streak_val
            current_streak_val = results[i]
            current_streak_len = 1

    # Check last streak
    if current_streak_len > patterns["number_repeats"]["longest_streak"]:
        patterns["number_repeats"]["longest_streak"] = current_streak_len
        patterns["number_repeats"]["number_for_longest_streak"] = current_streak_val
    if patterns["number_repeats"]["longest_streak"] == 1 and len(set(results)) == len(results): # if all numbers are unique, longest streak is 1 of any number.
        patterns["number_repeats"]["number_for_longest_streak"] = None if len(results) == 0 else results[0]


    # 2. Alternating Colors (Red/Black)
    # Re-initialize for this specific pattern logic
    current_alternating_streak = 0
    longest_alternating_streak = 0
    last_color_for_alternating = None

    for num in results:
        color = ROULETTE_WHEEL.get(num)
        if color in ['red', 'black']:
            if last_color_for_alternating is None or color != last_color_for_alternating:
                current_alternating_streak += 1
            else: # Color repeated, reset streak
                if current_alternating_streak > longest_alternating_streak:
                    longest_alternating_streak = current_alternating_streak
                current_alternating_streak = 1 # Start new streak with the current color
            last_color_for_alternating = color
        else: # Green or invalid number, breaks the red/black alternating streak
            if current_alternating_streak > longest_alternating_streak:
                longest_alternating_streak = current_alternating_streak
            current_alternating_streak = 0
            last_color_for_alternating = None # Reset for next R/B sequence

    if current_alternating_streak > longest_alternating_streak: # Check after loop
        longest_alternating_streak = current_alternating_streak
    patterns["alternating_color_streak"] = longest_alternating_streak


    # 3. Consecutive Dozens/Columns
    current_dozen_streak = 0
    longest_dozen_streak = 0
    current_dozen_val = None
    dozen_for_longest = None

    current_column_streak = 0
    longest_column_streak = 0
    current_column_val = None
    column_for_longest = None

    for num in results:
        if num == 0: # Zero resets streaks for dozens/columns
            if current_dozen_streak > longest_dozen_streak:
                longest_dozen_streak = current_dozen_streak
                dozen_for_longest = current_dozen_val
            current_dozen_streak = 0
            current_dozen_val = None

            if current_column_streak > longest_column_streak:
                longest_column_streak = current_column_streak
                column_for_longest = current_column_val
            current_column_streak = 0
            current_column_val = None
            continue

        dozen = NUMBER_TO_DOZEN.get(num)
        column = NUMBER_TO_COLUMN.get(num)

        # Dozen streak
        if dozen == current_dozen_val:
            current_dozen_streak += 1
        else:
            if current_dozen_streak > longest_dozen_streak:
                longest_dozen_streak = current_dozen_streak
                dozen_for_longest = current_dozen_val
            current_dozen_val = dozen
            current_dozen_streak = 1

        # Column streak
        if column == current_column_val:
            current_column_streak += 1
        else:
            if current_column_streak > longest_column_streak:
                longest_column_streak = current_column_streak
                column_for_longest = current_column_val
            current_column_val = column
            current_column_streak = 1

    # Final checks for dozen/column streaks
    if current_dozen_streak > longest_dozen_streak:
        longest_dozen_streak = current_dozen_streak
        dozen_for_longest = current_dozen_val
    patterns["consecutive_dozen_streak"] = {"longest_streak": longest_dozen_streak, "dozen": dozen_for_longest}

    if current_column_streak > longest_column_streak:
        longest_column_streak = current_column_streak
        column_for_longest = current_column_val
    patterns["consecutive_column_streak"] = {"longest_streak": longest_column_streak, "column": column_for_longest}

    if not patterns["message"]:
         patterns["message"] = "Pattern detection complete."

    # Clean up initial structures if they remained empty
    if not patterns["number_repeats"]["counts"]:
        del patterns["number_repeats"]["counts"]


    return patterns


if __name__ == '__main__':
    # ... (keep existing test cases for calculate_frequencies and identify_trends)
    print("\n\n--- Pattern Detection Tests ---")

    test_results_patterns_1 = [1, 2, 2, 3, 4, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 10, 10, 11] # len 18
    # Expected: repeats: (2,1), (4,2), (7,1), (10,3) -> total 7. longest_streak: 4 (for number 10)
    # R,B,B,R,B,B,B,R,B,R,R,B,R,B,B,B,B,B
    # Alt colors: R,B (2), B (reset), R,B (2), B (reset), B (reset), R,B (2), R (reset), R (reset), B,R,B (3), B (reset), B (reset), B (reset) -> longest 3
    # Dozens: 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1 -> D1: 18
    # Columns: C1,C2,C2,C3,C1,C1,C1,C2,C3,C1,C1,C2,C3,C1,C1,C1,C1,C2 -> C1: 4 (num 10)
    print(f"\nTest Results Patterns 1: {test_results_patterns_1}")
    freq_p1 = calculate_frequencies(test_results_patterns_1) # Needed by nothing in patterns, but good for consistency
    patterns_1 = detect_patterns(test_results_patterns_1, freq_p1)
    print(json.dumps(patterns_1, indent=4))

    test_results_patterns_2 = [1, 10, 2, 20, 3, 30] # R,B,B,B,R,R (Alternating R/B should be low) len 6
    # Alt colors: R,B (2). B (reset). B (reset). R (2). R (reset). Longest 2.
    print(f"\nTest Results Patterns 2 (alternating colors): {test_results_patterns_2}")
    freq_p2 = calculate_frequencies(test_results_patterns_2)
    patterns_2 = detect_patterns(test_results_patterns_2, freq_p2)
    print(json.dumps(patterns_2, indent=4))

    test_results_patterns_3 = [0, 1, 13, 2, 14, 3, 15, 0, 1, 2, 3] # Test 0, dozens, columns len 11
    # Dozens: 0, D1, D2, D1, D2, D1, D2, 0, D1, D1, D1. Longest D1 = 3
    # Columns:0, C1, C1, C2, C2, C3, C3, 0, C1, C2, C3. Longest C1,C2,C3 = 1
    print(f"\nTest Results Patterns 3 (zeros, dozens, columns): {test_results_patterns_3}")
    freq_p3 = calculate_frequencies(test_results_patterns_3)
    patterns_3 = detect_patterns(test_results_patterns_3, freq_p3)
    print(json.dumps(patterns_3, indent=4))

    test_results_patterns_4 = [1,2,3,4,5] # Short, no repeats, basic alternating
    print(f"\nTest Results Patterns 4 (short, distinct): {test_results_patterns_4}")
    freq_p4 = calculate_frequencies(test_results_patterns_4)
    patterns_4 = detect_patterns(test_results_patterns_4, freq_p4)
    print(json.dumps(patterns_4, indent=4))

    test_results_patterns_5 = [1,1,1,1,1] # All same number
    print(f"\nTest Results Patterns 5 (all same): {test_results_patterns_5}")
    freq_p5 = calculate_frequencies(test_results_patterns_5)
    patterns_5 = detect_patterns(test_results_patterns_5, freq_p5)
    print(json.dumps(patterns_5, indent=4))

    test_results_patterns_empty = []
    print(f"\nTest Results Patterns Empty: {test_results_patterns_empty}")
    freq_pe = calculate_frequencies(test_results_patterns_empty)
    patterns_e = detect_patterns(test_results_patterns_empty, freq_pe)
    print(json.dumps(patterns_e, indent=4))

    test_results_patterns_short = [1,2]
    print(f"\nTest Results Patterns Short: {test_results_patterns_short}")
    freq_ps = calculate_frequencies(test_results_patterns_short)
    patterns_s = detect_patterns(test_results_patterns_short, freq_ps)
    print(json.dumps(patterns_s, indent=4))

# --- Bias Detection ---

# More detailed wheel sections
# Voisins du Zéro (Neighbors of Zero): 0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35 (17 numbers)
VOISINS_DU_ZERO = {0, 2, 3, 4, 7, 12, 15, 18, 19, 21, 22, 25, 26, 28, 29, 32, 35}
# Tiers du Cylindre (Third of the Wheel): 5, 6, 8, 10, 11, 13, 16, 17, 23, 24, 27, 30, 33, 36 (12 numbers, but typically 6 numbers are bet with 6 splits)
# For frequency analysis, we consider all numbers in the section.
TIERS_DU_CYLINDRE = {5, 6, 8, 10, 11, 13, 16, 17, 23, 24, 27, 30, 33, 36} # Actually 12 numbers on the wheel: 27,13,36,11,30,8,23,10,5,24,16,33
# Orphelins (Orphans): 1, 9, 14, 20, 31, 34 (6 numbers, but typically 5 numbers are bet, 1 straight up, 4 splits)
# For frequency analysis, we consider all numbers in the section.
ORPHELINS = {1, 9, 14, 20, 31, 34} # Actually 8 numbers on the wheel: 1,20,14,31,9,17,34,6 (17&6 are also Tiers/Voisins based on some layouts)
# Let's use a common definition:
# Voisins: 22,18,29,7,28,12,35,3,26,0,32,15,19,4,21,2,25 (17 numbers)
VOISINS_NUMBERS = {22,18,29,7,28,12,35,3,26,0,32,15,19,4,21,2,25}
# Tiers: 33,16,24,5,10,23,8,30,11,36,13,27 (12 numbers)
TIERS_NUMBERS = {33,16,24,5,10,23,8,30,11,36,13,27}
# Orphelins: 17,34,6,1,20,14,31,9 (8 numbers)
ORPHELINS_NUMBERS = {17,34,6,1,20,14,31,9}

# Sanity check: 17 + 12 + 8 = 37 numbers. All numbers covered.
WHEEL_SECTIONS = {
    "Voisins du Zero": VOISINS_NUMBERS,
    "Tiers du Cylindre": TIERS_NUMBERS,
    "Orphelins": ORPHELINS_NUMBERS
}

MIN_SPINS_FOR_BIAS = 5 # Minimum spins for bias detection
LOW_SPIN_WARNING_THRESHOLD_BIAS = 30 # Threshold for low data warning for bias
CHI_SQUARED_CRITICAL_VALUE_P005_DF36 = 51.0 # Approximate critical value for p=0.05 and df=36

def detect_biases(frequencies: dict, total_spins: int, number_deviations: dict) -> dict:
    """
    Detects potential biases in roulette results using Chi-Squared test
    and sectional frequency analysis.

    Args:
        frequencies: A dictionary of frequencies from calculate_frequencies.
        total_spins: The total number of spins.
        number_deviations: A dictionary from identify_trends with detailed
                           number deviation data.

    Returns:
        A dictionary summarizing potential biases.
    """
    bias_analysis = {
        "message": "",
        "chi_squared_test": {"statistic": None, "critical_value": CHI_SQUARED_CRITICAL_VALUE_P005_DF36, "is_biased_suggestion": False, "message": ""},
        "sectional_bias": {},
        "interpretation": ""
    }

    if total_spins < MIN_SPINS_FOR_BIAS:
        bias_analysis["message"] = f"Insufficient data for bias detection (minimum {MIN_SPINS_FOR_BIAS} spins required, got {total_spins}). Chi-Squared test not performed."
        bias_analysis["interpretation"] = "More spins are needed for bias assessment."
        return bias_analysis
    elif MIN_SPINS_FOR_BIAS <= total_spins < LOW_SPIN_WARNING_THRESHOLD_BIAS:
        bias_analysis["message"] = (
            f"Bias detection performed. However, with only {total_spins} spins, these results (especially Chi-Squared) "
            "have very low statistical reliability. Interpret with extreme caution."
        )
        bias_analysis["interpretation"] = f"Results based on a very small dataset ({total_spins} spins)."
    else:
        bias_analysis["message"] = "Bias detection performed." # Default message if not overwritten

    # 1. Chi-Squared Goodness of Fit Test
    expected_freq_per_number = total_spins / 37.0
    chi_squared_specific_msg = "" # Specific messages about Chi-squared test itself

    if expected_freq_per_number < 1:
         chi_squared_specific_msg = (
             f"Critical Warning: Expected frequency per number ({expected_freq_per_number:.2f}) is less than 1. "
             "Chi-Squared test is highly unreliable and results should be disregarded. Substantially more spins are needed."
         )
    elif expected_freq_per_number < 5:
         chi_squared_specific_msg = (
             f"Warning: Expected frequency per number ({expected_freq_per_number:.2f}) is less than 5. "
             "Chi-Squared test results may be less reliable. Consider more spins."
         )

    chi_squared_statistic = 0
    dev_data = number_deviations # from trends output

    if not dev_data: # If number_deviations itself is empty or None
        bias_analysis["chi_squared_test"]["message"] = "Chi-Squared test not performed as number deviation data is unavailable. " + chi_squared_specific_msg
        bias_analysis["chi_squared_test"]["statistic"] = None
        bias_analysis["chi_squared_test"]["is_biased_suggestion"] = False
    else:
        # Determine key type for number_deviations once
        first_key_in_dev_data = next(iter(dev_data), None)
        keys_are_int = isinstance(first_key_in_dev_data, int)

        for num in range(37): # 0-36
            num_key_for_lookup = num if keys_are_int else str(num)
            observed_freq = dev_data.get(num_key_for_lookup, {}).get("actual", 0)

            if expected_freq_per_number == 0: # Avoid division by zero if total_spins somehow was 0 but passed min check
                chi_squared_statistic += float('inf') if observed_freq > 0 else 0
            else:
                chi_squared_statistic += ((observed_freq - expected_freq_per_number)**2) / expected_freq_per_number

        bias_analysis["chi_squared_test"]["statistic"] = round(chi_squared_statistic, 2)
        if chi_squared_statistic > CHI_SQUARED_CRITICAL_VALUE_P005_DF36:
            bias_analysis["chi_squared_test"]["is_biased_suggestion"] = True
            bias_analysis["chi_squared_test"]["message"] = "Chi-Squared statistic exceeds critical value, suggesting potential number distribution bias. " + chi_squared_specific_msg
        else:
            bias_analysis["chi_squared_test"]["message"] = "Chi-Squared statistic is within expected limits. " + chi_squared_specific_msg
            # No strong suggestion of bias from Chi-squared alone.

    # 2. Sectional Bias Analysis
    # Using a threshold similar to CATEGORY_TREND_THRESHOLD_PERCENTAGE for deviation significance
    SECTION_BIAS_THRESHOLD = CATEGORY_TREND_THRESHOLD_PERCENTAGE # +/- 25%

    for section_name, section_numbers in WHEEL_SECTIONS.items():
        observed_section_hits = sum(frequencies["number_frequencies"].get(str(n), frequencies["number_frequencies"].get(n, 0)) for n in section_numbers)
        expected_section_hits = (len(section_numbers) / 37.0) * total_spins

        deviation = observed_section_hits - expected_section_hits
        percent_deviation = (deviation / expected_section_hits) if expected_section_hits > 0 else float('inf') if observed_section_hits > 0 else 0

        status = "as_expected"
        if percent_deviation > SECTION_BIAS_THRESHOLD:
            status = "over_represented"
        elif percent_deviation < -SECTION_BIAS_THRESHOLD:
            status = "under_represented"

        bias_analysis["sectional_bias"][section_name] = {
            "observed_hits": observed_section_hits,
            "expected_hits": round(expected_section_hits, 2),
            "deviation_percent": round(percent_deviation * 100, 1),
            "status": status
        }

    # Interpretation - only append if not already set by low spin warning and if chi_squared_test was performed
    if not bias_analysis["interpretation"] and bias_analysis["chi_squared_test"].get("statistic") is not None:
        if bias_analysis["chi_squared_test"]["is_biased_suggestion"]:
            bias_analysis["interpretation"] = "Potential bias suggested by Chi-Squared test. "
            if any(s["status"] != "as_expected" for s in bias_analysis["sectional_bias"].values()):
                bias_analysis["interpretation"] += "Sectional analysis also shows imbalances. Further investigation or more data recommended."
            else:
                bias_analysis["interpretation"] += "Sectional analysis does not strongly highlight specific areas, but overall number distribution is suspect."
        else:
            bias_analysis["interpretation"] = "No strong evidence of overall bias from Chi-Squared test. "
            if any(s["status"] != "as_expected" for s in bias_analysis["sectional_bias"].values()):
                bias_analysis["interpretation"] += "However, some wheel sections show notable deviation, which might warrant closer observation."
            else:
                bias_analysis["interpretation"] += "Sectional distributions also appear relatively balanced."
    elif not bias_analysis["interpretation"]: # If interpretation still not set (e.g. Chi-sq not run)
        bias_analysis["interpretation"] = "Sectional bias analysis performed."


    # The main bias_analysis["message"] is already set based on spin count or default.
    return bias_analysis


if __name__ == '__main__':
    # ... (keep existing test cases)
    print("\n\n--- Bias Detection Tests ---")

    # Test 1: Relatively uniform data (low Chi-Squared)
    # To make it somewhat uniform for 74 spins (2 hits per number)
    uniform_results = []
    for i in range(37):
        uniform_results.extend([i, i]) # 74 spins

    # Add some minor variations to avoid perfect distribution
    uniform_results[0] = 0
    uniform_results[10] = 10
    uniform_results[20] = 20
    uniform_results.append(5) # 75 spins
    uniform_results.append(15) # 76 spins
    uniform_results.append(25) # 77 spins


    print(f"\nUniform-ish Results (approx {len(uniform_results)} spins):")
    freq_uniform = calculate_frequencies(uniform_results)
    trends_uniform = identify_trends(freq_uniform, len(uniform_results))
    # print(json.dumps(freq_uniform, indent=4))
    # print(json.dumps(trends_uniform["number_deviations"], indent=4)) # Pass only number_deviations
    biases_uniform = detect_biases(freq_uniform, len(uniform_results), trends_uniform["number_deviations"])
    print(json.dumps(biases_uniform, indent=4))

    # Test 2: Biased data (e.g., one number very frequent)
    biased_results = [7]*20 + [1]*5 + [10]*5 + [15]*5 + [20]*5 + [25]*5 + [30]*5 + list(range(10,30)) # 20 + 30 + 20 = 70 spins
    print(f"\nBiased Results ({len(biased_results)} spins):")
    freq_biased = calculate_frequencies(biased_results)
    trends_biased_for_bias = identify_trends(freq_biased, len(biased_results))
    # print(json.dumps(freq_biased, indent=4))
    # print(json.dumps(trends_biased_for_bias["number_deviations"], indent=4))
    biases_biased = detect_biases(freq_biased, len(biased_results), trends_biased_for_bias["number_deviations"])
    print(json.dumps(biases_biased, indent=4))

    # Test 3: Insufficient data
    short_results_bias = [1,2,3,4,5,6,7,8,9,10]
    print(f"\nShort Results for Bias ({len(short_results_bias)} spins):")
    freq_short_bias = calculate_frequencies(short_results_bias)
    trends_short_bias = identify_trends(freq_short_bias, len(short_results_bias))
    biases_short = detect_biases(freq_short_bias, len(short_results_bias), trends_short_bias["number_deviations"])
    print(json.dumps(biases_short, indent=4))

    # Test 4: Sectional Bias Example (Voisins heavy)
    voisins_heavy_results = list(VOISINS_NUMBERS) * 3 # 17 * 3 = 51 spins
    # Add a few other numbers to make it less perfect
    voisins_heavy_results.extend([5, 6, 8, 10, 11, 13, 16]) # 51 + 7 = 58 spins
    print(f"\nVoisins Heavy Results ({len(voisins_heavy_results)} spins):")
    freq_voisins = calculate_frequencies(voisins_heavy_results)
    trends_voisins = identify_trends(freq_voisins, len(voisins_heavy_results))
    biases_voisins = detect_biases(freq_voisins, len(voisins_heavy_results), trends_voisins["number_deviations"])
    print(json.dumps(biases_voisins, indent=4))

# --- Wheel Clustering Analysis ---

# Physical order of numbers on a standard European roulette wheel
WHEEL_ORDER = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
# len(WHEEL_ORDER) should be 37

MIN_SPINS_FOR_CLUSTERS = 5 # Minimum spins for cluster analysis
LOW_SPIN_WARNING_THRESHOLD_CLUSTERS = 20 # Threshold for low data warning for clusters
CLUSTER_ARC_SIZE = 5 # Number of adjacent numbers on the wheel to consider as a cluster/arc (e.g., 5 means center + 2 neighbors each side)
CLUSTER_DEVIATION_THRESHOLD = 0.30 # +/- 30% deviation for an arc to be considered hot/cold

def analyze_wheel_clusters(frequencies: dict, total_spins: int, wheel_order: list[int]) -> dict:
    """
    Analyzes clusters of numbers on the physical roulette wheel to identify
    hot or cold zones.

    Args:
        frequencies: A dictionary of frequencies from calculate_frequencies.
        total_spins: The total number of spins.
        wheel_order: An ordered list of numbers as they appear on the wheel.

    Returns:
        A dictionary summarizing hot and cold wheel clusters.
    """
    cluster_analysis = {
        "message": "",
        "hot_zones": [],
        "cold_zones": [],
        "arc_size": CLUSTER_ARC_SIZE,
        "note": "Result sequence clustering is a potential future enhancement."
    }

    if total_spins < MIN_SPINS_FOR_CLUSTERS:
        cluster_analysis["message"] = f"Insufficient data for wheel cluster analysis (minimum {MIN_SPINS_FOR_CLUSTERS} spins required, got {total_spins})."
        return cluster_analysis
    elif MIN_SPINS_FOR_CLUSTERS <= total_spins < LOW_SPIN_WARNING_THRESHOLD_CLUSTERS:
        cluster_analysis["message"] = (
            f"Wheel cluster analysis performed, but with only {total_spins} spins, identified hot/cold zones "
            "may be due to random chance. Interpret with extreme caution."
        )
    else:
        cluster_analysis["message"] = "Wheel cluster analysis performed." # Default

    if CLUSTER_ARC_SIZE % 2 == 0 or CLUSTER_ARC_SIZE < 3:
        cluster_analysis["message"] = f"Invalid CLUSTER_ARC_SIZE ({CLUSTER_ARC_SIZE}). Must be an odd number >= 3."
        # Defaulting to a valid arc_size or returning might be options. Here, just message and continue carefully.
        # This indicates a programming error rather than user input error.
        return cluster_analysis

    num_wheel_slots = len(wheel_order)
    if num_wheel_slots != 37: # Basic sanity check
        cluster_analysis["message"] = "Invalid wheel_order data."
        return cluster_analysis

    expected_freq_per_slot = total_spins / float(num_wheel_slots)
    expected_arc_freq = CLUSTER_ARC_SIZE * expected_freq_per_slot

    # Pad wheel_order for circularity when selecting arcs
    # e.g., for arc_size 5, need 2 numbers before start and 2 after end
    neighbors_on_each_side = (CLUSTER_ARC_SIZE - 1) // 2
    padded_wheel = wheel_order[-neighbors_on_each_side:] + wheel_order + wheel_order[:neighbors_on_each_side]

    for i in range(num_wheel_slots):
        center_num_index_in_original_wheel = i
        center_num = wheel_order[center_num_index_in_original_wheel]

        # Arc is from i to i + CLUSTER_ARC_SIZE in padded_wheel
        # The actual index in padded_wheel for wheel_order[0] is neighbors_on_each_side
        arc_numbers = padded_wheel[center_num_index_in_original_wheel : center_num_index_in_original_wheel + CLUSTER_ARC_SIZE]

        observed_arc_freq = 0
        for num in arc_numbers:
            observed_arc_freq += frequencies["number_frequencies"].get(str(num), frequencies["number_frequencies"].get(num, 0))

        deviation = observed_arc_freq - expected_arc_freq
        percent_deviation = (deviation / expected_arc_freq) if expected_arc_freq > 0 else float('inf') if observed_arc_freq > 0 else 0

        arc_data = {
            "center_number": center_num,
            "arc": arc_numbers,
            "observed_freq": observed_arc_freq,
            "expected_freq": round(expected_arc_freq, 2),
            "percent_deviation": round(percent_deviation, 2)
        }

        if percent_deviation > CLUSTER_DEVIATION_THRESHOLD:
            cluster_analysis["hot_zones"].append(arc_data)
        elif percent_deviation < -CLUSTER_DEVIATION_THRESHOLD:
            cluster_analysis["cold_zones"].append(arc_data)

    if not cluster_analysis["hot_zones"] and not cluster_analysis["cold_zones"]:
        if total_spins >= LOW_SPIN_WARNING_THRESHOLD_CLUSTERS: # Only override if not already a low spin warning
            cluster_analysis["message"] = "Wheel cluster analysis performed. No significant hot or cold wheel zones identified with current settings."
        # If low spin count and no zones, the earlier low spin message is more appropriate.
    elif total_spins >= LOW_SPIN_WARNING_THRESHOLD_CLUSTERS: # If zones found and not low spin
         cluster_analysis["message"] = "Wheel cluster analysis complete. Hot/cold zones identified."

    return cluster_analysis


if __name__ == '__main__':
    # ... (keep existing test cases)
    print("\n\n--- Wheel Cluster Analysis Tests ---")

    # Test 1: General case with enough spins
    cluster_test_results_1 = []
    # Make a zone around 0 hot: 0, 32, 15, 19, 4. (Indices 0,1,2,3,4 in WHEEL_ORDER)
    # (0, 32, 15, 19, 4) are WHEEL_ORDER[0] to WHEEL_ORDER[4]
    # Center on 15 (WHEEL_ORDER[2]), arc is [0,32,15,19,4]
    hot_zone_for_test = [0, 32, 15, 19, 4]
    for _ in range(10): # Make this zone appear 10 times each = 50 spins
        cluster_test_results_1.extend(hot_zone_for_test)

    # Add some other random numbers to reach total spins > MIN_SPINS_FOR_CLUSTERS
    import random
    for _ in range(30): # 50 + 30 = 80 spins
        cluster_test_results_1.append(random.choice([n for n in WHEEL_ORDER if n not in hot_zone_for_test]))

    print(f"\nCluster Test Results 1 ({len(cluster_test_results_1)} spins):")
    freq_ct1 = calculate_frequencies(cluster_test_results_1)
    # print("Frequencies for CT1:", json.dumps(freq_ct1, indent=2))
    clusters_ct1 = analyze_wheel_clusters(freq_ct1, len(cluster_test_results_1), WHEEL_ORDER)
    print(json.dumps(clusters_ct1, indent=4))
    # Expected: Arc around 15 (0,32,15,19,4) should be hot. Arc around 4 (19,4,21,2,25) also hot.

    # Test 2: Insufficient spins
    cluster_test_results_2 = [1,2,3,4,5,10,11,12,13,14] # 10 spins
    print(f"\nCluster Test Results 2 (Insufficient: {len(cluster_test_results_2)} spins):")
    freq_ct2 = calculate_frequencies(cluster_test_results_2)
    clusters_ct2 = analyze_wheel_clusters(freq_ct2, len(cluster_test_results_2), WHEEL_ORDER)
    print(json.dumps(clusters_ct2, indent=4))

    # Test 3: Uniform distribution (should find no significant clusters)
    uniform_cluster_results = []
    for i in range(2): # approx 2 hits per number = 74 spins
        uniform_cluster_results.extend(WHEEL_ORDER)
    print(f"\nCluster Test Results 3 (Uniform: {len(uniform_cluster_results)} spins):")
    freq_ct3 = calculate_frequencies(uniform_cluster_results)
    clusters_ct3 = analyze_wheel_clusters(freq_ct3, len(uniform_cluster_results), WHEEL_ORDER)
    print(json.dumps(clusters_ct3, indent=4)) # Expect no hot/cold zones, or very few if thresholds are sensitive
