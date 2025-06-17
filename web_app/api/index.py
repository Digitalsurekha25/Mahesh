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
            print(f"ERROR in initialize_history_file: Invalid content in '{GAME_HISTORY_FILE}', re-initializing: {e}")
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

    # Rule 1: Alternating Pattern (A-B-A -> predict B)
    if len(game_specific_history) >= 3:
        last_three_items = game_specific_history[-3:]
        # Ensure all items have 'winner'
        if all(isinstance(g, dict) and 'winner' in g for g in last_three_items):
            last_three_winners = [g['winner'] for g in last_three_items]
            if (last_three_winners[0] == last_three_winners[2] and
                last_three_winners[0] != last_three_winners[1] and
                last_three_winners[0] in primary_outcomes and
                last_three_winners[1] in primary_outcomes):
                return last_three_winners[1]

    # Rule 2: Streak Continuation (Current Streak of primary outcome >= 2)
    current_streak_winner_for_pred = None
    current_streak_count_for_pred = 0
    if game_specific_history: # Check if history is not empty
        last_game = game_specific_history[-1]
        s_winner = last_game.get('winner') if isinstance(last_game, dict) else None
        if s_winner and s_winner in primary_outcomes:
            current_streak_winner_for_pred = s_winner
            for g_entry in reversed(game_specific_history):
                g_winner = g_entry.get('winner') if isinstance(g_entry, dict) else None
                if g_winner == current_streak_winner_for_pred:
                    current_streak_count_for_pred += 1
                else:
                    break
            if current_streak_count_for_pred >= 2:
                return current_streak_winner_for_pred

    # Rule 3: Win Percentage from Last N Games (primary outcomes)
    last_n_history = game_specific_history[-last_n_games_count:]
    if last_n_history:
        last_n_winners = [g.get('winner') for g in last_n_history if isinstance(g, dict) and g.get('winner') in primary_outcomes]
        if last_n_winners:
            counts = Counter(last_n_winners)
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

    # Rule 4: Overall Win Percentage (primary outcomes)
    overall_winners = [g.get('winner') for g in game_specific_history if isinstance(g, dict) and g.get('winner') in primary_outcomes]
    if overall_winners:
        counts = Counter(overall_winners)
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
            game for game in history_before_this_round if isinstance(game, dict) and game.get('game_type') == game_type
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
        print(f"ERROR in submit_result: {str(e)}")
        return jsonify({"error": f"Failed to save result due to server issue: {str(e)}"}), 500

def calculate_predictions(game_history, game_filter):
    filtered_games = [game for game in game_history if isinstance(game, dict) and game.get('game_type') == game_filter]
    next_pred_winner = get_enhanced_next_prediction(filtered_games, game_filter)

    correct_predictions_count = 0
    total_predictions_accounted_for = 0
    for game in filtered_games: # game is already confirmed to be a dict from filtered_games
        actual = game.get('winner')
        predicted = game.get('predicted_winner_for_this_round')
        if actual is not None and predicted is not None: # Both must exist
            total_predictions_accounted_for += 1
            if actual.lower() == predicted.lower(): # Comparison is case-insensitive
                correct_predictions_count += 1

    prediction_accuracy = 0.0
    if total_predictions_accounted_for > 0:
        prediction_accuracy = round((correct_predictions_count / total_predictions_accounted_for) * 100, 2)

    if not filtered_games:
        return {
            "last_n_games": [], "percentages": {},
            "current_streak": {"winner": None, "count": 0}, "game_count": 0,
            "next_predicted_winner": next_pred_winner,
            "prediction_accuracy": 0.0,
            "total_predictions_made": 0
        }

    last_n_display = 5
    last_n_games_results = [{"winner": game.get('winner', 'N/A'), "timestamp": game.get('timestamp', 'N/A')} for game in filtered_games[-last_n_display:]]

    valid_winners = [g.get('winner') for g in filtered_games if g.get('winner') is not None]
    total_valid_games_for_percentage = len(valid_winners)
    percentages = {}
    if total_valid_games_for_percentage > 0:
        counts = Counter(valid_winners)
        percentages = {winner: round((count / total_valid_games_for_percentage) * 100, 2) for winner, count in counts.items()}

    current_streak_winner = None
    current_streak_count = 0
    if valid_winners:
        current_streak_winner = valid_winners[-1]
        for winner_val in reversed(valid_winners):
            if winner_val == current_streak_winner: current_streak_count += 1
            else: break

    return {
        "last_n_games": last_n_games_results, "percentages": percentages,
        "current_streak": {"winner": current_streak_winner, "count": current_streak_count},
        "game_count": len(filtered_games),
        "next_predicted_winner": next_pred_winner,
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
        print(f"ERROR in get_predictions: {str(e)}")
        return jsonify({"error": f"Failed to get predictions due to server issue: {str(e)}"}), 500

@app.route('/api/reset_history', methods=['POST'])
def reset_history():
    try:
        initialize_history_file()
        with open(GAME_HISTORY_FILE, 'w') as f: json.dump([], f)
        print(f"Game history file '{GAME_HISTORY_FILE}' has been reset.")
        return jsonify({"message": "Game history reset successfully."}), 200
    except Exception as e:
        print(f"ERROR in reset_history: {str(e)}")
        return jsonify({"error": f"Failed to reset game history: {str(e)}"}), 500

if __name__ == '__main__' and not IS_VERCEL:
    print(f"Starting Flask development server on port 5001...")
    app.run(debug=True, port=5001)
EOF
