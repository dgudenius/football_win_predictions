from util import *
from Pythag_Win import *
from Combined2 import *

# Read historical games from CSV
games = Util.read_games("data/nfl_games.csv")

# Forecast every game
Combined2.combined2(games)

# Evaluate our forecasts against Elo
Util.evaluate_forecasts(games)


