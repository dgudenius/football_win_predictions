from util import *
from Pythag_Win import *

# Read historical games from CSV
games = Util.read_games("data/nfl_games.csv")

# Forecast every game
Pythag_Win.pythag_win(games)

# Evaluate our forecasts against Elo
Util.evaluate_forecasts(games)


