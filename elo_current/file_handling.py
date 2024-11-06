#########################################################################################################
# Input
#########################################################################################################
import os
import pandas as pd
import numpy as np
from user_variables import *
from elo_scores import expected_score

def scale_initial_rating(rating, min_rating, max_rating, min_elo=1000, max_elo=2000):
    return min_elo + (rating - min_rating) * (max_elo - min_elo) / (max_rating - min_rating)

def initialise_dataframe(file_name):
    print(f"Loading initial DataFrame from {file_name}...")
    df = pd.read_csv(file_name)
    if NAME_COLUMN not in df.columns:
        raise ValueError(f"DataFrame must contain a '{NAME_COLUMN}' column.")
    df = df.dropna(subset=[NAME_COLUMN])
    columns_to_keep = [NAME_COLUMN]
    if RATING_COLUMN in df.columns:
        columns_to_keep.append(RATING_COLUMN)
    for col in KEEP_COLUMNS:
        if col in df.columns:
            columns_to_keep.append(col)
    if ELO_COLUMN not in df.columns:
        if RATING_COLUMN in df.columns:
            min_rating = df[RATING_COLUMN].min()
            max_rating = df[RATING_COLUMN].max()
            df[ELO_COLUMN] = df[RATING_COLUMN].apply(lambda r: scale_initial_rating(r, min_rating, max_rating))
            print(f"Initial Elo scores scaled from {RATING_COLUMN} column.")
        else:
            df[ELO_COLUMN] = STANDARD_ELO
            print(f"No {RATING_COLUMN} column found. Assigned standard Elo score of {STANDARD_ELO}.")
    else:
        print(f"Elo column {ELO_COLUMN} already exists in the CSV, no recalculation necessary.")
    if COMPARISONS_COLUMN not in df.columns:
        df[COMPARISONS_COLUMN] = 0
        print(f"Comparisons column '{COMPARISONS_COLUMN}' added and initialised to 0.")
    else:
        print(f"Comparisons column '{COMPARISONS_COLUMN}' already exists, keeping existing values.")
    df = df[columns_to_keep + [ELO_COLUMN, COMPARISONS_COLUMN]]
    print(f"DataFrame initialised with {len(df)} entries and columns: {list(df.columns)}")
    return df

def initialise_or_load_expected_score_matrix(df, directory, state_manager):
    """
    Load the expected score matrix from the previous run if it exists; otherwise, create a new one based on Elo scores.
    """
    expected_matrix_file = os.path.join(directory, 'expected_score_matrix.csv')
    if os.path.exists(expected_matrix_file):
        print("Loading expected score matrix from previous run.")
        state_manager.load_expected_score_matrix(expected_matrix_file)
    else:
        # Failsafe: Create a new expected score matrix if it doesn't exist
        print(f"Expected score matrix not found. Creating a new one based on Elo scores.")
        calculate_expected_scores_from_elo(df, state_manager)

def calculate_expected_scores_from_elo(df, state_manager):
    """
    Calculate the expected score matrix based on current Elo scores and store it in state_manager.
    """
    num_films = len(df)
    state_manager.expected_score_matrix = np.zeros((num_films, num_films))
    for i, film_1_elo in df[ELO_COLUMN].items():
        for j, film_2_elo in df[ELO_COLUMN].items():
            if i != j:
                expected_film_1_vs_film_2, _ = expected_score(film_1_elo, film_2_elo)
                state_manager.expected_score_matrix[i, j] = expected_film_1_vs_film_2
                state_manager.expected_score_matrix[j, i] = 1 - expected_film_1_vs_film_2

def load_or_initialise_data(directory, state_manager, initial_csv_file):
    """
    Load the latest CSV with film scores or initialize a new DataFrame.
    """
    print("Loading latest CSV file...")
    csv_files = [f for f in os.listdir(directory) if f.startswith('film_scores_') and f.endswith('.csv')]
    if csv_files:
        comparison_counts = [int(f.split('_')[2].split('.')[0]) for f in csv_files]
        latest_file = f'film_scores_{max(comparison_counts)}.csv'
        state_manager.comparison_count = max(comparison_counts)
        df = pd.read_csv(os.path.join(directory, latest_file))
        print(f"Loaded {latest_file}.")
    else:
        print(f"No existing CSV files found. Initialising a new DataFrame from {initial_csv_file}.")
        df = initialise_dataframe(initial_csv_file)
    
    # Initialise or load the expected score matrix
    initialise_or_load_expected_score_matrix(df, directory, state_manager)
    
    return df

#########################################################################################################
# Output
#########################################################################################################
def save_to_csv(df, state_manager, directory):
    """
    Saves the film data to a CSV file, sorted by Elo score, and uses the comparison count from the StateManager.
    Also saves the expected score matrix to a separate CSV file in the same directory.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Sort the DataFrame by Elo score
    sorted_df = df.sort_values(by=ELO_COLUMN, ascending=False)
    
    # Round the Elo scores and Elo change to 2 decimal places
    sorted_df[ELO_COLUMN] = sorted_df[ELO_COLUMN].round(2)
    if ELO_CHANGE_COLUMN in sorted_df.columns:
        sorted_df[ELO_CHANGE_COLUMN] = sorted_df[ELO_CHANGE_COLUMN].round(2)
    
    # Get the comparison count from the StateManager
    comparison_count = state_manager.comparison_count
    
    # Create the file name with the comparison count
    file_name = f'film_scores_{comparison_count}.csv'
    matrix_file_name = 'expected_score_matrix.csv'  # Name for the matrix file
    
    # Full path for saving the film data and the matrix
    full_path = os.path.join(directory, file_name)
    matrix_full_path = os.path.join(directory, matrix_file_name)
    
    # Save the sorted DataFrame to the specified directory
    sorted_df.to_csv(full_path, index=False)
    
    # Save the expected score matrix as a CSV file
    np.savetxt(matrix_full_path, state_manager.expected_score_matrix, delimiter=',')
    
    # Increment the comparison count in the StateManager for the next save
    state_manager.comparison_count += 1
    
    # Print confirmation of saving
    print(f"Saved Elo rankings to {full_path}.")
    print(f"Saved expected score matrix to {matrix_full_path}.")
