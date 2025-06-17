from flask import Flask, request, jsonify, send_from_directory
import os
import json
from datetime import datetime, timezone
from collections import Counter

app = Flask(__name__)

IS_VERCEL = os.environ.get('VERCEL') == '1'
if IS_VERCEL:
    DATA_DIR = '/tmp/data'
    print("Running on Vercel, DATA_DIR is /tmp/data")
else:
    # Local development paths
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(CURRENT_DIR, '..', 'data')
    app.static_folder = os.path.join(CURRENT_DIR, '..', 'static')
    print(f"Running locally, DATA_DIR is {DATA_DIR}")
    print(f"Running locally, app.static_folder is {app.static_folder}")

GAME_HISTORY_FILE = os.path.join(DATA_DIR, 'game_history.json')

def initialize_history_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(GAME_HISTORY_FILE) or os.path.getsize(GAME_HISTORY_FILE) == 0:
        print(f"Initializing {GAME_HISTORY_FILE}...")
        with open(GAME_HISTORY_FILE, 'w') as f:
            json.dump([], f)
    else:
        try:
            with open(GAME_HISTORY_FILE, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("History file is not a list.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error in history file '{GAME_HISTORY_FILE}', re-initializing: {e}")
            with open(GAME_HISTORY_FILE, 'w') as f:
                json.dump([], f)

initialize_history_file()

if not IS_VERCEL:
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

def get_enhanced_next_prediction(game_specific_history, game_filter, last_n_games_count=20):
    default_prediction = 'player' if game_filter == 'baccarat' else 'dragon'
    primary_outcomes = ['player', 'banker'] if game_filter == 'baccarat' else ['dragon', 'tiger']

    if not game_specific_history:
        return default_prediction

    if len(game_specific_history) >= 3:
        last_three_winners = [g['winner'] for g in game_specific_history[-3:]]
        if (last_three_winners[0] == last_three_winners[2] and
            last_three_winners[0] != last_three_winners[1] and
            last_three_winners[0] in primary_outcomes and
            last_three_winners[1] in primary_outcomes):
            return last_three_winners[1]

    current_streak_winner_for_pred = None
    current_streak_count_for_pred = 0
    if game_specific_history:
        s_winner = game_specific_history[-1]['winner']
        if s_winner in primary_outcomes:
            current_streak_winner_for_pred = s_winner
            for g in reversed(game_specific_history):
                if g['winner'] == current_streak_winner_for_pred:
                    current_streak_count_for_pred += 1
                else:
                    break
            if current_streak_count_for_pred >= 2:
                return current_streak_winner_for_pred

    last_n_history = game_specific_history[-last_n_games_count:]
    if last_n_history:
        last_n_primary_winners = [g['winner'] for g in last_n_history if g['winner'] in primary_outcomes]
        if last_n_primary_winners:
            counts = Counter(last_n_primary_winners)
            max_count = 0
            tied_winners = []
            for outcome, count in counts.items():
                if count > max_count:
                    max_count = count
                    tied_winners = [outcome]
                elif count == max_count:
                    tied_winners.append(outcome)
            if len(tied_winners) == 1: return tied_winners[0]
            elif len(tied_winners) > 1:
                if default_prediction in tied_winners: return default_prediction
                return sorted(tied_winners)[0]

    overall_primary_winners = [g['winner'] for g in game_specific_history if g['winner'] in primary_outcomes]
    if overall_primary_winners:
        counts = Counter(overall_primary_winners)
        max_count = 0
        tied_winners = []
        for outcome, count in counts.items():
            if count > max_count:
                max_count = count
                tied_winners = [outcome]
            elif count == max_count:
                tied_winners.append(outcome)
        if len(tied_winners) == 1: return tied_winners[0]
        elif len(tied_winners) > 1:
            if default_prediction in tied_winners: return default_prediction
            return sorted(tied_winners)[0]
    return default_prediction

@app.route('/api/submit_result', methods=['POST'])
def submit_result():
    data = request.get_json()
    if not data: return jsonify({"error": "No data provided"}), 400
    game_type = data.get('game_type')
    winner = data.get('winner')
    if not game_type or not winner: return jsonify({"error": "Missing game_type or winner"}), 400

    try:
        initialize_history_file()
        history_before_this_round = []
        try:
            with open(GAME_HISTORY_FILE, 'r') as f: history_before_this_round = json.load(f)
            if not isinstance(history_before_this_round, list): history_before_this_round = []
        except (json.JSONDecodeError, FileNotFoundError): history_before_this_round = []

        game_specific_history_before_this_round = [
            game for game in history_before_this_round if game.get('game_type') == game_type
        ]
        predicted_winner = get_enhanced_next_prediction(game_specific_history_before_this_round, game_type)
        new_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(), "game_type": game_type,
            "winner": winner, "predicted_winner_for_this_round": predicted_winner
        }
        updated_full_history = history_before_this_round + [new_entry]
        with open(GAME_HISTORY_FILE, 'w') as f: json.dump(updated_full_history, f, indent=4)
        return jsonify({"message": "Result submitted successfully", "data_saved": new_entry}), 200
    except Exception as e:
        print(f"Error saving data to '{GAME_HISTORY_FILE}': {e}")
        return jsonify({"error": f"Failed to save result: {str(e)}"}), 500

def calculate_predictions(game_history, game_filter):
    filtered_games = [game for game in game_history if game and game.get('game_type') == game_filter]

    # Calculate next prediction based on the current full filtered_games history
    next_pred_winner = get_enhanced_next_prediction(filtered_games, game_filter)

    # Calculate Accuracy
    correct_predictions_count = 0
    total_predictions_accounted_for = 0
    for game in filtered_games:
        actual = game.get('winner')
        # Ensure 'predicted_winner_for_this_round' exists in the game entry
        predicted = game.get('predicted_winner_for_this_round')

        if actual is not None and predicted is not None:
            total_predictions_accounted_for += 1
            # Comparisons should be case-insensitive if winners/predictions might have varied casing
            # However, they are stored as lowercase, and default_prediction is now lowercase.
            if actual == predicted: # Assumes consistent casing (lowercase)
                correct_predictions_count += 1

    prediction_accuracy = 0.0 # Use float for accuracy
    if total_predictions_accounted_for > 0:
        prediction_accuracy = round((correct_predictions_count / total_predictions_accounted_for) * 100, 2)

    # Handle case where there are no games (or no games with predictions)
    if not filtered_games: # This check might be slightly redundant given the loop for accuracy
        return {
            "last_n_games": [], "percentages": {},
            "current_streak": {"winner": None, "count": 0}, "game_count": 0,
            "next_predicted_winner": next_pred_winner, # Still provide next prediction (default)
            "prediction_accuracy": 0.0,
            "total_predictions_made": 0
        }

    last_n_display = 5
    last_n_games_results = [{"winner": game.get('winner', 'N/A'), "timestamp": game.get('timestamp', 'N/A')} for game in filtered_games[-last_n_display:]]

    winners = [game['winner'] for game in filtered_games if 'winner' in game]
    game_count = len(winners)

    percentages = {}
    if game_count > 0:
        counts = Counter(winners)
        percentages = {winner: round((count / game_count) * 100, 2) for winner, count in counts.items()}

    current_streak_winner_val = None
    current_streak_count_val = 0
    if winners:
        current_streak_winner_val = winners[-1]
        for winner_val_loop in reversed(winners):
            if winner_val_loop == current_streak_winner_val:
                current_streak_count_val += 1
            else: break

    return {
        "last_n_games": last_n_games_results, "percentages": percentages,
        "current_streak": {"winner": current_streak_winner_val, "count": current_streak_count_val},
        "game_count": game_count, "next_predicted_winner": next_pred_winner,
        "prediction_accuracy": prediction_accuracy,
        "total_predictions_made": total_predictions_accounted_for
    }

@app.route('/api/get_predictions', methods=['GET'])
def get_predictions():
    try:
        initialize_history_file()
        game_history = []
        try:
            with open(GAME_HISTORY_FILE, 'r') as f: game_history = json.load(f)
            if not isinstance(game_history, list): game_history = []
        except (json.JSONDecodeError, FileNotFoundError): game_history = []

        baccarat_predictions = calculate_predictions(game_history, 'baccarat')
        dragon_tiger_predictions = calculate_predictions(game_history, 'dragon-tiger')
        return jsonify({
            "baccarat": baccarat_predictions, "dragon_tiger": dragon_tiger_predictions,
            "loaded_history_size": len(game_history)
        }), 200
    except Exception as e:
        print(f"Error in get_predictions from '{GAME_HISTORY_FILE}': {e}")
        return jsonify({"error": f"Failed to get predictions: {str(e)}"}), 500

@app.route('/api/reset_history', methods=['POST'])
def reset_history():
    try:
        initialize_history_file()
        with open(GAME_HISTORY_FILE, 'w') as f: json.dump([], f)
        print(f"Game history file '{GAME_HISTORY_FILE}' has been reset.")
        return jsonify({"message": "Game history reset successfully."}), 200
    except Exception as e:
        print(f"Error resetting history file '{GAME_HISTORY_FILE}': {e}")
        return jsonify({"error": f"Failed to reset game history: {str(e)}"}), 500

if __name__ == '__main__' and not IS_VERCEL:
    # print(f"Running locally, DATA_DIR is {DATA_DIR}") # Already printed at top
    # print(f"Running locally, app.static_folder is {app.static_folder}") # Already printed at top
    print(f"Starting Flask development server on port 5001...")
    app.run(debug=True, port=5001)
EOF
