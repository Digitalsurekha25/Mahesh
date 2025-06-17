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
