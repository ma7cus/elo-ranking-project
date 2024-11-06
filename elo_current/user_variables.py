#File variables
DIRECTORY = r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Elo test"
INITIAL_CSV_FILE = 'top_100_clean.csv'#Initial file with items to be sorted

#Specify any colummns 
KEEP_COLUMNS = []  # Add the column names of any additional columns you want to keep here, or leave it empty for none

#Column titles according to their function
NAME_COLUMN = 'Name' #Name of the column with the names of items
RATING_COLUMN = 'Rating'  # Name of the column with initial ratings (if available)

ELO_COLUMN = 'Elo Score'
COMPARISONS_COLUMN = 'Comparisons'
RANK_COLUMN = 'Rank'
RANK_CHANGE_COLUMN = 'Rank Change'
ELO_CHANGE_COLUMN = 'Elo Change'

#Elo variables
K_FACTOR = 32  # The K-factor to control the magnitude of Elo change
STANDARD_ELO = 1000  # Standard starting Elo score for items with no initial rating



