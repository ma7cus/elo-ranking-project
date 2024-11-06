import numpy as np

class StateManager:
    """
    A class to manage the global state of the Elo comparison system.
    
    This class encapsulates two key state variables: 
    - `comparison_count`: Tracks how many comparisons have been made.
    - `stop_flag`: Controls when to stop the comparison loop.
    """
    def __init__(self):
        """
        Initializes the StateManager class.
        
        This constructor initializes two state variables:
        - `comparison_count` (int): Keeps track of the number of film comparisons made.
          Initialized to 0.
        - `stop_flag` (bool): A flag to indicate whether the comparison process should stop.
          Initialized to False, meaning the process will continue running until explicitly stopped.
        """
        self.comparison_count = 0
        self.stop_flag = False

        self.expected_score_matrix = None  # Initialise this later
    
    def set_expected_score_matrix(self, num_items):
        """
        Initializes the expected score matrix with default values once the number of items is known.
        :param num_items: Number of items (films) to initialize the matrix.
        """
        self.expected_score_matrix = np.full((num_items, num_items), 0.5)  # Set all expected scores to 0.5
    
    def load_expected_score_matrix(self, file_path):
        """
        Load the expected score matrix from a CSV file.
        """
        self.expected_score_matrix = np.loadtxt(file_path, delimiter=',')
    
    def save_expected_score_matrix(self, file_path):
        """
        Save the expected score matrix to a CSV file.
        """
        np.savetxt(file_path, self.expected_score_matrix, delimiter=',')

    def increment_comparison_count(self):
        """
        Increments the comparison count by 1.
        
        This method is called whenever a new comparison between two films is made. 
        It simply adds 1 to the `comparison_count` variable to keep track of the total number 
        of comparisons.
        """
        self.comparison_count += 1

    def stop(self):
        """
        Sets the stop flag to True.
        
        This method is called to stop the comparison process by setting the `stop_flag` to True. 
        When `stop_flag` is True, the comparison loop will break, ending the film comparison process.
        """
        self.stop_flag = True

    def is_stopped(self):
        """
        Returns the current state of the stop flag.
        
        This method checks whether the stop flag is True or False. It is used to determine 
        if the comparison process should continue running or if it should stop. If `is_stopped()` 
        returns True, the process should stop; if False, the process continues.
        
        :return: Boolean value indicating the state of `stop_flag`. 
                 True if the process is stopped, otherwise False.
        """
        return self.stop_flag
