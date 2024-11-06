from file_handling import load_or_initialise_data, save_to_csv
from elo_scores import calculate_rank_and_elo_changes
from popup_architecture import run_iterations
from visualisation import plot_elo_rankings
from user_variables import INITIAL_CSV_FILE, DIRECTORY, KEEP_COLUMNS
from state_manager import StateManager

import os

def main():
    # Step 1: Initialize StateManager with minimal setup (comparison count and stop flag)
    state_manager = StateManager()

    # Step 2: Load the latest CSV file or initialize a new DataFrame, and handle the expected score matrix
    df = load_or_initialise_data(DIRECTORY, state_manager, INITIAL_CSV_FILE)

    # Step 3: Make a copy of the DataFrame to keep the original as 'previous_df'
    previous_df = df.copy(deep=True)  # This captures the state before any comparisons
    
    # Step 4: Run item comparisons (using StateManager to manage state)
    df_new = run_iterations(df, state_manager)

    # Step 5: Calculate rank and Elo changes only after all comparisons are done
    df_new = calculate_rank_and_elo_changes(df_new, previous_df)

    # Step 6: Save the updated DataFrame and expected score matrix to CSV files
    save_to_csv(df_new, state_manager, DIRECTORY)
    
    # Step 7: Plot the Elo rankings of items
    plot_elo_rankings(df_new)

if __name__ == "__main__":
    main()

