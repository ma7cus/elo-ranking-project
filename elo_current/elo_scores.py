from user_variables import *
import pandas as pd

#########################################################################################################
# Elo Calculation Functions
#########################################################################################################

def expected_score(rating_1, rating_2):
    """
    Calculate expected score for two players based on their Elo ratings.
    """
    exp_score_1 = 1 / (1 + 10 ** ((rating_2 - rating_1) / 400))
    exp_score_2 = 1 / (1 + 10 ** ((rating_1 - rating_2) / 400))
    return exp_score_1, exp_score_2

def update_individual_elo(old_rating, expected_score, actual_score, k_factor=K_FACTOR):
    """
    Update Elo score based on the expected score and actual result.
    """
    return old_rating + k_factor * (actual_score - expected_score)

def calculate_rank_and_elo_changes(df, previous_df):
    """
    Compares the current and previous rankings to compute rank and Elo changes for each item.
    """
    # Initialise the new columns if required
    if previous_df is None:
        df[RANK_CHANGE_COLUMN] = '='
        df[ELO_CHANGE_COLUMN] = 0
        return df
    
    # Pull the old Elo scores and associated names in descending order by Elo score and rank them according to this score
    previous_ranks = previous_df[[NAME_COLUMN, ELO_COLUMN]].sort_values(by=ELO_COLUMN, ascending=False)  # Pulls the names and Elo scores in descending order
    previous_ranks[RANK_COLUMN] = range(1, len(previous_ranks) + 1)

    # Pull the new Elo scores and associated names in descending order by Elo score and rank them according to this score
    current_ranks = df[[NAME_COLUMN, ELO_COLUMN]].sort_values(by=ELO_COLUMN, ascending=False)
    current_ranks[RANK_COLUMN] = range(1, len(current_ranks) + 1)

    # Merges the two dataframes together by the names, adding new '_current' and '_previous' suffixes to the duplicated RANK_COLUMN and ELO_COLUMN columns
    merged_ranks = pd.merge(current_ranks, previous_ranks[[NAME_COLUMN, RANK_COLUMN, ELO_COLUMN]], on=NAME_COLUMN, suffixes=('_current', '_previous'))

    # Calculates the changes in the new merged dataframe
    merged_ranks[RANK_CHANGE_COLUMN] = merged_ranks[f'{RANK_COLUMN}_previous'] - merged_ranks[f'{RANK_COLUMN}_current']
    merged_ranks[ELO_CHANGE_COLUMN] = merged_ranks[f'{ELO_COLUMN}_current'] - merged_ranks[f'{ELO_COLUMN}_previous']

    # Drops the current rank and elo change columns from the current dataframe if they exist and appends the new ones merged from the merged dataframe 
    df = df.drop(columns=[RANK_CHANGE_COLUMN, ELO_CHANGE_COLUMN], errors='ignore')
    df = df.merge(merged_ranks[[NAME_COLUMN, RANK_CHANGE_COLUMN, ELO_CHANGE_COLUMN]], on=NAME_COLUMN, how='left')

    return df
