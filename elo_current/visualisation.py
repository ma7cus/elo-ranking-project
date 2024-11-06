import matplotlib.pyplot as plt
from user_variables import NAME_COLUMN,ELO_COLUMN

def plot_elo_rankings(df, max_title_length=20):
    """
    Plots the Elo rankings of items in a horizontal bar chart.
    """
    print("Displaying Elo rankings plot: ")
    df = df.dropna(subset=[NAME_COLUMN])
    sorted_df = df.sort_values(by=ELO_COLUMN, ascending=False)
    titles = sorted_df[NAME_COLUMN].apply(lambda x: x if len(x) <= max_title_length else x[:max_title_length-3] + '...')
    plt.figure(figsize=(12, 12))
    plt.barh(titles, sorted_df[ELO_COLUMN], color='skyblue')
    plt.xlabel('Elo Score', fontsize=12)
    #plt.ylabel('', fontsize=10)
    plt.title('Elo Rankings Distribution', fontsize=14)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
