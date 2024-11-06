import pandas as pd
import os
import numpy as np

# Define expected columns
EXPECTED_COLUMNS = {
    'Name': 'Name',  # Film name column
    'Elo Score': 'Elo Score',  # Elo score column
    'Number of comparisons': 'Number of comparisons',  # Comparisons column
}

# Default values for new columns
DEFAULT_ELO = 1500  # Default starting Elo score if missing
DEFAULT_COMPARISONS = 0  # Default number of comparisons if missing

# Paths and files
OLD_CSV_FILE = 'film_scores_768.csv'  # Path to the old file
UPDATED_CSV_FILE = 'updated_film_scores.csv'  # Output updated CSV file
EXPECTED_SCORE_MATRIX_FILE = 'expected_score_matrix.csv'  # Expected score matrix file

def load_and_update_old_csv(old_csv_file, expected_columns):
    """
    Loads the old CSV, updates missing columns, and saves it in a format compatible with the new script.
    """
    # Step 1: Load old CSV
    print(f"Loading old CSV file: {old_csv_file}")
    df = pd.read_csv(old_csv_file)

    # Step 2: Rename columns to match the expected names
    for old_col, new_col in expected_columns.items():
        if old_col in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)

    # Step 3: Add missing columns
    if 'Elo Score' not in df.columns:
        print(f"'Elo Score' column missing. Initializing all scores to {DEFAULT_ELO}.")
        df['Elo Score'] = DEFAULT_ELO
    if 'Number of comparisons' not in df.columns:
        print(f"'Number of comparisons' column missing. Initializing to {DEFAULT_COMPARISONS}.")
        df['Number of comparisons'] = DEFAULT_COMPARISONS

    # Step 4: Save updated CSV
    print(f"Saving updated CSV to {UPDATED_CSV_FILE}")
    df.to_csv(UPDATED_CSV_FILE, index=False)

    return df

def calculate_expected_scores(elo_scores):
    """
    Calculate the expected score matrix based on Elo scores.
    Uses the Elo formula for expected outcomes.
    """
    n = len(elo_scores)
    expected_scores = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                expected_scores[i, j] = 1 / (1 + 10 ** ((elo_scores[j] - elo_scores[i]) / 400))
    return expected_scores

def save_expected_scores(expected_scores, output_file):
    """Saves the expected scores matrix to a CSV file."""
    pd.DataFrame(expected_scores).to_csv(output_file, index=False)
    print(f"Expected score matrix saved to {output_file}.")

def main():
    # Step 1: Load and update the old CSV
    df = load_and_update_old_csv(OLD_CSV_FILE, EXPECTED_COLUMNS)

    # Step 2: Calculate expected score matrix if not available
    if not os.path.exists(EXPECTED_SCORE_MATRIX_FILE):
        print(f"No expected score matrix found. Calculating based on Elo scores.")
        elo_scores = df['Elo Score'].values
        expected_scores = calculate_expected_scores(elo_scores)
        save_expected_scores(expected_scores, EXPECTED_SCORE_MATRIX_FILE)

if __name__ == "__main__":
    main()
