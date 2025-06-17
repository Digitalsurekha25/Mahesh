from flask import Flask, render_template, request, session, redirect, url_for, flash
import json # For pretty printing in placeholders
import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image

app = Flask(__name__)
app.secret_key = 'super secret key' # Important for session management

# Configure Upload Folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Import your existing analysis and prediction functions
# Assuming they are in roulette_analyzer/src/
import sys
sys.path.append('src') # Add src to path to find modules
# from input_handler import validate_and_parse_input # We'll need a web-specific parser
# For now, direct import from analysis_engine and prediction_engine, assuming they are in src
from analysis_engine import (
    calculate_frequencies, identify_trends, detect_patterns,
    detect_biases, analyze_wheel_clusters, WHEEL_ORDER, ROULETTE_WHEEL
)
from prediction_engine import generate_predictions
from src.database_manager import init_db, add_multiple_spin_results, get_total_spins_count # DB functions
from src.train_models import train_predict_next_dozen_model # For triggering training

# Initialize DB (creates table if it doesn't exist)
init_db()

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


# Helper function to parse numbers from OCR text
def parse_numbers_from_ocr_text(text: str) -> str:
    # This is a very basic parser. It will need significant improvement
    # based on typical OCR output for roulette screenshots.
    # It looks for sequences of digits, possibly separated by common delimiters.
    import re
    # Remove anything that's not a digit or a common delimiter (space, comma, newline, semicolon)
    # This is a very naive first pass.
    cleaned_text = re.sub(r'[^0-9\s,;\n]', '', text)
    # Find sequences of 1 or 2 digits. Using \b for word boundaries might be too restrictive if numbers are close.
    # Instead, split by common delimiters then validate.
    potential_numbers = re.split(r'[\s,;\n]+', cleaned_text)

    valid_roulette_numbers = []
    for num_str in potential_numbers:
        if num_str.isdigit(): # Check if it's purely digits after split
            try:
                num = int(num_str)
                if 0 <= num <= 36:
                    valid_roulette_numbers.append(str(num))
            except ValueError:
                continue

    return ", ".join(valid_roulette_numbers) # Return as a comma-separated string


@app.route('/ocr_upload', methods=['POST'])
def ocr_upload_route():
    # flash("Debug: Testing flash message directly from ocr_upload_route.", "debug") # DEBUG FLASH - REMOVING THIS FOR ACTUAL TEST
    if 'screenshot_image' not in request.files:
        flash('No image file selected for upload.', 'error')
        return redirect(url_for('home'))

    file = request.files['screenshot_image']
    if file.filename == '':
        flash('No image file selected for upload.', 'error')
        return redirect(url_for('home'))

    if file: # Basic check if file exists
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath) # File is saved, but not processed by PIL for these tests

            file.save(filepath)

            # OCR Processing
            img = Image.open(filepath) # Restored
            img = img.convert('L') # Convert to grayscale # Restored

            # --- OCR-dependent part ---
            try:
                ocr_text = pytesseract.image_to_string(img) # Restored
                extracted_numbers_str = parse_numbers_from_ocr_text(ocr_text)

                if extracted_numbers_str:
                    flash(f"Numbers extracted via OCR. Please review and click 'Analyze Results' if correct. Extracted: {extracted_numbers_str}", 'info')
                    session['ocr_extracted_numbers'] = extracted_numbers_str
                else:
                    flash("OCR did not find any recognizable roulette numbers (0-36) in the image. Please try manual input or a clearer image.", 'warning')
                    session.pop('ocr_extracted_numbers', None)

            except pytesseract.TesseractNotFoundError: # Restored this specific exception
                flash("OCR Error: Tesseract OCR engine is not installed or not found in PATH. Please install Tesseract to use this feature (see README for details).", 'error')
                session.pop('ocr_extracted_numbers', None)
            except Exception as e_ocr:
                flash(f"An error occurred during OCR processing: {str(e_ocr)}", 'error') # General OCR error
                session.pop('ocr_extracted_numbers', None)
            # --- End of OCR-dependent part ---

        except Exception as e_file: # For file saving or Image.open errors
            flash(f"An error occurred processing the image file: {str(e_file)}", 'error')
            session.pop('ocr_extracted_numbers', None)
        finally:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e_remove:
                    print(f"Error removing uploaded file {filepath}: {e_remove}") # Log this error
    else:
        flash('Invalid file or file type for upload.', 'error') # Should be caught by browser accept ideally

    return redirect(url_for('home'))


@app.route('/')
def home():
    session.setdefault('roulette_numbers_history', [])
    history_display = ", ".join(map(str, session.get('roulette_numbers_history', [])[-50:]))

    # Get OCR extracted numbers if available and then clear from session
    ocr_prefill_numbers = session.pop('ocr_extracted_numbers', '') # Pop to use it once

    # Get any flashed parsing messages (e.g. from previous direct POST to /analyze if it were to redirect)
    # Note: flash messages are typically handled by get_flashed_messages in template directly.
    # This specific session.pop for 'parsing_messages' was from an earlier design idea.
    # For OCR prefill, 'ocr_prefill_numbers' is now the primary mechanism.
    # Parsing messages from manual input are handled within the /analyze POST itself.
    # Flashed messages from /ocr_upload will be handled by Jinja's get_flashed_messages.
    total_db_spins = get_total_spins_count()

    return render_template('index.html',
                           results_available=False,
                           numbers_history_display=history_display,
                           color_map=ROULETTE_WHEEL,
                           ocr_prefill_numbers=ocr_prefill_numbers,
                           total_db_spins=total_db_spins) # Pass this to template

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
                               color_map=ROULETTE_WHEEL,
                               total_db_spins=get_total_spins_count()) # Added color_map and total_db_spins

    # Add valid numbers from this input to the persistent database
    if numbers_from_input:
        add_multiple_spin_results(numbers_from_input)

    # Update session history
    current_history.extend(numbers_from_input)
    session['roulette_numbers_history'] = current_history # current_history now includes numbers_from_input
    session.modified = True

    updated_history_display = ", ".join(map(str, current_history[-50:])) # Display last 50 from session

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
                            color_map=ROULETTE_WHEEL,
                            total_db_spins=get_total_spins_count()) # Added color_map and total_db_spins

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


@app.route('/train_ml_models', methods=['POST'])
def trigger_model_training_route():
    flash("AI/ML model training started. This might take a few moments...", "info")

    try:
        # For now, only the dozen model training is called.
        # This function is expected to print its own logs to the console.
        # It returns True on success, False on failure/issues.
        if train_predict_next_dozen_model():
            flash("AI/ML Training Process (Next Dozen Model) Completed. Check server logs for details of accuracy and other metrics.", "success")
        else:
            flash("AI/ML Training Process (Next Dozen Model) may have encountered issues, had insufficient data, or the model performance was very low. Check server logs.", "warning")

        # TODO: When other models (column, section, number) are created, add their training calls here:
        # if train_predict_next_column_model():
        #     flash("Column Model training completed.", "success")
        # else:
        #     flash("Column Model training failed or had issues.", "warning")
        # ... and so on for other models.

    except Exception as e:
        flash(f"An unexpected error occurred during the training process trigger: {str(e)}", "error")
        print(f"Error during trigger_model_training_route: {e}") # Log to server console

    return redirect(url_for('home'))
