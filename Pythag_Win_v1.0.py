import csv
import math

past_games = 20     # Past Games to include in Pythagorean Win Projection (must be integer)
v_value = 1      # Rate at which previous seasons are discounted (not yet in use)
wf = 2.37       # Exponential for Pythagorean calcs, default for football is 2.37
HFA = 4.5      # home field advantage as percentage
#REVERT = 1/3.0 Between seasons, a team retains 2/3 of its previous season's rating

REVERSIONS = {'CBD1925': 1502.032, 'RAC1926': 1403.384, 'LOU1926': 1307.201, 'CIB1927': 1362.919, 'MNN1929': 1306.702, # Some between-season reversions of unknown origin
              'BFF1929': 1331.943, 'LAR1944': 1373.977, 'PHI1944': 1497.988, 'ARI1945': 1353.939, 'PIT1945': 1353.939, 'CLE1999': 1300.0}

class Pythag_Win:

    @staticmethod
    def pythag_win(games):
        """ Generates win probabilities in the my_prob1 field for each game based on Pythagorean Win Theorem model """

        # Initialize team objects to maintain ratings
        teams = {}
        for row in [item for item in csv.DictReader(open("data/initial_elos.csv"))]:
            teams[row['team']] = {
                'name': row['team'],
                'season': 'season',
                'Pwin': float(0.5),
                'Pfor': [],
                'Pagainst': []
            }

        for game in games:
            team1, team2 = teams[game['team1']], teams[game['team2']]

            # My difference needs to include home field advantage
            my_diff = (team1['Pwin']+ (0 if game['neutral'] == 1 else HFA/100)) - (team2['Pwin'])



            # This is the most important piece, where we set my_prob1 to our forecasted probability
            if game['elo_prob1'] != None:
                game['my_prob1'] = .5+my_diff

            # If game was played, maintain team Elo ratings
            if game['score1'] != None:

                # Margin of victory is used as a K multiplier
              #   pd = abs(game['score1'] - game['score2'])
              #  mult = math.log(max(pd, 1) + 1.0) * (2.2 / (1.0 if game['result1'] == 0.5 else ((my_diff if game['result1'] == 1.0 else -my_diff) * 0.001 + 2.2)))

                # Elo shift based on K and the margin of victory multiplier
               # Pwin = (K * mult) * (game['result1'] - game['my_prob1'])

                # Add Points to team arrays
                team1['Pfor'].append(game['score1'])
                team1['Pagainst'].append(game['score2'])
                team2['Pfor'].append(game['score2'])
                team2['Pagainst'].append(game['score1'])
              #  print (team1['Pfor'])
                # Sum team all time points
                team1['PforSum']=(sum(team1['Pfor']))
                team1['PagainstSum'] = (sum(team1['Pagainst']))
                team2['PforSum']=(sum(team2['Pfor']))
                team2['PagainstSum'] = (sum(team2['Pagainst']))



              #  team1['PforSquare']=team1['PforSum']**2.37
                if len(team1['Pfor']) <= past_games and (team1['PforSum'] or team1['PagainstSum']) != 0:
                   team1['Pwin'] = ((team1['PforSum'])**wf)/((sum(team1['Pfor']))**wf+(sum(team1['Pagainst']))**wf)
                elif len(team1['Pfor']) > past_games and (team1['PforSum'] or team1['PagainstSum']) !=0:
                    # Sum points for games in past_games range
                    team1['PforSumInRange'] = (sum(team1['Pfor'][len(team1['Pfor']) - past_games:]))
                    team1['PagainstSumInRange'] = (sum(team1['Pagainst'][len(team1['Pagainst']) - past_games:]))
                    team1['Pwin'] = team1['PforSumInRange']**wf/(((team1['PforSumInRange'])**wf)+((team1['PforSumInRange'])**wf))
                    #team1['Pwin'] = ((sum(team1['Pfor'][len(team1['Pfor'])-past_games:]))** wf)/(((sum(team1['Pfor'][len(team1['Pfor'])-past_games:]))**wf)+((sum(team1['Pagainst'][len(team1['Pagainst'])-past_games:]))**wf))
                    # print len(team1['Pfor'])
                else:
                   team1['Pwin'] = .5
                if len(team1['Pfor']) <= past_games and (team2['PforSum'] or team2['PagainstSum']) != 0:
                   team2['Pwin'] = ((sum(team2['Pfor']))**wf)/((sum(team2['Pfor']))**wf+(sum(team2['Pagainst']))**wf)
                elif len(team2['Pfor']) > past_games and (team2['PforSum'] or team2['PagainstSum']) != 0:
                    # Sum points for games in past_games range
                    team2['PforSumInRange'] = (sum(team2['Pfor'][len(team2['Pfor']) - past_games:]))
                    team2['PagainstSumInRange'] = (sum(team2['Pagainst'][len(team2['Pagainst']) - past_games:]))
                    #
                    team2['Pwin'] = ((sum(team2['Pfor'][len(team2['Pfor'])-past_games:]))**wf)/(((sum(team2['Pfor'][len(team2['Pfor'])-past_games:]))**wf)+((sum(team2['Pagainst'][len(team2['Pagainst'])-past_games:]))**wf))
                else:
                    team2['Pwin'] = .5
            # print team1['Pwin']
        print teams['CLE']
        print teams['PIT']
