from flask import Flask, render_template, request, session, redirect, url_for, flash # Added redirect, url_for, flash
import json # For pretty printing in placeholders

app = Flask(__name__)
app.secret_key = 'super secret key' # Important for session management

# Import your existing analysis and prediction functions
# Assuming they are in roulette_analyzer/src/
import sys
sys.path.append('src') # Add src to path to find modules
# from input_handler import validate_and_parse_input # We'll need a web-specific parser
# For now, direct import from analysis_engine and prediction_engine, assuming they are in src
from analysis_engine import (
    calculate_frequencies, identify_trends, detect_patterns,
    detect_biases, analyze_wheel_clusters, WHEEL_ORDER, ROULETTE_WHEEL # Added ROULETTE_WHEEL
)
from prediction_engine import generate_predictions

def parse_web_input(input_string: str) -> tuple[list[int], list[str]]:
    """
    Parses a string of roulette numbers from web input.
    Accepts numbers separated by commas, spaces, or newlines.
    Validates numbers are integers between 0 and 36.

    Returns:
        A tuple containing:
        - list[int]: A list of valid integer numbers.
        - list[str]: A list of warning/error messages encountered during parsing.
    """
    if not input_string.strip():
        return [], ["Input was empty."]

    # Replace commas and newlines with spaces, then split by space
    processed_string = input_string.replace(',', ' ').replace('\n', ' ')
    raw_entries = processed_string.split(' ')

    valid_numbers = []
    messages = []

    for entry in raw_entries:
        entry = entry.strip()
        if not entry:  # Skip empty strings resulting from multiple spaces
            continue

        if entry.isdigit():
            try:
                num = int(entry)
                if 0 <= num <= 36:
                    valid_numbers.append(num)
                else:
                    messages.append(f"Ignored out-of-range value: '{entry}' (must be 0-36).")
            except ValueError:
                # This case should ideally not be reached if entry.isdigit() is true,
                # but kept for robustness.
                messages.append(f"Ignored non-integer value: '{entry}'.")
        else:
            messages.append(f"Ignored non-numeric value: '{entry}'.")

    if not valid_numbers and not messages: # e.g. input was just spaces
        messages.append("Input contained no processable numbers.")
    elif not valid_numbers and messages: # All inputs were invalid
        messages.insert(0,"No valid numbers found in input.")


    return valid_numbers, messages


@app.route('/')
def home():
    session.setdefault('roulette_numbers_history', [])
    history_display = ", ".join(map(str, session.get('roulette_numbers_history', [])[-50:]))
    # Get any messages flashed from previous redirects, if applicable
    parsing_messages = session.pop('parsing_messages', [])
    return render_template('index.html',
                           results_available=False,
                           numbers_history_display=history_display,
                           parsing_messages=parsing_messages,
                           color_map=ROULETTE_WHEEL) # Added color_map

@app.route('/analyze', methods=['POST'])
def analyze_results():
    user_input_string = request.form.get('roulette_numbers', '')

    numbers_from_input, parsing_messages = parse_web_input(user_input_string)

    current_history = session.get('roulette_numbers_history', [])

    if not numbers_from_input:
        # If no valid numbers were parsed, re-render home with messages
        # Store parsing messages in session to display after redirect or on current render
        # session['parsing_messages'] = parsing_messages # If redirecting
        history_display = ", ".join(map(str, current_history[-50:]))
        return render_template('index.html',
                               error_message="No valid numbers were processed from your input.",
                               parsing_messages=parsing_messages, # show why
                               results_available=False,
                               numbers_history_display=history_display,
                               color_map=ROULETTE_WHEEL) # Added color_map

    # Update session history
    current_history.extend(numbers_from_input)
    session['roulette_numbers_history'] = current_history
    session.modified = True

    updated_history_display = ", ".join(map(str, current_history[-50:]))

    # --- Call Analysis Functions ---
    analysis_results_dict = {}
    total_spins = len(current_history)
    general_error_message = None # For errors during analysis phase

    try:
        frequencies = calculate_frequencies(current_history)
        analysis_results_dict['frequencies'] = frequencies

        trends = identify_trends(frequencies, total_spins)
        analysis_results_dict['trends'] = trends

        patterns = detect_patterns(current_history, frequencies)
        analysis_results_dict['patterns'] = patterns

        number_deviations = trends.get('number_deviations', {})
        biases = detect_biases(frequencies, total_spins, number_deviations)
        analysis_results_dict['biases'] = biases

        clusters = analyze_wheel_clusters(frequencies, total_spins, WHEEL_ORDER)
        analysis_results_dict['clusters'] = clusters

        predictions_output = generate_predictions(analysis_results_dict, current_history)

    except Exception as e:
        print(f"Error during analysis: {str(e)}") # Log error
        general_error_message = "An unexpected error occurred during data analysis. Please try again."
        # Reset results if analysis failed mid-way
        analysis_results_dict = {}
        predictions_output = {}


    # Prepare success message, including count of numbers processed
    success_message = f"Successfully processed {len(numbers_from_input)} number(s) from your input."
    if general_error_message: # If analysis error, parsing messages might be less relevant than the analysis error
        parsing_messages = [general_error_message] # Prioritize general_error_message
        success_message = None # No success if analysis failed

    return render_template('index.html',
                            results_available=bool(analysis_results_dict and not general_error_message),
                            analysis=analysis_results_dict,
                            predictions=predictions_output,
                            numbers_history_display=updated_history_display,
                            parsing_messages=parsing_messages,
                            success_message=success_message,
                            error_message=general_error_message if general_error_message else None,
                            color_map=ROULETTE_WHEEL) # Added color_map

@app.route('/reset', methods=['POST'])
def reset_session():
    # Clear the specific session variable for roulette numbers history
    session.pop('roulette_numbers_history', None)
    # session['roulette_numbers_history'] = [] # Alternative
    # session.modified = True

    flash('Session cleared. You can start a new analysis with fresh numbers.', 'info')

    # Redirect back to the home page
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
