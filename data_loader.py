import json
import os


# This function reads and updates a player's game data stored in a file.

# Function to get the player's data from a file.
def get_player_data(path):
    # Check if a file exists at the given 'path'.
    if os.path.exists(path):
        # If the file exists, open it for reading ('r') and load the data from it.
        with open(path, 'r') as player_data:
            data = json.load(player_data)
    else:
        # If the file doesn't exist, create a default player data and save it to the file.
        data = {
            'level1': [0, 22],
            'level2': [0, 34],
            'level3': [0, 32]
        }
        with open(path, 'w') as player_data:
            json.dump(data, player_data)

    # Return the player's data, whether it was loaded from an existing file or created.
    return data


# Function to update the player's data when they achieve a high score.
def update_player_data(path, level, nb_coin):
    # Open the file for reading ('r') and load the player's data.
    with open(path, 'r') as player_data:
        data = json.load(player_data)

    # Create a key to identify the specific level data (e.g., 'level1', 'level2', 'level3').
    key = 'level' + str(level)

    # Retrieve the best number of coins achieved for the given level.
    best_nb_coin = data[key][0]

    # Check if the new number of coins is greater than the current best for that level.
    if nb_coin > best_nb_coin:
        # If it's a new high score, update the data and save it to the file.
        data[key][0] = nb_coin
        with open(path, 'w') as player_data:
            json.dump(data, player_data)
        # Return 'True' to indicate that the data was updated.
        return True
    else:
        # If the new score isn't higher, return 'False' to indicate no update was made.
        return False
