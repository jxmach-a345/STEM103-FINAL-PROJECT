# Robot Competition Game 
from important_one import *

# Run the intro sequence and get the player's robot name
player_name = intro_sequence()

# Initialize the player's robot using the name from the intro
player = initialize_player(player_name)

# Start the infinite‑day robot competition loop
run_game_loop(player)
