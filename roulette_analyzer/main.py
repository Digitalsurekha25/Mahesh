import json
from src.input_handler import get_manual_input
from src.analysis_engine import (
    calculate_frequencies,
    identify_trends,
    detect_patterns,
    detect_biases,
    analyze_wheel_clusters,
    WHEEL_ORDER, # Constant for wheel layout
    ROULETTE_WHEEL # For colors
)
from src.prediction_engine import generate_predictions

# --- Display Helper Functions ---

def print_section_header(title):
    print(f"\n{'='*10} {title.upper()} {'='*10}")

def display_frequencies(freq_data):
    print_section_header("Frequency Analysis")
    if not freq_data or not freq_data.get("number_frequencies"):
        print("No frequency data to display.")
        return

    print(f"Total Spins: {freq_data.get('total_spins', 0)}")

    print("\n--- Number Frequencies ---")
    # Sort by number for consistent display
    num_freq_sorted = sorted(freq_data["number_frequencies"].items(), key=lambda item: int(item[0]))
    for num, count in num_freq_sorted:
        color = ROULETTE_WHEEL.get(int(num), "N/A")
        print(f"Number {num} ({color}): {count} time(s)")

    print("\n--- Color Frequencies ---")
    for color, count in freq_data.get("color_frequencies", {}).items():
        print(f"{color.capitalize()}: {count} time(s)")

    for cat_name in ["Dozen", "Column", "Half", "Even/Odd"]:
        print(f"\n--- {cat_name} Frequencies ---")
        key_name = f"{cat_name.lower().replace('/','_')}_frequencies" # e.g. dozen_frequencies
        for item, count in freq_data.get(key_name, {}).items():
            print(f"{cat_name} {item}: {count} time(s)")

def display_trends(trend_data):
    print_section_header("Trend Analysis")
    if not trend_data or trend_data.get("message", "").startswith("Insufficient data"):
        print(trend_data.get("message", "No trend data to display or insufficient data."))
        return

    print(f"Status: {trend_data.get('message', 'Analysis performed.')}")

    if trend_data.get("hot_numbers"):
        print("\n--- Hot Numbers (appearing more than expected) ---")
        for item in trend_data["hot_numbers"]:
            print(f"Number {item['number']} (Actual: {item['actual']}, Expected: {item['expected']:.1f})")

    if trend_data.get("cold_numbers"):
        print("\n--- Cold Numbers (appearing less than expected) ---")
        for item in trend_data["cold_numbers"]:
            print(f"Number {item['number']} (Actual: {item['actual']}, Expected: {item['expected']:.1f})")

    if trend_data.get("category_trends"):
        print("\n--- Category Trends (deviations from expected) ---")
        for category, trends in trend_data["category_trends"].items():
            print(f"  Category: {category.capitalize()}")
            for item, data in trends.items():
                print(f"    {item}: Actual: {data['actual']}, Expected: {data['expected']:.1f} (Deviation: {data['percent_deviation']:.1%})")
    # Optionally, print detailed number_deviations if desired (can be verbose)
    # print("\n--- Detailed Number Deviations ---")
    # for num, data in trend_data.get("number_deviations", {}).items():
    #     print(f"Num {num}: Actual={data['actual']}, Expected={data['expected']:.2f}, Deviation={data['deviation']:.2f} ({data['percent_deviation']:.1%})")


def display_patterns(pattern_data):
    print_section_header("Pattern Detection")
    if not pattern_data or pattern_data.get("message", "").startswith("Insufficient data"):
        print(pattern_data.get("message", "No pattern data to display or insufficient data."))
        return

    print(f"Status: {pattern_data.get('message', 'Analysis performed.')}")

    nr = pattern_data.get("number_repeats", {})
    if nr:
        print("\n--- Number Repeats ---")
        print(f"  Total immediate number repeats: {nr.get('total_immediate_repeats',0)}")
        if nr.get("number_for_longest_streak") is not None:
            print(f"  Longest single number streak: {nr['longest_streak']} (for number {nr['number_for_longest_streak']})")
        if nr.get("counts"):
             print(f"  Counts of repeating numbers: {dict(nr['counts'])}")


    acs = pattern_data.get("alternating_color_streak", 0)
    print(f"\n--- Alternating Colors (Red/Black) ---")
    print(f"  Longest alternating R/B streak: {acs}")

    cds = pattern_data.get("consecutive_dozen_streak", {})
    if cds and cds.get("longest_streak", 0) > 0:
        print("\n--- Consecutive Dozens ---")
        print(f"  Longest dozen streak: {cds['longest_streak']} (for dozen {cds['dozen']})")

    ccs = pattern_data.get("consecutive_column_streak", {})
    if ccs and ccs.get("longest_streak", 0) > 0:
        print("\n--- Consecutive Columns ---")
        print(f"  Longest column streak: {ccs['longest_streak']} (for column {ccs['column']})")


def display_biases(bias_data):
    print_section_header("Bias Detection")
    if not bias_data or bias_data.get("message", "").startswith("Insufficient data"):
        print(bias_data.get("message", "No bias data to display or insufficient data."))
        return

    print(f"Status: {bias_data.get('message', 'Analysis performed.')}")
    print(f"Overall Interpretation: {bias_data.get('interpretation', 'N/A')}")

    cs_test = bias_data.get("chi_squared_test", {})
    if cs_test.get("statistic") is not None:
        print("\n--- Chi-Squared Test for Number Distribution ---")
        print(f"  Statistic: {cs_test['statistic']:.2f}")
        print(f"  Critical Value (p=0.05, df=36): {cs_test['critical_value']:.2f}")
        print(f"  Suggestion: {'Potential bias' if cs_test['is_biased_suggestion'] else 'No strong bias'} suggested.")
        if cs_test.get("message"): print(f"  Note: {cs_test['message']}")

    sb = bias_data.get("sectional_bias", {})
    if sb:
        print("\n--- Sectional Bias ---")
        for section, data in sb.items():
            print(f"  Section: {section}")
            print(f"    Observed Hits: {data['observed_hits']}, Expected Hits: {data['expected_hits']:.1f}")
            print(f"    Deviation: {data['deviation_percent']:.1f}%, Status: {data['status']}")

def display_clusters(cluster_data):
    print_section_header("Wheel Cluster Analysis")
    if not cluster_data or cluster_data.get("message", "").startswith("Insufficient data"):
        print(cluster_data.get("message", "No cluster data to display or insufficient data."))
        return

    print(f"Status: {cluster_data.get('message', 'Analysis performed.')}")
    print(f"Arc Size Used: {cluster_data.get('arc_size')}")

    if cluster_data.get("hot_zones"):
        print("\n--- Hot Wheel Zones (arcs with higher than expected frequency) ---")
        for zone in cluster_data["hot_zones"]:
            print(f"  Arc centered at {zone['center_number']} (Numbers: {zone['arc']})")
            print(f"    Observed: {zone['observed_freq']}, Expected: {zone['expected_freq']:.1f} (Deviation: {zone['percent_deviation']:.1%})")

    if cluster_data.get("cold_zones"):
        print("\n--- Cold Wheel Zones (arcs with lower than expected frequency) ---")
        for zone in cluster_data["cold_zones"]:
            print(f"  Arc centered at {zone['center_number']} (Numbers: {zone['arc']})")
            print(f"    Observed: {zone['observed_freq']}, Expected: {zone['expected_freq']:.1f} (Deviation: {zone['percent_deviation']:.1%})")
    print(f"Note: {cluster_data.get('note','')}")


def display_predictions(pred_data):
    print_section_header("Predictions")
    if not pred_data:
        print("No prediction data available.")
        return

    print("--- Prediction Summary ---")
    if pred_data.get("prediction_summary"):
        for note in pred_data["prediction_summary"]:
            print(f"- {note}")
    else:
        print("No specific prediction drivers identified.")

    print("\n--- Predicted Numbers ---")
    if pred_data.get("predicted_numbers"):
        for p_num in pred_data["predicted_numbers"]:
            print(f"  Number: {p_num['number']} (Reason: {p_num['reason']})")
    else:
        print("  No specific numbers predicted.")

    for cat_key, cat_name, item_key in [
        ("predicted_dozens", "Dozens", "dozen"),
        ("predicted_columns", "Columns", "column")
    ]:
        print(f"\n--- Predicted {cat_name} ---")
        if pred_data.get(cat_key):
            for p_item in pred_data[cat_key]:
                print(f"  {cat_name.singular()}: {p_item[item_key]} (Reason: {p_item['reason']})")
        else:
            print(f"  No specific {cat_name.lower()} predicted.")

    print("\n--- Predicted Sections ---")
    sections = pred_data.get("predicted_sections", {})
    if sections.get("voisins_tiers_orphelins"):
        for p_sec in sections["voisins_tiers_orphelins"]:
            print(f"  Bet Type: {p_sec['section']} (Reason: {p_sec['reason']})")
    if sections.get("halves"):
        for p_half in sections["halves"]:
            print(f"  Bet Type: Half {p_half['half']} (Reason: {p_half['reason']})")
    if sections.get("even_odd"):
        for p_eo in sections["even_odd"]:
            print(f"  Bet Type: {p_eo['type']} (Reason: {p_eo['reason']})")
    if not any(sections.values()):
         print("  No specific sections predicted.")

    print(f"\n--- Confidence Note ---")
    print(pred_data.get("confidence_note", "Gamble responsibly."))


def show_main_menu():
    print("\nRoulette Analyzer Menu:")
    print("1. Enter Roulette Results")
    print("2. View Full Analysis Details")
    print("3. View Predictions")
    print("4. View Current Results History")
    print("5. Exit")
    return input("Choose an option (1-5): ")

# --- Main Application Logic ---
def main():
    print("Welcome to the Roulette Analyzer CLI!")
    roulette_numbers = []
    analysis_results = {} # To store all analysis outputs
    predictions = {}

    while True:
        choice = show_main_menu()
        needs_recalculation = False

        if choice == '1':
            print("\n--- Enter Roulette Results ---")
            new_numbers = get_manual_input()
            if new_numbers:
                roulette_numbers.extend(new_numbers)
                print(f"Added {len(new_numbers)} new results. Total results: {len(roulette_numbers)}")
                needs_recalculation = True
            else:
                print("No new numbers were added.")

        elif choice in ['2', '3']:
            if not roulette_numbers:
                print("\nNo results entered yet. Please enter results first (Option 1).")
                continue

            if needs_recalculation or not analysis_results.get("frequencies"): # Recalculate if new numbers or first time
                print("\nCalculating new analysis...")
                total_spins = len(roulette_numbers)
                analysis_results["frequencies"] = calculate_frequencies(roulette_numbers)
                analysis_results["trends"] = identify_trends(analysis_results["frequencies"], total_spins)
                analysis_results["patterns"] = detect_patterns(roulette_numbers, analysis_results["frequencies"])
                number_deviations_data = analysis_results["trends"].get("number_deviations", {})
                analysis_results["biases"] = detect_biases(analysis_results["frequencies"], total_spins, number_deviations_data)
                analysis_results["clusters"] = analyze_wheel_clusters(analysis_results["frequencies"], total_spins, WHEEL_ORDER)
                predictions = generate_predictions(analysis_results, roulette_numbers)
                needs_recalculation = False # Reset flag
                print("Analysis complete.")

            if choice == '2':
                display_frequencies(analysis_results.get("frequencies", {}))
                display_trends(analysis_results.get("trends", {}))
                display_patterns(analysis_results.get("patterns", {}))
                display_biases(analysis_results.get("biases", {}))
                display_clusters(analysis_results.get("clusters", {}))

            elif choice == '3':
                 # Predictions might need recalculation even if analysis was done, if parameters change later.
                 # For now, it's tied to the main analysis recalculation.
                if not predictions: # Ensure predictions are generated if not already
                    print("\nGenerating predictions...")
                    predictions = generate_predictions(analysis_results, roulette_numbers)
                display_predictions(predictions)

        elif choice == '4':
            print_section_header("Current Results History")
            if roulette_numbers:
                print(f"Total spins recorded: {len(roulette_numbers)}")
                print(roulette_numbers)
            else:
                print("No results entered yet.")

        elif choice == '5':
            print("\nExiting Roulette Analyzer. Gamble responsibly!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
