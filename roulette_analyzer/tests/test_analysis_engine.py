import unittest
import json # For comparing complex dicts if needed, though direct comparison is usually fine.
from collections import Counter

from src.analysis_engine import (
    calculate_frequencies,
    identify_trends,
    detect_patterns,
    detect_biases,
    analyze_wheel_clusters,
    WHEEL_ORDER,
    MIN_SPINS_FOR_TRENDS,
    MIN_SPINS_FOR_PATTERNS,
    MIN_SPINS_FOR_BIAS,
    MIN_SPINS_FOR_CLUSTERS
)

class TestAnalysisEngine(unittest.TestCase):

    # --- Test calculate_frequencies ---
    def test_calculate_frequencies_empty(self):
        results = []
        expected = {
            "number_frequencies": Counter(), "color_frequencies": Counter(),
            "dozen_frequencies": Counter(), "column_frequencies": Counter(),
            "half_frequencies": Counter(), "even_odd_frequencies": Counter(),
            "total_spins": 0
        }
        self.assertEqual(calculate_frequencies(results), expected)

    def test_calculate_frequencies_simple(self):
        results = [0, 1, 10, 13, 36] # Green, Red, Black, Black, Red
        expected_num_freq = {0:1, 1:1, 10:1, 13:1, 36:1}
        expected_color_freq = {'green':1, 'red':2, 'black':2}
        expected_dozen_freq = {1:2, 2:1, 3:1} # 1(1,10), 13(2nd), 36(3rd)
        expected_col_freq = {1:2, 2:1, 3:1} # 1(1,10,13), 36(3rd) -> 1(1,10), 13(col1), 36(col3) -> Error in manual calc above.
                                           # Corrected: 0:None, 1(C1), 10(C1), 13(C1), 36(C3)
        expected_col_freq_corrected = {1:3, 3:1}
        expected_half_freq = {1:2, 2:1} # 1,10 (1st half), 13 (1st half), 36 (2nd half) -> 1,10,13 (1st), 36 (2nd)
        expected_half_freq_corrected = {1:3, 2:1}
        expected_eo_freq = {'odd':2, 'even':2} # 1,13 (odd), 10,36 (even)

        actual = calculate_frequencies(results)
        self.assertEqual(actual["number_frequencies"], expected_num_freq)
        self.assertEqual(actual["color_frequencies"], expected_color_freq)
        self.assertEqual(actual["dozen_frequencies"], expected_dozen_freq)
        self.assertEqual(actual["column_frequencies"], expected_col_freq_corrected)
        self.assertEqual(actual["half_frequencies"], expected_half_freq_corrected)
        self.assertEqual(actual["even_odd_frequencies"], expected_eo_freq)
        self.assertEqual(actual["total_spins"], 5)

    # --- Test identify_trends ---
    def test_identify_trends_insufficient_data(self):
        results_short = [1] * (MIN_SPINS_FOR_TRENDS - 1)
        freq_short = calculate_frequencies(results_short)
        trends = identify_trends(freq_short, len(results_short))
        self.assertTrue(trends["message"].startswith("Insufficient data"))
        self.assertEqual(trends["hot_numbers"], [])
        self.assertEqual(trends["cold_numbers"], [])

    def test_identify_trends_clear_trends(self):
        # Make number 7 very hot, number 1 very cold
        results = [7]*15 + [1]*1 + [2]*5 + [3]*5 + [4]*5 # 31 spins, 7 appears 15 times, 1 appears 1 time
        # Expected for 7: 31/37 = 0.83 spins. Actual 15. Deviation is large.
        # Expected for 1: 0.83 spins. Actual 1. Deviation small.
        # Make Red hot: 1,3,7 are red. 15+5+1=21 red. Black: 2,4 are black. 5+5=10 black.
        # Total spins = 31. Expected Red/Black = 31 * 18/37 = ~15.08
        freq = calculate_frequencies(results)
        trends = identify_trends(freq, len(results))

        self.assertIn({"number": 7, "actual": 15, "expected": round(31/37,2)}, trends["hot_numbers"])
        # For cold numbers, the threshold might be tricky with low expecteds.
        # If a number is expected 0.83 times, appearing 0 times is a large % deviation but might not be "cold" in spirit yet.
        # The current logic: percent_deviation < -THRESHOLD and actual_freq < expected_number_freq
        # If 1 is expected 0.83 and appears 1, it's not cold by this.
        # If we had a number like 5 (expected 0.83) that appeared 0 times:
        # results_for_cold = [7]*15 + [2]*5 + [3]*5 + [4]*5 # Number 5 is missing
        # freq_cold = calculate_frequencies(results_for_cold)
        # trends_cold = identify_trends(freq_cold, len(results_for_cold))
        # self.assertIn({"number": 5, "actual": 0, "expected": round(len(results_for_cold)/37,2)}, trends_cold["cold_numbers"])

        self.assertIn('red', trends["category_trends"]["colors"])
        self.assertTrue(trends["category_trends"]["colors"]['red']["percent_deviation"] > 0)


    # --- Test detect_patterns ---
    def test_detect_patterns_insufficient_data(self):
        results_short = [1] * (MIN_SPINS_FOR_PATTERNS -1)
        freq_short = calculate_frequencies(results_short)
        patterns = detect_patterns(results_short, freq_short)
        self.assertTrue(patterns["message"].startswith("Insufficient data"))

    def test_detect_patterns_all_same_number(self):
        results = [7] * 10
        freq = calculate_frequencies(results)
        patterns = detect_patterns(results, freq)
        self.assertEqual(patterns["number_repeats"]["total_immediate_repeats"], 9)
        self.assertEqual(patterns["number_repeats"]["longest_streak"], 10)
        self.assertEqual(patterns["number_repeats"]["number_for_longest_streak"], 7)
        self.assertEqual(patterns["alternating_color_streak"], 1) # Color of 7 is red. Stays red. So streak of 1.

    def test_detect_patterns_alternating_colors(self):
        results = [1, 2, 3, 4, 1, 2, 0, 3, 4] # R, B, R, B, R, B, G, R, B
        freq = calculate_frequencies(results)
        patterns = detect_patterns(results, freq)
        self.assertEqual(patterns["alternating_color_streak"], 6) # RBRBRB

    def test_detect_patterns_consecutive_dozens(self):
        results = [1,2,3,4,5,6, 13,14,15] # 6 in D1, then 3 in D2
        freq = calculate_frequencies(results)
        patterns = detect_patterns(results, freq)
        self.assertEqual(patterns["consecutive_dozen_streak"]["longest_streak"], 6)
        self.assertEqual(patterns["consecutive_dozen_streak"]["dozen"], 1)


    # --- Test detect_biases ---
    def test_detect_biases_insufficient_data(self):
        results_short = [1] * (MIN_SPINS_FOR_BIAS - 1)
        freq = calculate_frequencies(results_short)
        trends = identify_trends(freq, len(results_short))
        biases = detect_biases(freq, len(results_short), trends["number_deviations"])
        self.assertTrue(biases["message"].startswith("Insufficient data"))

    def test_detect_biases_uniform_data(self):
        # Approx 2 hits per number for 74 spins
        results = []
        for i in range(37): results.extend([i,i])
        freq = calculate_frequencies(results)
        trends = identify_trends(freq, len(results))
        biases = detect_biases(freq, len(results), trends["number_deviations"])
        self.assertFalse(biases["chi_squared_test"]["is_biased_suggestion"])
        for section_name, data in biases["sectional_bias"].items():
            self.assertEqual(data["status"], "as_expected")

    def test_detect_biases_clear_bias(self):
        results = [7]*40 + list(range(10)) # 7 is very over-represented, 50 spins
        freq = calculate_frequencies(results)
        trends = identify_trends(freq, len(results))
        biases = detect_biases(freq, len(results), trends["number_deviations"])
        self.assertTrue(biases["chi_squared_test"]["is_biased_suggestion"])
        # Check if section containing 7 (Voisins) is over-represented
        self.assertEqual(biases["sectional_bias"]["Voisins du Zero"]["status"], "over_represented")


    # --- Test analyze_wheel_clusters ---
    def test_analyze_wheel_clusters_insufficient_data(self):
        results_short = [1] * (MIN_SPINS_FOR_CLUSTERS -1)
        freq = calculate_frequencies(results_short)
        clusters = analyze_wheel_clusters(freq, len(results_short), WHEEL_ORDER)
        self.assertTrue(clusters["message"].startswith("Insufficient data"))

    def test_analyze_wheel_clusters_hot_zone(self):
        # Make zone around 0 (0, 32, 15, 19, 4) hot.
        # WHEEL_ORDER[0..4] are these numbers.
        # Arc centered at WHEEL_ORDER[2]=15 should be hot.
        hot_zone_numbers = WHEEL_ORDER[0:5] # 0, 32, 15, 19, 4
        results = []
        for _ in range(8): # make each number in zone appear 8 times
            results.extend(hot_zone_numbers)
        # Add other numbers to dilute, total 40 + 10 = 50 spins
        other_numbers = [n for n in WHEEL_ORDER if n not in hot_zone_numbers][:10]
        results.extend(other_numbers)

        freq = calculate_frequencies(results)
        clusters = analyze_wheel_clusters(freq, len(results), WHEEL_ORDER)

        found_hot_zone_around_15 = False
        for zone in clusters["hot_zones"]:
            if zone["center_number"] == 15 and set(zone["arc"]) == set(hot_zone_numbers) :
                found_hot_zone_around_15 = True
                break
        self.assertTrue(found_hot_zone_around_15, "Expected hot zone around number 15 not found or arc numbers mismatch.")

    def test_analyze_wheel_clusters_uniform_data(self):
        results = []
        for i in range(2): results.extend(WHEEL_ORDER) # 74 spins, 2 hits per number
        freq = calculate_frequencies(results)
        clusters = analyze_wheel_clusters(freq, len(results), WHEEL_ORDER)
        self.assertEqual(clusters["hot_zones"], [])
        self.assertEqual(clusters["cold_zones"], [])


if __name__ == '__main__':
    unittest.main()
