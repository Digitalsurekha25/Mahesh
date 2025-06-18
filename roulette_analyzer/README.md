# Roulette Analyzer

This project is a tool for analyzing roulette game data. It aims to provide insights into game patterns, potentially identify biases, and explore prediction strategies.

## Features

*   Manual data entry.
*   Statistical analysis of number frequencies, colors, even/odd, dozens, columns, etc.
*   Trend analysis to identify hot/cold numbers and categories.
*   Pattern detection for repeats, alternating colors, and consecutive dozens/columns.
*   Bias detection including a Chi-Squared test and sectional bias analysis.
*   Wheel cluster analysis to find hot/cold zones on the physical wheel.
*   Optional OCR for number input from screenshots (requires Tesseract installation).
*   Web interface for interactive analysis.
*   Predictions based on combined analysis results.

## Setup

### Python Dependencies

The core Python dependencies are listed in `requirements.txt`. You can install them using pip:

```bash
pip install -r requirements.txt
```
This includes Flask (for the web interface) and Pillow & pytesseract (for the optional OCR feature).

### Optional OCR Feature: Tesseract OCR Engine Installation

This tool includes an optional feature to upload screenshots of roulette results. The system will attempt to extract numbers from the image using Optical Character Recognition (OCR). For this feature to work, you need to have Google's Tesseract OCR engine installed on your system and accessible in your system's PATH.

*   **Debian/Ubuntu Linux:**
    ```bash
    sudo apt-get update
    sudo apt-get install tesseract-ocr
    ```
*   **macOS (using Homebrew):**
    ```bash
    brew install tesseract
    ```
*   **Windows:**
    1.  Download the installer from the [Tesseract at UB Mannheim GitHub page](https://github.com/UB-Mannheim/tesseract/wiki) (look for the latest stable version).
    2.  Run the installer. **Important:** During installation, make sure to check the option to add Tesseract to your system's PATH. You might also want to install additional language data if you need to recognize text in languages other than English (the default is English).

After installation, you might need to restart your terminal or system for the PATH changes to take effect. You can verify the installation by opening a new terminal/command prompt and typing `tesseract --version`.

## Running the Web Application

1.  Ensure all Python dependencies are installed (see Setup above).
2.  If using the OCR feature, ensure Tesseract is installed.
3.  Navigate to the `roulette_analyzer` root directory in your terminal.
4.  Run the Flask application:
    ```bash
    python app.py
    ```
5.  Open your web browser and go to `http://127.0.0.1:5000/`.

## Running Tests

To run the automated unit tests, navigate to the root directory of the project (`roulette_analyzer`) in your terminal and execute the following command:

```bash
python -m unittest discover tests
```

This will discover and run all test files located in the `tests` directory.

## Disclaimer

This tool is for educational and analytical purposes only. Roulette is a game of chance, and this tool does not guarantee any winnings or predict outcomes with certainty. Gamble responsibly.

## Deployment to Vercel & Data Persistence

This application is designed to be deployable on Vercel. However, there are important considerations regarding data persistence, particularly for the Machine Learning (ML) features:

*   **SQLite Database:** The application uses an SQLite database (`roulette_data.db`) located in the project's root directory. This database stores a persistent history of all roulette numbers submitted through the application. Its primary purpose is to accumulate data for training the ML prediction models (e.g., predicting the next dozen).

*   **ML Model Training (`/train_ml_models` route):** The ML models are trained using the data stored in `roulette_data.db`. When you trigger training, the application reads from this database.

*   **Vercel Serverless Environment:** When deployed to Vercel's serverless functions:
    *   The filesystem is generally ephemeral or read-only, especially on free/hobby tiers.
    *   Directly writing to or relying on a persistent SQLite file within the deployment bundle might not work as expected for continuous data accumulation. Data written to `roulette_data.db` during a function's execution may not persist across different invocations or after a redeployment.
    *   While the application might initialize the database if it's missing, any new data added via the web interface to the SQLite DB on Vercel is unlikely to be saved permanently in the serverless environment.

*   **Implications:**
    *   **ML Model Training on Vercel:** The `/train_ml_models` route will likely not be effective for *on-the-fly retraining with newly submitted data* in a standard Vercel serverless deployment due to the SQLite persistence issue.
    *   **Using Pre-trained Models:** The application is structured to save trained ML models as `.joblib` files in the `/models` directory. These files *can and should be bundled* with your Vercel deployment. The prediction engine will then load these pre-trained models, and predictions will work correctly.
    *   **Local Development & Initial Training:** It is recommended to run the training process (`python -m src.train_models` or via the web UI's training button) in your local development environment where SQLite can persist data correctly. Once models are trained and saved in the `/models` directory, they can be committed and deployed with the application.
    *   **Session Data:** The core roulette analysis features (frequencies, trends, patterns, etc.) that operate on numbers entered during the *current user session* (stored temporarily in the browser's session) will function correctly on Vercel.

*   **For Persistent Server-Side Data on Vercel:** If you require the ability to continuously accumulate training data and retrain models directly on Vercel, you would need to integrate a Vercel-compatible persistent storage solution, such as:
    *   Vercel KV
    *   Vercel Postgres
    *   An external cloud database service.
    This would involve modifying `roulette_analyzer/src/database_manager.py` to use the chosen service instead of SQLite for production deployments.

In summary, for Vercel deployment:
1.  Train your ML models in your local environment.
2.  Ensure the generated `.joblib` files in the `models/` directory are committed and deployed.
3.  The prediction features will use these bundled models.
4.  The core analysis of session data will work fine.
5.  Avoid relying on the `/train_ml_models` route to update models with new live data on Vercel unless you reconfigure data persistence.
