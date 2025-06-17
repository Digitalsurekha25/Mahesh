# Handles prediction logic for Roulette Analyzer.

from collections import Counter
import os
import joblib
import numpy as np

# Assuming ml_utils is in the same 'src' package
try:
    from .ml_utils import extract_sequences
except ImportError:
    from ml_utils import extract_sequences

# Define model path and feature window size (must match training)
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
DOZEN_MODEL_FILENAME = os.path.join(MODEL_DIR, 'predict_next_dozen_model.joblib')
COLUMN_MODEL_FILENAME = os.path.join(MODEL_DIR, 'predict_next_column_model.joblib')
SECTION_MODEL_FILENAME = os.path.join(MODEL_DIR, 'predict_next_section_model.joblib') # For V/T/O/Z etc.
NUMBER_MODEL_FILENAME = os.path.join(MODEL_DIR, 'predict_next_number_model.joblib')

FEATURE_WINDOW_SIZE = 5 # Assuming all models use the same window size for now

MAX_PREDICTED_NUMBERS = 5
MAX_PREDICTED_DOZENS_STATISTICAL = 1
MAX_PREDICTED_COLUMNS_STATISTICAL = 1
MAX_PREDICTED_OTS_STATISTICAL = 1
MAX_PREDICTED_HALVES_STATISTICAL = 1
MAX_PREDICTED_EVEN_ODD_STATISTICAL = 1


def _get_ml_prediction(model_filename: str, model_name: str, current_numbers_history: list[int], feature_window_size: int, value_map: dict = None) -> dict:
    """
    Generic helper to load a trained model and predict for the current history.
    Returns a dictionary with the prediction or error/status.
    """
    prediction_result = {
        "model_name": model_name,
        "prediction": "N/A",
        "status": "",
        # "probabilities": {} # Optional placeholder
    }

    # MODEL_DIR is created by train_models.py if it doesn't exist.
    # Here, we just check for the specific model file.
    if not os.path.exists(model_filename):
        prediction_result["status"] = "Model file not found. Please train the corresponding AI/ML model first."
        return prediction_result

    if len(current_numbers_history) < feature_window_size:
        prediction_result["status"] = f"Not enough data. Need at least {feature_window_size} spins for this AI/ML prediction."
        return prediction_result

    try:
        model = joblib.load(model_filename)
    except Exception as e:
        prediction_result["status"] = f"Error loading model ({os.path.basename(model_filename)}): {str(e)}"
        return prediction_result

    last_sequence = np.array([current_numbers_history[-feature_window_size:]])

    if last_sequence.shape[1] != feature_window_size:
        prediction_result["status"] = "Error preparing feature vector (sequence too short for window)."
        return prediction_result

    try:
        predicted_code = model.predict(last_sequence)[0]
        # if hasattr(model, 'predict_proba'):
        #    probabilities = model.predict_proba(last_sequence)[0]
        #    # Example: prediction_result["probabilities"] = dict(zip(model.classes_, probabilities))

        if value_map:
            prediction_result["prediction"] = value_map.get(predicted_code, f"Unknown Code: {predicted_code}")
        else: # For direct number prediction
            prediction_result["prediction"] = str(predicted_code) # Ensure it's string for consistency

        prediction_result["status"] = "Prediction successful."
    except Exception as e:
        prediction_result["status"] = f"Error during prediction with {os.path.basename(model_filename)}: {str(e)}"

    return prediction_result


def generate_predictions(analysis_results: dict, results_history: list[int]) -> dict:
    """
    Generates predictions based on the comprehensive analysis results,
    including both statistical and ML-based predictions.
    """
    # Initialize from statistical analysis if available, or set up structure
    # This assumes analysis_results might contain 'statistical_predictions' and 'prediction_summary' from a prior step
    # or that this function is the sole generator of all predictions.
    # For clarity, this function will now generate statistical predictions internally first.

    predictions = {
        "predicted_numbers": [],
        "predicted_dozens": [],
        "predicted_columns": [],
        "predicted_sections": {
            "voisins_tiers_orphelins": [],
            "halves": [],
            "even_odd": []
        },
        "ml_based_predictions": [],
        "prediction_summary": [],
        "confidence_note": "Predictions are based on statistical analysis and/or AI/ML models using past results and are not guarantees of future outcomes. The more data provided, the more meaningful the analysis."
    }

    # --- Statistical Predictions (copied and adapted from previous version) ---
    trends = analysis_results.get('trends', {})
    patterns = analysis_results.get('patterns', {})
    biases = analysis_results.get('biases', {})
    clusters = analysis_results.get('clusters', {})

    number_candidates = {}
    if trends.get("hot_numbers"):
        for item in trends["hot_numbers"]:
            num = item["number"]
            reason = f"Hot number (actual: {item['actual']}, expected: {item['expected']:.1f})"
            number_candidates.setdefault(num, []).append(reason)
    if clusters.get("hot_zones"):
        for zone in clusters["hot_zones"]:
            for num in zone["arc"]:
                reason = f"Part of hot wheel zone centered at {zone['center_number']} (arc dev: {zone['percent_deviation']:.0%})"
                number_candidates.setdefault(num, []).append(reason)
    if patterns.get("number_repeats") and patterns["number_repeats"].get("longest_streak", 0) >= 3 :
        num_streak = patterns["number_repeats"]["number_for_longest_streak"]
        if num_streak is not None:
            reason = f"Part of longest recent streak of {patterns['number_repeats']['longest_streak']}"
            number_candidates.setdefault(num_streak, []).append(reason)
    sorted_number_candidates = sorted(number_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for num, reasons in sorted_number_candidates[:MAX_PREDICTED_NUMBERS]:
        predictions["predicted_numbers"].append({"number": num, "reason": "; ".join(reasons)})
    if sorted_number_candidates:
         predictions["prediction_summary"].append(f"Statistically prioritizing numbers that are hot or in hot wheel zones.")

    dozen_candidates = {}
    if trends.get("category_trends", {}).get("dozens"):
        for dozen, data in trends["category_trends"]["dozens"].items():
            if data["percent_deviation"] > 0:
                 reason = f"Trending dozen (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                 dozen_candidates.setdefault(int(dozen), []).append(reason)
    if patterns.get("consecutive_dozen_streak", {}).get("longest_streak", 0) >= 3:
        dozen = patterns["consecutive_dozen_streak"]["dozen"]
        if dozen: # Dozen can be None if streak was for 0 or not set
            reason = f"Recent longest streak of {patterns['consecutive_dozen_streak']['longest_streak']} for dozen {dozen}"
            dozen_candidates.setdefault(dozen, []).append(reason)
    sorted_dozen_candidates = sorted(dozen_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for dozen, reasons in sorted_dozen_candidates[:MAX_PREDICTED_DOZENS_STATISTICAL]:
        predictions["predicted_dozens"].append({"dozen": dozen, "reason": "Statistical: " + "; ".join(reasons)})
    if sorted_dozen_candidates:
        predictions["prediction_summary"].append(f"Statistically suggesting dozens that are trending or show recent streaks.")

    column_candidates = {}
    if trends.get("category_trends", {}).get("columns"):
        for col, data in trends["category_trends"]["columns"].items():
            if data["percent_deviation"] > 0:
                 reason = f"Trending column (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                 column_candidates.setdefault(int(col), []).append(reason)
    if patterns.get("consecutive_column_streak", {}).get("longest_streak", 0) >= 3:
        col = patterns["consecutive_column_streak"]["column"]
        if col: # Column can be None
            reason = f"Recent longest streak of {patterns['consecutive_column_streak']['longest_streak']} for column {col}"
            column_candidates.setdefault(col, []).append(reason)
    sorted_column_candidates = sorted(column_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for col, reasons in sorted_column_candidates[:MAX_PREDICTED_COLUMNS_STATISTICAL]:
        predictions["predicted_columns"].append({"column": col, "reason": "Statistical: " + "; ".join(reasons)})
    if sorted_column_candidates:
        predictions["prediction_summary"].append(f"Statistically suggesting columns that are trending or show recent streaks.")

    vto_candidates = {}
    if biases.get("sectional_bias"):
        for section_name, data in biases["sectional_bias"].items():
            if data["status"] == "over_represented":
                reason = f"Over-represented in bias analysis (obs: {data['observed_hits']}, exp: {data['expected_hits']:.1f}, dev: {data['deviation_percent']:.0%})"
                vto_candidates.setdefault(section_name, []).append(reason)
    sorted_vto_candidates = sorted(vto_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for section, reasons in sorted_vto_candidates[:MAX_PREDICTED_OTS_STATISTICAL]:
        predictions["predicted_sections"]["voisins_tiers_orphelins"].append({"section": section, "reason": "Statistical: " + "; ".join(reasons)})
    if sorted_vto_candidates:
        predictions["prediction_summary"].append(f"Statistically highlighting biased wheel sections.")

    halves_candidates = {}
    if trends.get("category_trends", {}).get("halves"):
        for half_key, data in trends["category_trends"]["halves"].items():
            half_label = f"1-18" if str(half_key) == '1' else (f"19-36" if str(half_key) == '2' else str(half_key))
            if data["percent_deviation"] > 0:
                reason = f"Trending half (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                halves_candidates.setdefault(half_label, []).append(reason)
    sorted_halves_candidates = sorted(halves_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for half, reasons in sorted_halves_candidates[:MAX_PREDICTED_HALVES_STATISTICAL]:
        predictions["predicted_sections"]["halves"].append({"half": half, "reason": "Statistical: " + "; ".join(reasons)})
    if sorted_halves_candidates:
        predictions["prediction_summary"].append(f"Statistically suggesting halves that are trending.")

    even_odd_candidates = {}
    if trends.get("category_trends", {}).get("even_odd"):
        for eo_type, data in trends["category_trends"]["even_odd"].items():
            if data["percent_deviation"] > 0:
                reason = f"Trending {eo_type} (actual: {data['actual']}, expected: {data['expected']:.1f}, dev: {data['percent_deviation']:.0%})"
                even_odd_candidates.setdefault(eo_type.capitalize(), []).append(reason)
    sorted_eo_candidates = sorted(even_odd_candidates.items(), key=lambda item: len(item[1]), reverse=True)
    for eo_type, reasons in sorted_eo_candidates[:MAX_PREDICTED_EVEN_ODD_STATISTICAL]:
        predictions["predicted_sections"]["even_odd"].append({"type": eo_type, "reason": "Statistical: " + "; ".join(reasons)})
    if sorted_eo_candidates:
        predictions["prediction_summary"].append(f"Statistically suggesting Even/Odd bets that are trending.")

    # --- ML-based Predictions ---
    if results_history: # Only run ML if there's some history
        # Define value maps for categorical predictions
        dozen_map = {0: "Zero (0)", 1: "1st Dozen (1-12)", 2: "2nd Dozen (13-24)", 3: "3rd Dozen (25-36)"}
        column_map = {0: "Zero (0)", 1: "Column 1", 2: "Column 2", 3: "Column 3"} # Assuming 0 for Zero's column if trained that way
        section_map = {0: "Zero (0)", 1: "Voisins du Zéro", 2: "Tiers du Cylindre", 3: "Orphelins"} # Example mapping

        ml_preds_to_run = [
            {"file": DOZEN_MODEL_FILENAME, "name": "Next Dozen (AI/ML)", "map": dozen_map},
            {"file": COLUMN_MODEL_FILENAME, "name": "Next Column (AI/ML)", "map": column_map},
            {"file": SECTION_MODEL_FILENAME, "name": "Next Section (AI/ML)", "map": section_map},
            {"file": NUMBER_MODEL_FILENAME, "name": "Next Number (AI/ML)", "map": None},
        ]

        for ml_config in ml_preds_to_run:
            ml_pred_info = _get_ml_prediction(
                ml_config["file"], ml_config["name"], results_history, FEATURE_WINDOW_SIZE, ml_config["map"]
            )
            predictions['ml_based_predictions'].append(ml_pred_info)

            # Add to summary only if there's a meaningful status or prediction
            if ml_pred_info["prediction"] != "N/A" and "successful" in ml_pred_info.get("status",""):
                 predictions["prediction_summary"].append(f"{ml_pred_info['model_name']} predicts: {ml_pred_info['prediction']}.")
            elif "Model file not found" not in ml_pred_info.get("status",""): # Don't clutter summary if model just isn't trained
                 predictions["prediction_summary"].append(f"{ml_pred_info['model_name']}: {ml_pred_info['status']}")

    # Final check for summary
    if not predictions["prediction_summary"] and len(results_history) > 0 :
         predictions["prediction_summary"].append("No strong statistical indicators found; AI/ML models might need training or more data.")
    elif len(results_history) == 0:
        predictions["prediction_summary"] = ["No data provided for analysis, so no predictions can be generated."] # Overwrite if empty history

    return predictions


if __name__ == '__main__':
    print("Testing Prediction Engine with generic ML component...")
    sample_ml_history = [10, 20, 5, 0, 15, 30, 1, 2, 3, 4, 5, 13, 14, 15, 16, 17, 25, 26, 27, 28, 29, 0]
    sample_analysis_results = {"trends": {}, "patterns": {}, "biases": {}, "clusters": {}} # Empty statistical results

    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    class DummyModel: # More generic dummy model
        def __init__(self, prediction_value=1, classes=None, n_features=FEATURE_WINDOW_SIZE):
            self.prediction_value = prediction_value
            self.classes_ = classes if classes is not None else np.array([0,1,2,3])
            self.n_features_in_ = n_features
        def predict(self, X):
            return np.array([self.prediction_value] * len(X))

    # Create dummy models for all types if they don't exist
    model_files_to_check = [
        DOZEN_MODEL_FILENAME, COLUMN_MODEL_FILENAME, SECTION_MODEL_FILENAME, NUMBER_MODEL_FILENAME
    ]
    for model_file in model_files_to_check:
        if not os.path.exists(model_file):
            print(f"Creating dummy model at {model_file} for testing.")
            # For number model, prediction_value should be a number e.g. 7
            pred_val = 7 if "number" in model_file else 1
            dummy_model = DummyModel(prediction_value=pred_val)
            joblib.dump(dummy_model, model_file)
        else:
            print(f"Using existing model at {model_file} for testing.")

    predictions_with_ml = generate_predictions(sample_analysis_results, sample_ml_history)
    import json
    print("\n--- Predictions with ML Components (using dummy models if real ones not trained) ---")
    print(json.dumps(predictions_with_ml, indent=4))

    # Test with short history
    short_history = [1,2,3] # Less than FEATURE_WINDOW_SIZE
    print(f"\n--- Predictions with short history ({len(short_history)} spins) ---")
    short_preds = generate_predictions(sample_analysis_results, short_history)
    print(json.dumps(short_preds, indent=4))
    # Expected: ML statuses should indicate not enough data. Statistical might also be minimal.

    # Test with one model missing
    if os.path.exists(NUMBER_MODEL_FILENAME):
        os.rename(NUMBER_MODEL_FILENAME, NUMBER_MODEL_FILENAME + ".backup_test")

    print("\n--- Predictions with Number Model missing ---")
    missing_model_preds = generate_predictions(sample_analysis_results, sample_ml_history)
    print(json.dumps(missing_model_preds, indent=4))
    # Expected: Status for Number model should be "Model file not found..."

    if os.path.exists(NUMBER_MODEL_FILENAME + ".backup_test"):
        os.rename(NUMBER_MODEL_FILENAME + ".backup_test", NUMBER_MODEL_FILENAME)
