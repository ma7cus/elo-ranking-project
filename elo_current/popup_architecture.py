import tkinter as tk
from tkinter import font as tkFont
import random
from elo_scores import *
from user_variables import *
from state_manager import StateManager

#########################################################################################################
# GUI wrapping handling
#########################################################################################################

def wrap_title(title, max_chars_per_line,separator = "-"):
    """
    Wraps item titles to ensure they don't exceed a maximum line length.
    """
    words = title.split(separator) #Splits the inputted title into words by the specified separator
    lines = []
    current_line = words[0] if words else "" #Sets up the current line with the first word if there is one

    for word in words[1:]: #Iterates through the words in the title
        if len(current_line) + len(word) + 1 > max_chars_per_line: #Checks if the current word would go over the character limit
            lines.append(current_line) #Saves the previous line
            current_line = word #Sets up the new line with the current word
        else:
            current_line += separator + word #Adds the current word to the current line if it fits

    if len(current_line) > 0:
        lines.append(current_line) #Appends the last line if it exists

    return "\n".join(lines)

def calculate_max_chars(width, tk_font):
    """
    Calculates the maximum number of characters per line based on width and font metrics.
    """
    char_width = tk_font.measure("A") #Pulls the width of a standard character in the given font
    return int(width * 0.8 / char_width) #Calculates the number of characters that will fit in 80% of the screen width

def calculate_button_height(wrapped_text, tk_font, padding=2):
    """
    Calculate the button height based on the number of lines in the wrapped text and font height,
    with additional padding added at the top and bottom.
    """
    num_lines = wrapped_text.count('\n') + 1  # Number of lines +1 for the last line (without \n)
    line_height = tk_font.metrics("linespace")  # Retrieves the height of a single line of text
    return (num_lines * line_height) + (padding * line_height)  # Calculates the space needed including padding space


def calculate_window_height(title_lines, button_heights, title_font, base_height=100, spacing_between_elements=10):
    """
    Calculates the required window height based on the number of lines in the titles and buttons,
    using actual font metrics for title height and explicitly adding space between elements.
    
    :param title_lines: Number of lines in the titles.
    :param button_heights: A list of heights for all buttons.
    :param title_font: The font used for the titles to calculate accurate title height.
    :param base_height: The base height for the window.
    :param spacing_between_elements: The vertical space between titles and buttons, and between buttons.
    :return: The calculated window height.
    """
    # Calculate the height of each title line using the actual line height from the font
    title_line_height = title_font.metrics("linespace")
    
    # Calculates the total title height
    total_title_height = title_lines * title_line_height

    # Calculates total button height 
    total_button_height = sum(button_heights)

    # Add vertical spacing between titles, buttons, and between individual buttons
    spacing_for_buttons = (len(button_heights) - 1) * spacing_between_elements
    
    # Return total window height
    return base_height + total_title_height + total_button_height + spacing_for_buttons

#########################################################################################################
# GUI functionality 
#########################################################################################################

def update_expected_scores_matrix(item_1_index, item_2_index, df, expected_score_matrix):
    """
    Updates the expected scores for two items (item_1 and item_2) with respect to all other items 
    in the dataset after their Elo ratings have been updated.
    
    :param item_1_index: Index of the first item in the DataFrame.
    :param item_2_index: Index of the second item in the DataFrame.
    :param df: The DataFrame containing the Elo ratings for all the items.
    :param expected_score_matrix: The matrix that stores the expected scores between all items, 
                                  which will be updated in this function.
    """
    # Retrieve the updated Elo ratings for both items after their latest comparison
    item_1_elo = df.at[item_1_index, ELO_COLUMN]
    item_2_elo = df.at[item_2_index, ELO_COLUMN]

    # Loop through all items in the dataset and update the expected scores for item_1 and item_2
    for other_item_index, other_item_elo in df[ELO_COLUMN].items():
        
        # Skip updating the score for item_1 against itself
        if other_item_index != item_1_index:
            # Calculate the expected score for item_1 vs another item
            expected_item_1_vs_other, _ = expected_score(item_1_elo, other_item_elo)
            
            # Update the expected score matrix for item_1 vs the other item
            expected_score_matrix[item_1_index, other_item_index] = expected_item_1_vs_other
            
            # Since the expected score is reciprocal, update the reverse (other item vs item_1)
            expected_score_matrix[other_item_index, item_1_index] = 1 - expected_item_1_vs_other

        # Skip updating the score for item_2 against itself
        if other_item_index != item_2_index:
            # Calculate the expected score for item_2 vs another item
            expected_item_2_vs_other, _ = expected_score(item_2_elo, other_item_elo)
            
            # Update the expected score matrix for item_2 vs the other item
            expected_score_matrix[item_2_index, other_item_index] = expected_item_2_vs_other
            
            # Since the expected score is reciprocal, update the reverse (other item vs item_2)
            expected_score_matrix[other_item_index, item_2_index] = 1 - expected_item_2_vs_other



def update_score(item_1_name, item_2_name, item_1_score, item_2_score, root, df, state_manager):
    """
    Updates Elo scores after a comparison and recalculates expected scores with all other items.
    """
    # Get the rows and their indices corresponding to both items using loc
    item_1_row = df.loc[df[NAME_COLUMN] == item_1_name].squeeze()
    item_2_row = df.loc[df[NAME_COLUMN] == item_2_name].squeeze()

    # Get the index of both items (the same loc call provides this)
    item_1_index = item_1_row.name  # This is the index of item_1_row
    item_2_index = item_2_row.name  # This is the index of item_2_row

    # Get the current Elo scores for both items
    item_1_elo = item_1_row[ELO_COLUMN]
    item_2_elo = item_2_row[ELO_COLUMN]

    # Retrieve the precomputed expected scores from the expected score matrix
    expected_item_1_score = state_manager.expected_score_matrix[item_1_index, item_2_index]
    expected_item_2_score = 1 - expected_item_1_score

    # Update Elo scores based on the actual scores (1, 0, or 0.5 for each item)
    new_item_1_elo = update_individual_elo(item_1_elo, expected_item_1_score, item_1_score)
    new_item_2_elo = update_individual_elo(item_2_elo, expected_item_2_score, item_2_score)

    # Calculate and store Elo change
    item_1_elo_change = new_item_1_elo - item_1_elo
    item_2_elo_change = new_item_2_elo - item_2_elo

    # Update the Elo change in the DataFrame
    df.loc[item_1_index, 'Elo Change'] = item_1_elo_change
    df.loc[item_2_index, 'Elo Change'] = item_2_elo_change

    # Update the new Elo scores in the DataFrame
    df.loc[item_1_index, ELO_COLUMN] = new_item_1_elo
    df.loc[item_2_index, ELO_COLUMN] = new_item_2_elo

    # Update the comparison count for both items
    df.loc[item_1_index, COMPARISONS_COLUMN] += 1
    df.loc[item_2_index, COMPARISONS_COLUMN] += 1

    # Update the expected scores matrix for both items using the actual matrix from StateManager
    update_expected_scores_matrix(item_1_index, item_2_index, df, state_manager.expected_score_matrix)

    # Simplified print statement
    print(f"{item_1_name}: ({'+' if item_1_elo_change >= 0 else ''}{item_1_elo_change:.2f}), {item_2_name}: ({'+' if item_2_elo_change >= 0 else ''}{item_2_elo_change:.2f})")

    # Close the Tkinter popup
    root.destroy()



# Function to stop the comparison iterations
def quit_iterations(root, state_manager):
    """
    Sets the stop flag to True and closes the Tkinter window, ending the comparison loop.
    """
    state_manager.stop()
    root.destroy()


def create_popup(item_1, item_2, df, state_manager, window_width=700, title_font_size=14, button_font_size=12, button_width=300):
    """
    Creates a Tkinter GUI for comparing two items and allowing the user to select a winner.
    """
    root = tk.Tk()

    # Font definition (type and size)
    title_font = tkFont.Font(family="Arial", size=title_font_size)
    button_font = tkFont.Font(family="Arial", size=button_font_size)

    # Calculate number of characters that will fit into the window and the button width
    max_chars_per_line_window = calculate_max_chars(window_width, title_font)
    max_chars_per_line_button = calculate_max_chars(button_width, button_font)

    # Generate strings split into lines according to the number of characters calculated
    wrapped_title1_window = wrap_title(item_1, max_chars_per_line_window)
    wrapped_title2_window = wrap_title(item_2, max_chars_per_line_window)

    wrapped_title1_button = wrap_title(f"{item_1} Wins", max_chars_per_line_button)
    wrapped_title2_button = wrap_title(f"{item_2} Wins", max_chars_per_line_button)

    # Calculate button heights based on the strings generated
    button1_height = calculate_button_height(wrapped_title1_button, button_font)
    button2_height = calculate_button_height(wrapped_title2_button, button_font)

    # Calculate window height based on the title strings and button heights
    title_lines = wrapped_title1_window.count('\n') + wrapped_title2_window.count('\n') + 2 #Calculates the number of lines in the title with padding
    window_height = calculate_window_height(title_lines, [button1_height, button2_height, 40, 40], title_font) #Calculates the window height

    # Get screen dimensions and calculate respective window position
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    top_left_x = int((screen_width / 2) - (window_width / 2)) #Finds the top left x position as half the window up from the vertical middle of the screen
    top_left_y = int((screen_height / 2) - (window_height / 2)) #Finds the the top left y position as half the window left of the horizontal middle of the screen

    # Set window size and position
    root.geometry(f"{window_width}x{window_height}+{top_left_x}+{top_left_y}")

    # Set up a grid layout for the window
    root.grid_columnconfigure(0, weight=1)
    for i in range(6):
        root.grid_rowconfigure(i, weight=1)

    # Add in title 1
    label1 = tk.Label(root, text=f"Item 1: {wrapped_title1_window}", font=title_font, wraplength=window_width * 0.8, anchor="center")
    label1.grid(row=0, column=0, pady=10, sticky="n")

    # Add in title 2
    label2 = tk.Label(root, text=f"Item 2: {wrapped_title2_window}", font=title_font, wraplength=window_width * 0.8, anchor="center")
    label2.grid(row=1, column=0, pady=10, sticky="n")

    # Add in item 1 button
    button1 = tk.Button(root, text=wrapped_title1_button, font=button_font, width=int(button_width / button_font_size), height=int(button1_height / 20), 
                        command=lambda: update_score(item_1, item_2, 1, 0, root, df, state_manager))
    button1.grid(row=2, column=0, pady=10, sticky="n")

    #Add in item 2 button
    button2 = tk.Button(root, text=wrapped_title2_button, font=button_font, width=int(button_width / button_font_size), height=int(button2_height / 20), 
                        command=lambda: update_score(item_2, item_1, 0, 1, root, df,state_manager))
    button2.grid(row=3, column=0, pady=10, sticky="n")

    #Add in draw button
    button_draw = tk.Button(root, text="Draw", font=button_font, width=int(button_width / button_font_size), height=2, 
                            command=lambda: update_score(item_1, item_2, 0.5, 0.5, root, df,state_manager))
    button_draw.grid(row=4, column=0, pady=10, sticky="n")

    #Add in quit button
    button_quit = tk.Button(root, text="Quit", font=button_font, width=int(button_width / button_font_size), height=2, 
                            command=lambda: quit_iterations(root, state_manager))
    button_quit.grid(row=5, column=0, pady=10, sticky="n")

    root.mainloop()

def generate_random_pairs(df):
    """
    Generates a list of random pairs from the DataFrame where each item is compared at least once.
    
    :param df: DataFrame containing the item data.
    :return: A list of (item_1, item_2) pairs for comparison.
    """
    items = df[NAME_COLUMN].tolist()
    random.shuffle(items)

    # Create random pairs by shuffling the list and grouping into pairs
    pairs = [(items[i], items[i + 1]) for i in range(0, len(items) - 1, 2)]
    
    # If there's an odd number of items, pair the last item with a random one
    if len(items) % 2 == 1:
        pairs.append((items[-1], random.choice(items[:-1])))

    return pairs

def select_closest_pairs(df, state_manager, batch_size=10):
    """
    Selects the batch_size closest pairs of items for comparison based on the expected score matrix.
    Finds the batch_size pairs with expected scores closest to 0.5.
    
    :param df: DataFrame containing the item data.
    :param state_manager: Instance of StateManager, containing the expected score matrix.
    :param batch_size: The number of pairs to return in the batch for random sampling (default is 10).
    :return: List of (item_1, item_2) pairs for comparison.
    """
    expected_scores = state_manager.expected_score_matrix
    differences = []

    # Iterate over the matrix and calculate the difference from 0.5
    for i in range(len(expected_scores)):
        for j in range(i + 1, len(expected_scores)):  # Only check the upper triangular part of the matrix
            expected_score = expected_scores[i, j]
            diff_from_0_5 = abs(expected_score - 0.5)
            differences.append((diff_from_0_5, i, j))
    
    # Sort all pairs by their difference from 0.5 (smallest differences first)
    differences.sort()

    # Get the top batch_size closest pairs
    closest_pairs = differences[:batch_size]

    # Retrieve the item names using the DataFrame index for the closest pairs
    item_pairs = [(df.iloc[pair[1]][NAME_COLUMN], df.iloc[pair[2]][NAME_COLUMN]) for pair in closest_pairs]

    return item_pairs

def run_iterations(df, state_manager, batch_size=10, n=2):
    """
    Runs the item comparison process in two phases:
    1. Random Swiss-like pairings until every item has been compared 'n' times.
    2. Intelligent batch pairings based on expected scores once the first phase is complete.
    
    :param df: DataFrame containing the item data.
    :param state_manager: Instance of StateManager, managing the expected score matrix and state.
    :param batch_size: Size of the batch for intelligent pairing.
    :param n: The minimum number of comparisons each item must undergo in the initial phase.
    """
    # Take a snapshot of the current DataFrame to track Elo and rank changes
    previous_df = df.copy()

    print("Starting item comparisons...")

    # Phase 1: Swiss-like random pairings to ensure each item is compared at least 'n' times
    while df[COMPARISONS_COLUMN].min() < n:
        item_pairs = generate_random_pairs(df)

        for item_1, item_2 in item_pairs:
            if state_manager.is_stopped():
                break

            # Show the comparison popup
            create_popup(item_1, item_2, df, state_manager)

            # Update the comparison count for both items
            df.loc[df[NAME_COLUMN] == item_1, COMPARISONS_COLUMN] += 1
            df.loc[df[NAME_COLUMN] == item_2, COMPARISONS_COLUMN] += 1

            state_manager.increment_comparison_count()

    print(f"Phase 1 complete: Each item has been compared at least {n} times.")

    # Phase 2: Intelligent pairings based on the expected score matrix
    while not state_manager.is_stopped():
        # Preselect the batch of item pairs based on the current expected scores
        item_pairs = select_closest_pairs(df, state_manager, batch_size=batch_size)

        for item_1, item_2 in item_pairs:
            if state_manager.is_stopped():
                break

            # Show the comparison popup
            create_popup(item_1, item_2, df, state_manager)

            # Increment the comparison count after each comparison
            state_manager.increment_comparison_count()

    print("Item comparisons completed.")

    # Call the function to calculate the rank and Elo changes based on the previous_df
    df = calculate_rank_and_elo_changes(df, previous_df)

    return df





