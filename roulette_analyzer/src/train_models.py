import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier # Example model
# from sklearn.linear_model import LogisticRegression # Alternative
from sklearn.metrics import accuracy_score, classification_report

# Assuming database_manager and ml_utils are in the same 'src' package
try:
    from .database_manager import get_all_spins_for_training, get_total_spins_count # Added get_total_spins_count for example
    from .ml_utils import extract_sequences
except ImportError: # Handle running script directly for testing
    from database_manager import get_all_spins_for_training, get_total_spins_count, init_db, add_multiple_spin_results
    from ml_utils import extract_sequences

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models') # Place models dir in project root
MODEL_FILENAME_DOZEN = os.path.join(MODEL_DIR, 'predict_next_dozen_model.joblib')
FEATURE_WINDOW_SIZE = 5 # Number of past spins to consider for features

MIN_SAMPLES_FOR_TRAINING = 50 # Minimum number of sequences needed to attempt training

def get_dozen(number: int) -> int:
    """ Returns the dozen for a given roulette number (0 for 0, 1 for 1-12, etc.). """
    if not isinstance(number, int): # Basic type check
        # print(f"Warning: Invalid type for get_dozen: {number} (type: {type(number)})")
        return -1 # Or handle as a separate category, or raise error

    if number == 0:
        return 0 # Or a specific category for zero, e.g., 4, if preferred for modeling
    if 1 <= number <= 12:
        return 1
    elif 13 <= number <= 24:
        return 2
    elif 25 <= number <= 36:
        return 3
    return -1 # Should not happen for valid numbers 0-36 if logic is correct

def train_predict_next_dozen_model():
    print("Starting model training for predicting the next dozen...")

    if not os.path.exists(MODEL_DIR):
        print(f"Creating model directory: {MODEL_DIR}")
        os.makedirs(MODEL_DIR)

    # 1. Load data
    all_spins_data = get_all_spins_for_training() # Returns list of (number, timestamp_str)
    if not all_spins_data:
        print("No data available from database for training.")
        return False

    numbers_history = [spin[0] for spin in all_spins_data] # Extract just the numbers

    if len(numbers_history) < FEATURE_WINDOW_SIZE + 1:
        print(f"Not enough historical data (need at least {FEATURE_WINDOW_SIZE + 1} spins, got {len(numbers_history)}) to create sequences.")
        return False

    # 2. Feature Engineering
    print(f"Extracting sequences with window size {FEATURE_WINDOW_SIZE}...")
    X_sequences, y_next_numbers = extract_sequences(numbers_history, FEATURE_WINDOW_SIZE)

    if not X_sequences: # Check if extract_sequences returned empty (should be caught by len(numbers_history) check too)
        print("No sequences were extracted. Aborting training.")
        return False

    if len(X_sequences) < MIN_SAMPLES_FOR_TRAINING:
        print(f"Insufficient samples ({len(X_sequences)}) to train model. Need at least {MIN_SAMPLES_FOR_TRAINING} sequences.")
        return False

    # 3. Transform labels (y) to Dozens
    y_dozens = np.array([get_dozen(n) for n in y_next_numbers if get_dozen(n) != -1])
    # Filter X_features based on valid y_dozens (if any n in y_next_numbers was invalid for get_dozen)
    X_features = np.array([X_sequences[i] for i, n in enumerate(y_next_numbers) if get_dozen(n) != -1])

    if len(X_features) != len(y_dozens) or len(y_dozens) == 0:
        print("Mismatch in feature/label count after filtering invalid dozens, or no valid labels. Aborting.")
        return False

    unique_classes, counts = np.unique(y_dozens, return_counts=True)
    print(f"Unique dozen classes in labels: {unique_classes} with counts: {counts}")

    if len(unique_classes) < 2:
        print(f"Not enough class diversity in target labels (dozens). Found only {len(unique_classes)} unique class(es). Training aborted.")
        return False

    print(f"Generated {len(X_features)} feature sets and {len(y_dozens)} labels for dozens.")

    # 4. Split data
    stratify_option = y_dozens if len(unique_classes) > 1 and all(c >= 2 for c in counts) else None

    test_size = 0.25
    if len(X_features) * test_size < len(unique_classes) * 2 and stratify_option is not None: # Ensure test set can have at least 2 samples per class if stratifying
        print("Warning: Small dataset. Reducing test size or disabling stratification for robust splitting.")
        # Option: reduce test_size or disable stratification
        # For now, let proceed, split might warn/error if not possible.
        # A better approach might be to require more samples if stratification is desired.
        if len(X_features) < 20 : # Arbitrary small number where stratification becomes very hard
             stratify_option = None
             print("Disabling stratification due to very small dataset size.")


    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X_features, y_dozens, test_size=test_size, random_state=42, stratify=stratify_option
        )
    except ValueError as e:
        print(f"Could not stratify data (error: {e}), splitting without stratification.")
        X_train, X_test, y_train, y_test = train_test_split(
            X_features, y_dozens, test_size=test_size, random_state=42
        )

    print(f"Training with {len(X_train)} samples, testing with {len(X_test)} samples.")
    if len(X_train) == 0 or len(X_test) == 0:
        print("Training or testing set is empty. Aborting training.")
        return False

    # 5. Train Model
    print("Training RandomForestClassifier model for dozens...")
    model = RandomForestClassifier(n_estimators=50, random_state=42, class_weight='balanced', min_samples_leaf=2, oob_score=True)

    try:
        model.fit(X_train, y_train)
        print(f"Model OOB Score: {model.oob_score_:.4f}")
    except Exception as e:
        print(f"Error during model training: {e}")
        return False

    # 6. Evaluate Model
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy (Dozens): {accuracy:.4f}")
    print("Classification Report (Dozens):")
    # Ensure all unique classes present in y_dozens are used as labels if y_test/y_pred is sparse
    report_labels = sorted(unique_classes)
    print(classification_report(y_test, y_pred, labels=report_labels, zero_division=0))

    # 7. Save Model
    print(f"Saving dozen prediction model to {MODEL_FILENAME_DOZEN}...")
    joblib.dump(model, MODEL_FILENAME_DOZEN)
    print("Dozen prediction model training complete and model saved.")
    return True

if __name__ == '__main__':
    print("Running train_models.py directly...")
    # Initialize DB and add sample data if DB is empty or has too few records
    init_db()
    if get_total_spins_count() < MIN_SAMPLES_FOR_TRAINING + FEATURE_WINDOW_SIZE: # Ensure enough data to generate MIN_SAMPLES
        print(f"Database has less than {MIN_SAMPLES_FOR_TRAINING + FEATURE_WINDOW_SIZE} records. Populating with sample data...")
        # Generate diverse sample data to ensure multiple dozen outcomes
        sample_data = []
        for i in range(150): # Generate 150 random numbers
            sample_data.append(np.random.randint(0, 37))

        # Ensure all dozens are represented reasonably often as next numbers
        # This is a bit artificial but helps ensure model can train on all classes
        for _ in range(10): # Add sequences that ensure each dozen class appears as a label
            sample_data.extend([1,1,1,1,1, 5])  # Next is 5 (Dozen 1)
            sample_data.extend([2,2,2,2,2, 15]) # Next is 15 (Dozen 2)
            sample_data.extend([3,3,3,3,3, 28]) # Next is 28 (Dozen 3)
            sample_data.extend([4,4,4,4,4, 0])  # Next is 0 (Dozen 0)

        add_multiple_spin_results(sample_data)
        print(f"Added {len(sample_data)} sample records. New total: {get_total_spins_count()}")

    train_predict_next_dozen_model()
