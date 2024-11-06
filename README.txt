# Elo-Based Ranking System

## Overview

This project is an Elo-based system designed to compare and rank any set of items. The system uses a combination of a random initial pairing strategy followed by a smarter pairing mechanism based on Elo ratings to refine rankings over time. The project supports dynamically adding new items, continuing previously saved rankings, and visualising results.

The goal is to create an evolving ranking of items based on user comparisons, where each item's ranking reflects its relative quality compared to others in the set. The Elo system provides a way to effectively quantify and update these rankings based on a series of pairwise comparisons.

### Versions Available

- **Current Version (Recommended)**: This version uses a combination of random initial pairing and a smart pairing mechanism based on Elo scores to produce more meaningful rankings over time. This version is designed to be flexible and can rank any type of item.
- **Old Version**: The previous version, available in the `elo_old` directory, uses only random pairing throughout the entire process. This version is simpler and should work fine, but the newer version is designed to smooth the results more quickly by making better use of competitive matchups.

The following documentation is focused on the current version.

## Workflow Summary

The system has a two-phase approach:
1. **Initial Random Pairing Phase**: Items are initially paired randomly to ensure unbiased comparisons, allowing Elo scores to stabilise before transitioning to the next phase.
2. **Smart Pairing Phase**: Once each item reaches a threshold number of comparisons, the system transitions to a smarter pairing mechanism, selecting items with similar Elo scores to produce more competitive matchups. The **expected score matrix** is generated if it does not already exist, storing the expected scores for each possible pair of items. After each comparison, this matrix is updated to ensure future matchups use the latest information.

This two-phase system ensures that the ratings are not skewed by early biases and become more accurate as more data is collected.

## Files and Structure

### `elo_scores.py`
Manages the calculation and updating of Elo ratings and expected scores between items.

- **Key Functions**:
  - `expected_score(elo_A, elo_B)`: Calculates the expected outcome for two items given their Elo scores.
  - `update_individual_elo(current_elo, expected_score, actual_score)`: Updates the Elo score of an item after a comparison.
  - `update_expected_scores_matrix(item_1_index, item_2_index, df, expected_score_matrix)`: Updates the expected score matrix to reflect new Elo scores.
  - `update_score(item_1_name, item_2_name, item_1_score, item_2_score, root, df, state_manager)`: Updates all relevant data after a comparison.

### `file_handling.py`
Handles loading and saving of data to ensure persistence between runs.

- **Key Functions**:
  - `load_initial_data()`: Loads the initial CSV file containing the items and sets up default columns if not present.
  - `save_data(df)`: Saves the updated item data to the CSV file.

### `main.py`
Serves as the main control script for running comparisons and managing transitions between phases.

- **Key Functions**:
  - `select_random_pair(df)`: Selects two items randomly for comparison during the initial phase.
  - `select_smart_pair(df, expected_score_matrix)`: Selects two items for comparison using an Elo-based approach once the initial threshold is met.
  - `run_comparisons(df, state_manager)`: Handles the comparison process, managing the transition between phases.

### `popup_architecture.py`
Implements the GUI for user interaction during comparisons.

- **Key Functions**:
  - `create_popup(item_1, item_2, df, state_manager)`: Creates a popup window for comparing two items, allowing the user to select a winner or indicate a draw.
  - `update_score()`: Updates ratings after user interaction in the popup window.

### `state_manager.py`
Manages the state of the comparison process, such as the expected score matrix and stopping conditions.

- **Key Functions**:
  - `__init__()`: Initialises the expected score matrix and other state-tracking attributes.
  - `stop()` and `should_stop()`: Manages stopping conditions for the comparison loop.

### `update_script.py`
Handles updates and integrity checks for the expected score matrix.

- **Key Functions**:
  - `main()`: Verifies the existence and consistency of the expected score matrix, recalculating if necessary to align with current Elo ratings.

### `user_variables.py`
Stores user-defined variables and settings.

- **Key Variables**:
  - `STANDARD_ELO`: Default starting Elo score for new items.
  - `K_FACTOR`: Controls the magnitude of Elo changes.
  - `DIRECTORY` and `INITIAL_CSV_FILE`: Paths and filenames for data storage.
  - `INITIAL_COMPARISONS_THRESHOLD`: The number of initial comparisons each item must undergo before switching to the smart pairing phase.
  - `BATCH_SIZE`: The number of pairs to be selected in each batch during the smart pairing phase.

### `visualisation.py`
Generates visualisations of item rankings.

- **Key Functions**:
  - `plot_elo_rankings(df)`: Displays a bar chart of items sorted by Elo scores.

## How It Works

### Initial Random Pairing Phase
Items are initially paired randomly to ensure unbiased comparisons. The system uses `select_random_pair()` to randomly pick pairs until each item has reached a specified number of comparisons, as defined by `INITIAL_COMPARISONS_THRESHOLD` in `user_variables.py`.

### Smart Pairing Phase
Once each item reaches the comparison threshold, the system switches to a smarter pairing mechanism (`select_smart_pair()`). In this phase, pairs of items are selected based on the **proximity of their expected scores to 0.5**, which means the items are closely matched and likely to result in competitive comparisons. The system pulls **batches of pairs** of a user-defined size (`BATCH_SIZE`), selecting the top pairs that are closest to an expected score of 0.5. This recursive batch selection ensures that items are compared in meaningful ways that refine the rankings over time. The **expected score matrix** is used as a lookup table for these scores and is updated dynamically to reflect changes after each comparison.

### Adding Items Midway
To add a new item, update the CSV file. New items are assigned the `STANDARD_ELO` score and start with random comparisons until they meet the threshold, after which they enter the smarter pairing phase.

## Setup Instructions

1. **Environment Setup**:
   - Install Python 3.x and the required packages.
   - Make sure all scripts are placed in the same directory or adjust paths accordingly in `user_variables.py`.

2. **File Configuration**:
   - Update `user_variables.py` with the correct path for `INITIAL_CSV_FILE`. The file should include at least a `Name` column for the items.

3. **Running the Program**:
   - To start the comparison process, run `main.py`. Initially, items will be compared randomly to establish Elo ratings, then transition to the smarter comparison mechanism based on `INITIAL_COMPARISONS_THRESHOLD` and `BATCH_SIZE`.

4. **Visualisation**:
   - To see the current rankings, run `visualisation.py`, which will display a bar chart showing Elo scores of the items.

## Dependencies
The required dependencies are listed in the `requirements.txt` file. To install them, run:
```sh
pip install -r requirements.txt
```
This will install all necessary Python packages, including `pandas`, `matplotlib`, and `tkinter`.

## Important Notes

- **K-Factor**: The `K_FACTOR` controls how much Elo ratings change after each comparison. A higher value means faster adjustments but more volatility.
- **Threshold Management**: The number of initial comparisons (`INITIAL_COMPARISONS_THRESHOLD`) before switching to the smart pairing phase can be adjusted in `user_variables.py`.
- **Batch Size**: The number of pairs (`BATCH_SIZE`) selected for smart comparisons in each batch can also be adjusted in `user_variables.py`.
- **Expected Score Matrix**: Managed by `state_manager`, this matrix keeps track of expected outcomes and recalculates when necessary to maintain consistency.

## Potential Issues

- **Scaling**: The expected score matrix scales quadratically, which can cause high memory usage with a large number of items.
- **Adding Items**: When adding items, ensure that the expected score matrix is updated to include them properly. The `update_script.py` helps manage this process.
- **Incomplete Comparisons**: Make sure that items receive enough initial random comparisons to avoid bias during the smart pairing phase.

## Conclusion
This project is a robust solution for ranking any set of items using Elo ratings. It balances unbiased early comparisons with a refined matching mechanism as data is collected, ensuring accurate and meaningful rankings. Follow the setup instructions, and pay attention to configuration files like `user_variables.py` for the best experience.

For further customization, feel free to modify the scripts to better fit your dataset and use case.
  
The older version is available in the `elo_old/` directory for reference. This version is simpler, using only random pairing, and should work fine but may not smooth the rankings as effectively as the newer version with smart pairing.

