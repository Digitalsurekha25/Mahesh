import unittest
from src.prediction_engine import generate_predictions

class TestPredictionEngine(unittest.TestCase):

    def test_generate_predictions_hot_number_and_zone(self):
        analysis_results = {
            "trends": {
                "hot_numbers": [{"number": 7, "actual": 10, "expected": 2.0}],
                "category_trends": {}, "number_deviations": {} # Simplified
            },
            "patterns": {},
            "biases": {},
            "clusters": {
                "hot_zones": [{"center_number": 7, "arc": [29, 7, 28, 12, 35], "percent_deviation": 0.5}]
            }
        }
        results_history = [7]*10 + [1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5] # 30 spins
        predictions = generate_predictions(analysis_results, results_history)

        self.assertTrue(any(p['number'] == 7 for p in predictions['predicted_numbers']))
        self.assertIn("Hot number", predictions['predicted_numbers'][0]['reason'])
        self.assertIn("Part of hot wheel zone", predictions['predicted_numbers'][0]['reason'])

    def test_generate_predictions_trending_dozen_and_streak(self):
        analysis_results = {
            "trends": {
                "hot_numbers": [],
                "category_trends": {
                    "dozens": {1: {"actual": 15, "expected": 10.0, "percent_deviation": 0.5}}
                },
                 "number_deviations": {}
            },
            "patterns": {
                "consecutive_dozen_streak": {"longest_streak": 4, "dozen": 1}
            },
            "biases": {}, "clusters": {}
        }
        results_history = [1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,13,14,15,13,14,15,25,26,27,25,26,27,25,26,27] # 30 spins
        predictions = generate_predictions(analysis_results, results_history)

        self.assertTrue(any(p['dozen'] == 1 for p in predictions['predicted_dozens']))
        self.assertIn("Trending dozen", predictions['predicted_dozens'][0]['reason'])
        self.assertIn("Recent longest streak", predictions['predicted_dozens'][0]['reason'])

    def test_generate_predictions_sectional_bias(self):
        analysis_results = {
            "trends": {}, "patterns": {},
            "biases": {
                "sectional_bias": {
                    "Voisins du Zero": {"status": "over_represented", "observed_hits": 20, "expected_hits": 10, "deviation_percent": 1.0}
                }
            },
            "clusters": {}
        }
        results_history = [0]*20 + [1]*10 # 30 spins
        predictions = generate_predictions(analysis_results, results_history)

        predicted_vto = predictions["predicted_sections"]["voisins_tiers_orphelins"]
        self.assertTrue(any(p['section'] == "Voisins du Zero" for p in predicted_vto))
        self.assertIn("Over-represented in bias analysis", predicted_vto[0]['reason'])

    def test_generate_predictions_no_strong_signals(self):
        analysis_results = { # Essentially empty or non-triggering data
            "trends": {"hot_numbers": [], "cold_numbers":[], "category_trends":{}, "number_deviations":{}},
            "patterns": {"number_repeats":{}, "alternating_color_streak":0, "consecutive_dozen_streak":{}, "consecutive_column_streak":{}},
            "biases": {"chi_squared_test":{}, "sectional_bias":{}},
            "clusters": {"hot_zones":[], "cold_zones":[]}
        }
        results_history = list(range(30)) # 30 distinct spins
        predictions = generate_predictions(analysis_results, results_history)

        self.assertEqual(len(predictions["predicted_numbers"]), 0)
        self.assertEqual(len(predictions["predicted_dozens"]), 0)
        self.assertEqual(len(predictions["predicted_columns"]), 0)
        self.assertTrue(all(not val for val in predictions["predicted_sections"].values()))
        self.assertIn("No strong indicators", predictions["prediction_summary"][0])

    def test_generate_predictions_insufficient_data_for_all_analyses(self):
        # This simulates when main.py calls generate_predictions with empty analysis dicts
        # because total_spins was too low for any analysis module to run.
        empty_analysis_results = {
            "trends": {}, "patterns": {}, "biases": {}, "clusters": {}
        }
        results_history = [1, 2, 3] # Very short history
        predictions = generate_predictions(empty_analysis_results, results_history)

        self.assertEqual(len(predictions["predicted_numbers"]), 0)
        self.assertEqual(len(predictions["predicted_dozens"]), 0)
        # ... and so on for other categories
        self.assertIn("No strong indicators", predictions["prediction_summary"][0])
        self.assertTrue(predictions["confidence_note"]) # Ensure note is always present

    def test_generate_predictions_empty_history_and_empty_analysis(self):
        empty_analysis_results = {
            "trends": {}, "patterns": {}, "biases": {}, "clusters": {}
        }
        results_history = []
        predictions = generate_predictions(empty_analysis_results, results_history)
        self.assertIn("No data provided for analysis", predictions["prediction_summary"][0])


if __name__ == '__main__':
    unittest.main()
