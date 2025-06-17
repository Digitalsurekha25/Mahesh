# Handles prediction logic for Roulette Analyzer.

from collections import Counter

MAX_PREDICTED_NUMBERS = 5
MAX_PREDICTED_DOZENS = 1
MAX_PREDICTED_COLUMNS = 1
MAX_PREDICTED_OTS = 1 # Orphelins, Tiers, Sections
MAX_PREDICTED_HALVES = 1
MAX_PREDICTED_EVEN_ODD = 1


def generate_predictions(analysis_results: dict, results_history: list[int]) -> dict:
    """
    Generates predictions based on the comprehensive analysis results.

    Args:
        analysis_results: A dictionary containing all analysis data:
            - 'frequencies': Output from calculate_frequencies
            - 'trends': Output from identify_trends
            - 'patterns': Output from detect_patterns
            - 'biases': Output from detect_biases
            - 'clusters': Output from analyze_wheel_clusters
        results_history: The raw list of numbers entered.

    Returns:
        A dictionary of predictions with reasons.
    """
    predictions = {
        "predicted_numbers": [],
        "predicted_dozens": [],
        "predicted_columns": [],
        "predicted_sections": {
            "voisins_tiers_orphelins": [],
            "halves": [],
            "even_odd": []
        },
        "prediction_summary": [], # General textual summary of key prediction drivers
        "confidence_note": "Predictions are based on statistical analysis of past results and are not guarantees of future outcomes. The more data provided, the more meaningful (but still not certain) the analysis."
    }

    # Ensure all keys are present in analysis_results, even if empty from insufficient data
    trends = analysis_results.get('trends', {})
    patterns = analysis_results.get('patterns', {})
    biases = analysis_results.get('biases', {})
    clusters = analysis_results.get('clusters', {})

    # --- 1. Number Predictions ---
    number_candidates = {} # Store number -> reason list

    # From Trends: Hot Numbers
    if trends.get("hot_numbers"):
        for item in trends["hot_numbers"]:
            num = item["number"]
            reason = f"Hot number (actual: {item['actual']}, expected: {item['expected']:.1f})"
            number_candidates.setdefault(num, []).append(reason)

    # From Clusters: Numbers in Hot Zones
    if clusters.get("hot_zones"):
        for zone in clusters["hot_zones"]:
            for num in zone["arc"]:
                reason = f"Part of hot wheel zone centered at {zone['center_number']} (arc dev: {zone['percent_deviation']:.0%})"
                number_candidates.setdefault(num, []).append(reason)

    # From Patterns: Recently repeated numbers (if strong)
    # This is a bit subjective. Let's say if a number has repeated >= X times recently.
    # The current 'patterns' output has 'number_repeats': {'counts': Counter(), 'longest_streak': Y, 'number_for_longest_streak': Z}
    # We can use 'number_for_longest_streak' if 'longest_streak' is significant (e.g. >=3)
    if patterns.get("number_repeats") and patterns["number_repeats"].get("longest_streak", 0) >= 3 :
        num_streak = patterns["number_repeats"]["number_for_longest_streak"]
        if num_streak is not None: # Can be None if no repeats or very short history
            reason = f"Part of longest recent streak of {patterns['number_repeats']['longest_streak']}"
            number_candidates.setdefault(num_streak, []).append(reason)

    # Consolidate and select top number predictions
    # Simple prioritization: more reasons = higher rank. Can be more sophisticated.
    sorted_number_candidates = sorted(number_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for num, reasons in sorted_number_candidates[:MAX_PREDICTED_NUMBERS]:
        predictions["predicted_numbers"].append({"number": num, "reason": "; ".join(reasons)})
    if sorted_number_candidates:
         predictions["prediction_summary"].append(f"Prioritizing numbers that are hot or in hot wheel zones.")


    # --- 2. Dozen Predictions ---
    dozen_candidates = {} # dozen -> reason list

    # From Trends: Hot Dozens
    if trends.get("category_trends", {}).get("dozens"):
        for dozen, data in trends["category_trends"]["dozens"].items():
            if data["percent_deviation"] > 0: # Positive deviation = hot
                 reason = f"Trending dozen (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                 dozen_candidates.setdefault(int(dozen), []).append(reason)

    # From Patterns: Consecutive Dozen Streaks
    if patterns.get("consecutive_dozen_streak", {}).get("longest_streak", 0) >= 3: # e.g. min streak of 3
        dozen = patterns["consecutive_dozen_streak"]["dozen"]
        if dozen:
            reason = f"Recent longest streak of {patterns['consecutive_dozen_streak']['longest_streak']} for dozen {dozen}"
            dozen_candidates.setdefault(dozen, []).append(reason)

    sorted_dozen_candidates = sorted(dozen_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for dozen, reasons in sorted_dozen_candidates[:MAX_PREDICTED_DOZENS]:
        predictions["predicted_dozens"].append({"dozen": dozen, "reason": "; ".join(reasons)})
    if sorted_dozen_candidates:
        predictions["prediction_summary"].append(f"Suggesting dozens that are trending or show recent streaks.")


    # --- 3. Column Predictions --- (Similar logic to Dozens)
    column_candidates = {} # column -> reason list
    if trends.get("category_trends", {}).get("columns"):
        for col, data in trends["category_trends"]["columns"].items():
            if data["percent_deviation"] > 0:
                 reason = f"Trending column (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                 column_candidates.setdefault(int(col), []).append(reason)

    if patterns.get("consecutive_column_streak", {}).get("longest_streak", 0) >= 3:
        col = patterns["consecutive_column_streak"]["column"]
        if col:
            reason = f"Recent longest streak of {patterns['consecutive_column_streak']['longest_streak']} for column {col}"
            column_candidates.setdefault(col, []).append(reason)

    sorted_column_candidates = sorted(column_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for col, reasons in sorted_column_candidates[:MAX_PREDICTED_COLUMNS]:
        predictions["predicted_columns"].append({"column": col, "reason": "; ".join(reasons)})
    if sorted_column_candidates:
        predictions["prediction_summary"].append(f"Suggesting columns that are trending or show recent streaks.")

    # --- 4. Section Predictions (Voisins, Tiers, Orphelins) ---
    vto_candidates = {} # section_name -> reason list
    if biases.get("sectional_bias"):
        for section_name, data in biases["sectional_bias"].items():
            if data["status"] == "over_represented":
                reason = f"Over-represented in bias analysis (obs: {data['observed_hits']}, exp: {data['expected_hits']:.1f}, dev: {data['deviation_percent']:.0%})"
                vto_candidates.setdefault(section_name, []).append(reason)

    # Could also add from hot wheel zones if a zone largely overlaps a VTO section - more complex mapping needed.

    sorted_vto_candidates = sorted(vto_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for section, reasons in sorted_vto_candidates[:MAX_PREDICTED_OTS]:
        predictions["predicted_sections"]["voisins_tiers_orphelins"].append({"section": section, "reason": "; ".join(reasons)})
    if sorted_vto_candidates:
        predictions["prediction_summary"].append(f"Highlighting biased wheel sections (Voisins, Tiers, Orphelins).")

    # --- 5. Section Predictions (Halves) ---
    halves_candidates = {} # half_identifier (e.g., 1 for "1-18") -> reason list
    if trends.get("category_trends", {}).get("halves"):
        for half, data in trends["category_trends"]["halves"].items():
            half_label = f"{half} (1-18)" if half == 1 else f"{half} (19-36)" if half == 2 else str(half)
            if data["percent_deviation"] > 0:
                reason = f"Trending half (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                halves_candidates.setdefault(half_label, []).append(reason)

    sorted_halves_candidates = sorted(halves_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for half, reasons in sorted_halves_candidates[:MAX_PREDICTED_HALVES]:
        predictions["predicted_sections"]["halves"].append({"half": half, "reason": "; ".join(reasons)})
    if sorted_halves_candidates:
        predictions["prediction_summary"].append(f"Suggesting halves (1-18/19-36) that are trending.")


    # --- 6. Section Predictions (Even/Odd) ---
    even_odd_candidates = {} # type ("Even"/"Odd") -> reason list
    if trends.get("category_trends", {}).get("even_odd"):
        for eo_type, data in trends["category_trends"]["even_odd"].items():
            if data["percent_deviation"] > 0:
                reason = f"Trending {eo_type} (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                even_odd_candidates.setdefault(eo_type.capitalize(), []).append(reason)

    sorted_eo_candidates = sorted(even_odd_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for eo_type, reasons in sorted_eo_candidates[:MAX_PREDICTED_EVEN_ODD]:
        predictions["predicted_sections"]["even_odd"].append({"type": eo_type, "reason": "; ".join(reasons)})
    if sorted_eo_candidates:
        predictions["prediction_summary"].append(f"Suggesting Even/Odd bets that are trending.")

    if not predictions["prediction_summary"] and len(results_history) > 0 :
         predictions["prediction_summary"].append("No strong indicators for specific predictions with current data and thresholds. Consider more spins or adjusting analysis settings.")
    elif len(results_history) == 0:
        predictions["prediction_summary"].append("No data provided for analysis, so no predictions can be generated.")


    return predictions


if __name__ == '__main__':
    # Example usage for testing - requires comprehensive dummy analysis_results
    print("Testing Prediction Engine...")

    # Construct a sample analysis_results structure (can be quite verbose)
    sample_results_history = [1, 10, 1, 20, 1, 30, 7, 7, 7, 19, 25, 0] # 12 spins

    # A very simplified sample, real analysis_results would come from analysis_engine.py
    # and be much more detailed.
    sample_analysis_results = {
        "trends": {
            "hot_numbers": [{"number": 1, "actual": 3, "expected": 0.32}],
            "category_trends": {
                "dozens": {1: {"actual": 6, "expected": 3.8, "percent_deviation": 0.57}}, # Dozen 1 is hot
                "columns": {1: {"actual": 5, "expected": 3.8, "percent_deviation": 0.31}}, # Col 1 is hot
                "halves": {1: {"actual": 8, "expected": 5.8, "percent_deviation": 0.38}}, # 1-18 is hot
            }
        },
        "patterns": {
            "number_repeats": {"longest_streak": 3, "number_for_longest_streak": 7, "total_immediate_repeats": 3},
            "consecutive_dozen_streak": {"longest_streak": 4, "dozen": 1},
        },
        "biases": {
             "sectional_bias": {
                 "Voisins du Zero": {"status": "over_represented", "observed_hits": 5, "expected_hits":2.5, "deviation_percent":100.0}
             }
        },
        "clusters": {
            "hot_zones": [
                {"center_number": 1, "arc": [33,1,20,14,31], "percent_deviation": 0.6}
            ]
        }
    }

    predictions = generate_predictions(sample_analysis_results, sample_results_history)
    import json
    print(json.dumps(predictions, indent=4))

    empty_analysis = {key: {} for key in ["trends", "patterns", "biases", "clusters"]}
    predictions_empty = generate_predictions(empty_analysis, [])
    print("\nPredictions with empty analysis and no history:")
    print(json.dumps(predictions_empty, indent=4))

    predictions_empty_with_history = generate_predictions(empty_analysis, [1,2,3,4,5,6,7,8,9,10])
    print("\nPredictions with empty analysis but with history:")
    print(json.dumps(predictions_empty_with_history, indent=4))
