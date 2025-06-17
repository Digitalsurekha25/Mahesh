from flask import Flask, request, jsonify, send_from_directory
import os
import json
from datetime import datetime, timezone
from collections import Counter

app = Flask(__name__) # Static folder handling is now conditional or by Vercel

# Determine data path based on environment
IS_VERCEL = os.environ.get('VERCEL') == '1'

if IS_VERCEL:
    DATA_DIR = '/tmp/data' # Vercel allows writing to /tmp
    # On Vercel, static files are served by Vercel's routing (vercel.json), not Flask.
    # Flask's app.static_folder is not needed for serving index.html via Flask.
    print("Running on Vercel, DATA_DIR is /tmp/data")
else:
    # Local development paths
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(CURRENT_DIR, '..', 'data')
    # For local dev, Flask needs to know where static files are to serve index.html
    app.static_folder = os.path.join(CURRENT_DIR, '..', 'static')
    print(f"Running locally, DATA_DIR is {DATA_DIR}")
    print(f"Running locally, app.static_folder is {app.static_folder}")


GAME_HISTORY_FILE = os.path.join(DATA_DIR, 'game_history.json')

def initialize_history_file():
    os.makedirs(DATA_DIR, exist_ok=True) # Ensure directory exists
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
            # print(f"{GAME_HISTORY_FILE} is valid.") # Optional: for verbose logging
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error in history file '{GAME_HISTORY_FILE}', re-initializing: {e}")
            with open(GAME_HISTORY_FILE, 'w') as f:
                json.dump([], f)

initialize_history_file() # Initialize on import/startup

# Serve index.html for local development only.
# On Vercel, static routing in vercel.json handles serving index.html from web_app/static.
if not IS_VERCEL:
    @app.route('/')
    def serve_index():
        print(f"Local: Serving index.html from {app.static_folder}")
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/submit_result', methods=['POST'])
def submit_result():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    game_type = data.get('game_type')
    winner = data.get('winner')

    if not game_type or not winner:
        return jsonify({"error": "Missing game_type or winner"}), 400

    new_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "game_type": game_type,
        "winner": winner
    }

    try:
        initialize_history_file()
        history = []
        with open(GAME_HISTORY_FILE, 'r') as f: # Read should be safe due to initialize
            history = json.load(f)

        history.append(new_entry)

        with open(GAME_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)

        return jsonify({"message": "Result submitted successfully", "data_saved": new_entry}), 200

    except Exception as e:
        print(f"Error saving data to '{GAME_HISTORY_FILE}': {e}")
        return jsonify({"error": f"Failed to save result: {str(e)}"}), 500

def calculate_predictions(game_history, game_filter):
    filtered_games = [game for game in game_history if game and game.get('game_type') == game_filter]

    if not filtered_games:
        return {
            "last_n_games": [],
            "percentages": {},
            "current_streak": {"winner": None, "count": 0},
            "game_count": 0
        }

    last_n = 5
    last_n_games_results = [{"winner": game.get('winner', 'N/A'), "timestamp": game.get('timestamp', 'N/A')} for game in filtered_games[-last_n:]]

    winners = [game['winner'] for game in filtered_games if 'winner' in game]
    total_games = len(winners)

    percentages = {}
    if total_games > 0:
        counts = Counter(winners)
        percentages = {winner: round((count / total_games) * 100, 2) for winner, count in counts.items()}

    current_streak_winner = None
    current_streak_count = 0
    if winners:
        current_streak_winner = winners[-1]
        current_streak_count = 0
        for winner_val in reversed(winners):
            if winner_val == current_streak_winner:
                current_streak_count += 1
            else:
                break

    return {
        "last_n_games": last_n_games_results,
        "percentages": percentages,
        "current_streak": {"winner": current_streak_winner, "count": current_streak_count},
        "game_count": len(filtered_games) # Use len(filtered_games) for consistency with initial check
    }

@app.route('/api/get_predictions', methods=['GET'])
def get_predictions():
    try:
        initialize_history_file()
        game_history = []
        if os.path.exists(GAME_HISTORY_FILE):
            with open(GAME_HISTORY_FILE, 'r') as f: # Read should be safe due to initialize
                game_history = json.load(f)

        baccarat_predictions = calculate_predictions(game_history, 'baccarat')
        dragon_tiger_predictions = calculate_predictions(game_history, 'dragon-tiger')

        return jsonify({
            "baccarat": baccarat_predictions,
            "dragon_tiger": dragon_tiger_predictions,
            "loaded_history_size": len(game_history)
        }), 200

    except Exception as e:
        print(f"Error in get_predictions from '{GAME_HISTORY_FILE}': {e}")
        return jsonify({"error": f"Failed to get predictions: {str(e)}"}), 500


@app.route("/api/reset_history", methods=["POST"])
def reset_history():
    try:
        initialize_history_file() # Ensure file/path integrity first
        # Reset the history by writing an empty list to the file
        with open(GAME_HISTORY_FILE, "w") as f:
            json.dump([], f)
        print(f"Game history file '{GAME_HISTORY_FILE}' has been reset.")
        return jsonify({"message": "Game history reset successfully."}), 200
    except Exception as e:
        print(f"Error resetting history file '{GAME_HISTORY_FILE}': {e}")
        return jsonify({"error": f"Failed to reset game history: {str(e)}"}), 500

# Local development server (Vercel uses its own WSGI entry point for the 'app' object)
if __name__ == '__main__' and not IS_VERCEL:
    print(f"Starting Flask development server on port 5001...")
    app.run(debug=True, port=5001)
