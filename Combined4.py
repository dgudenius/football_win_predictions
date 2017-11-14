import csv
import math

past_games = 17          # Past Games to include in Pythagorean Win Projection (must be integer greater than 3) (~18 ?)
v_value = 4.1            # Rate at which previous seasons are discounted (~4 seems good)
wf = 1.39                # Exponential for Pythagorean calcs, default for football is 2.37(?) (must be a float) (~1.39 seems good)
HFA = 7.2                # home field advantage as percentage, default is 5.5 (~7.4 seems good)
HFA2 = HFA               # home field advantage for win chart
HFAE = 65.0              # elo hfa points
HFA_P_M = 1.59           # multiplier for home field advantage in playoffs (~1.6 seems good)
HFAP = HFA*HFA_P_M       # Pythag Win home field advantage for playoffs
HFA2P = HFA2*HFA_P_M     # win chart hfa for playoffs
HFAEP = HFAE*HFA_P_M     # elo hfa for playoffs
team_below_min = 32.25   # Expected win percentage by teams that have played 1 game (must be float) (32.25 seems good)
new_team = 27.5          # Expected win percentage by team in first game (must be float) (27.5 seems good)
a_factor = 2.45          # Exponential factor to compare Expected Wins Head to Head (2.465 seems good)
expect_points = 42.5     # Expected total points for calculating point differential (45.4 was 2016 league average points/game)
percent_mine = 40.0      # % using Pwin instead of Elo (must be float) (~40 seems good)
percent_win_chart = 3.25  # % using expected win chart (must be float) (~3.25 seems good)
b_factor = 0.9          # Exponential factor to compare Win Chart values Head to Head (0.9 seems good)
K = 20.7
REVERT = 1/2.97
y_factor  = 1.3          # Multiplier for points expectations (try 1.9?)
x_factor  = 1.2          # Root for points expectations (try 1.4?), this and the y_factor are used in compressing/expanding score predictions
backup_qb_loss = 2.3     # Expected point loss if backup QB is starting
backup_qb_percent = backup_qb_loss/(expect_points)

REVERSIONS = {'CBD1925': 1502.032, 'RAC1926': 1403.384, 'LOU1926': 1307.201, 'CIB1927': 1362.919, 'MNN1929': 1306.702, # Some between-season reversions of unknown origin
              'BFF1929': 1331.943, 'LAR1944': 1373.977, 'PHI1944': 1497.988, 'ARI1945': 1353.939, 'PIT1945': 1353.939, 'CLE1999': 1300.0}


class Combined4:

    @staticmethod
    def combined4(games):
        """ Generates win probabilities in the my_prob1 field for each game based on Pythagorean Win Theorem model """

        # Initialize team objects(?)
        teams = {}
        for row in [item for item in csv.DictReader(open("data/initial_elos.csv"))]:
            teams[row['team']] = {
                'name': row['team'],
                'season': 'season',
                'Pwin': float(new_team/100),
                'Pfor': [],
                'Pagainst': [],
                'elo': float(row['elo']),
                'Wfor' : [],
                'WforSum' : 0,
                'WinTable' : .5
            }

        for game in games:
            team1, team2 = teams[game['team1']], teams[game['team2']]

            # Revert teams at the start of seasons
            for team in [team1, team2]:
                if team['season'] and game['season'] != team['season']:
                    team['Wfor'] = []
                    # Revert Pythag Win points
                    team['Pfor'][:] = [n / v_value for n in team['Pfor']]
                    team['Pagainst'][:] = [n / v_value for n in team['Pagainst']]
                    k = "%s%s" % (team['name'], game['season'])
                    if k in REVERSIONS:
                        team['elo'] = REVERSIONS[k]
                    else:
                        team['elo'] = 1505.0 * REVERT + team['elo'] * (1 - REVERT)
                team['season'] = game['season']


            # My difference includes home field advantage
            my_diff = (team1['Pwin']+(0 if game['neutral'] == 1 else HFA/100)) - (team2['Pwin'])

            elo_diff = team1['elo'] - team2['elo'] + (0 if game['neutral'] == 1 else HFAE)

            # This is the most important piece, where we set my_prob1 to our forecasted probability
            if game['elo_prob1'] != None:
             #    game['my_prob1'] = .5+my_diff
                if game['playoff'] == 1:
                 elo_diff = team1['elo'] - team2['elo'] + (0 if game['neutral'] == 1 else HFAEP)
                 game['my_prob1'] = (team1['Pwin']+(HFAP/100))**a_factor/((team1['Pwin']+(HFAP/100))**a_factor+team2['Pwin']**a_factor)
                 game['my_prob2'] = 1.0 / (math.pow(10.0, (-elo_diff / 400.0)) + 1.0)
                 game['my_prob3'] = (((team1['WinTable']+(HFA2P/100))**b_factor)/(((team1['WinTable']+(HFA2P/100))**b_factor)+(team2['WinTable']**b_factor)))
                 game['my_prob1'] = (percent_mine/100)*game['my_prob1']+((percent_win_chart/100)*game['my_prob3'])+((1-((percent_mine/100)+(percent_win_chart/100)))*game['my_prob2'])
                 game['point_diff'] = round((expect_points * game['my_prob1']) - (expect_points / 2), 1)
                 game['point_diff2'] = round((y_factor * (abs(((expect_points * game['my_prob1']) - (expect_points / 2))))) ** ( 1 / x_factor), 1)
                else:
                 game['my_prob1'] = (team1['Pwin']+(0 if game['neutral'] == 1 else HFA/100))**a_factor/((team1['Pwin']+(0 if game['neutral'] == 1 else HFA/100))**a_factor+team2['Pwin']**a_factor)
                 game['my_prob2'] = 1.0 / (math.pow(10.0, (-elo_diff / 400.0)) + 1.0)
                 game['my_prob3'] = (((team1['WinTable']+(HFA2/100))**b_factor)/(((team1['WinTable']+(HFA2/100))**b_factor)+(team2['WinTable']**b_factor)))
                 game['my_prob1'] = (percent_mine/100)*game['my_prob1']+((percent_win_chart/100)*game['my_prob3'])+((1-((percent_mine/100)+(percent_win_chart/100)))*game['my_prob2'])
                 game['my_prob_qb1_out'] = game['my_prob1']-backup_qb_percent
                 game['my_prob_qb2_out'] = game['my_prob1']+backup_qb_percent
                 game['point_diff'] = ((expect_points * game['my_prob1']) - (expect_points / 2))
                 #game['point_diff2'] = round(((y_factor * (abs(((expect_points * game['my_prob1']) - (expect_points / 2))))) ** ( 1 / x_factor))*2,0)/2
                 game['point_diff2'] = (y_factor * (abs(((expect_points * game['my_prob1']) - (expect_points / 2))))) ** (1 / x_factor)
                 game['point_diff_qb1_out'] = round((y_factor * (abs(((expect_points * game['my_prob_qb1_out']) - (expect_points / 2))))) ** ( 1 / x_factor),1)
                 game['point_diff_qb2_out'] = round((y_factor * (abs(((expect_points * game['my_prob_qb2_out']) - (expect_points / 2))))) ** (1 / x_factor),1)
                 if game['point_diff'] < 0:
                    game['point_diff2'] = -game['point_diff2']
                    if game['my_prob_qb1_out'] < .5:
                       game['point_diff_qb1_out'] = -game['point_diff_qb1_out']
                    if game['my_prob_qb2_out'] < .5:
                       game['point_diff_qb2_out'] = -game['point_diff_qb2_out']

            # If game was played, maintain team Elo ratings
            if game['score1'] != None:

              #   Margin of victory is used as a K multiplier
                pd = abs(game['score1'] - game['score2'])
                mult = math.log(max(pd, 1) + 1.0) * (2.2 / (1.0 if game['result1'] == 0.5 else ((my_diff if game['result1'] == 1.0 else -my_diff) * 0.001 + 2.2)))

              # Elo shift based on K and the margin of victory multiplier
                shift = (K * mult) * (game['result1'] - game['my_prob1'])

              #  Elo shift based on K and the margin of victory multiplier
                Pwin = (K * mult) * (game['result1'] - game['my_prob1'])
              # Apply shift
                team1['elo'] += shift
                team2['elo'] -= shift


            # Add Points to team arrays
                team1['Pfor'].append(game['score1'])
                team1['Pagainst'].append(game['score2'])
                team2['Pfor'].append(game['score2'])
                team2['Pagainst'].append(game['score1'])

            # Add Wins to team arrays
                team1['Wfor'].append(game['result1'])
                team2['Wfor'].append(1-game['result1'])

            # Sum team all time points
                team1['PforSum']=(sum(team1['Pfor']))
                team1['PagainstSum'] = (sum(team1['Pagainst']))
                team2['PforSum']=(sum(team2['Pfor']))
                team2['PagainstSum'] = (sum(team2['Pagainst']))


                if len(team1['Pfor']) <= past_games and (team1['PforSum'] or team1['PagainstSum']) != 0:
                   team1['Pwin'] = ((team1['PforSum'])**wf)/((sum(team1['Pfor']))**wf+(sum(team1['Pagainst']))**wf)
                elif len(team1['Pfor']) > past_games and (team1['PforSum'] or team1['PagainstSum']) !=0:
                  #  print len(team1['Pfor'])
                    # Sum points for games in past_games range
                    team1['PforSumInRange'] = (sum(team1['Pfor'][len(team1['Pfor']) - past_games:]))
                    team1['PagainstSumInRange'] = (sum(team1['Pagainst'][len(team1['Pagainst']) - past_games:]))
                    team1['Pwin'] = (team1['PforSumInRange']**wf)/(((team1['PforSumInRange'])**wf)+((team1['PagainstSumInRange'])**wf))
                    #team1['Pwin'] = ((sum(team1['Pfor'][len(team1['Pfor'])-past_games:]))** wf)/(((sum(team1['Pfor'][len(team1['Pfor'])-past_games:]))**wf)+((sum(team1['Pagainst'][len(team1['Pagainst'])-past_games:]))**wf))
                    # print len(team1['Pfor'])
                else:
                   team1['Pwin'] = team_below_min/100
                if len(team1['Pfor']) <= past_games and (team2['PforSum'] or team2['PagainstSum']) != 0:
                   team2['Pwin'] = ((sum(team2['Pfor']))**wf)/(((sum(team2['Pfor']))**wf)+(sum(team2['Pagainst']))**wf)
                elif len(team2['Pfor']) > past_games and (team2['PforSum'] or team2['PagainstSum']) != 0:
                    # Sum points for games in past_games range
                    team2['PforSumInRange'] = (sum(team2['Pfor'][len(team2['Pfor']) - past_games:]))
                    team2['PagainstSumInRange'] = (sum(team2['Pagainst'][len(team2['Pagainst']) - past_games:]))
                    #
                    team2['Pwin'] = ((sum(team2['Pfor'][len(team2['Pfor'])-past_games:]))**wf)/(((sum(team2['Pfor'][len(team2['Pfor'])-past_games:]))**wf)+((sum(team2['Pagainst'][len(team2['Pagainst'])-past_games:]))**wf))
                else:
                    team2['Pwin'] = team_below_min/100

                # Check number of games played, find record, disregard playoffs
                if game['playoff'] == 1:
                    team1['WinTable'] = 0.0
                else:
                    team1['WforSum'] = sum(team1['Wfor'])
                    team1['LforSum'] = round(len(team1['Wfor'])-sum(team1['Wfor']),0)
                    team1['Games_played'] = len(team1['Wfor'])
                if game['playoff'] == 1:
                    team2['WinTable'] = 0.0
                else:
                    team2['WforSum'] = sum(team2['Wfor'])
                    team2['LforSum'] = round(len(team2['Wfor']) - sum(team2['Wfor']), 0)
                    team2['Games_played'] = len(team2['Wfor'])
               # print(team1['WforSum'])

                # Values for each possible record
                if   team1['Games_played']==0:
                     team1['WinTable'] = 0.5
                elif team1['Games_played'] == 1:
                    if  team1['WforSum'] == 1:
                        team1['WinTable'] = 0.54
                    else:
                        team1['WinTable'] = 0.46
                elif team1['Games_played'] == 2:
                    if  team1['WforSum'] == 2:
                        team1['WinTable'] = .564286
                    elif team1['WforSum'] == 1:
                        team1['WinTable'] = 0.514286
                    else:
                        team1['WinTable'] = 0.407143
                elif team1['Games_played'] == 3:
                    if  team1['WforSum'] == 3:
                        team1['WinTable'] = .592308
                    elif  team1['WforSum'] == 2:
                        team1['WinTable'] = .538462
                    elif team1['WforSum'] == 1:
                        team1['WinTable'] = 0.476923
                    else:
                        team1['WinTable'] = 0.376923
                elif team1['Games_played'] == 4:
                    if  team1['WforSum'] == 4:
                        team1['WinTable'] = .600833
                    elif team1['WforSum'] == 3:
                        team1['WinTable'] = .566667
                    elif  team1['WforSum'] == 2:
                        team1['WinTable'] = .508333
                    elif team1['WforSum'] == 1:
                        team1['WinTable'] = 0.433333
                    else:
                        team1['WinTable'] = 0.366667
                elif team1['Games_played'] == 5:
                    if  team1['WforSum'] == 5:
                        team1['WinTable'] = .645455
                    elif team1['WforSum'] == 4:
                        team1['WinTable'] = .6
                    elif team1['WforSum'] == 3:
                        team1['WinTable'] = .527273
                    elif  team1['WforSum'] == 2:
                        team1['WinTable'] = .463636
                    elif team1['WforSum'] == 1:
                        team1['WinTable'] = 0.409091
                    else:
                        team1['WinTable'] = 0.363636
                elif team1['Games_played'] == 6:
                    if  team1['WforSum'] == 6:
                        team1['WinTable'] = .66
                    elif team1['WforSum'] == 5:
                        team1['WinTable'] = .6
                    elif team1['WforSum'] == 4:
                        team1['WinTable'] = .55
                    elif team1['WforSum'] == 3:
                        team1['WinTable'] = .52
                    elif  team1['WforSum'] == 2:
                        team1['WinTable'] = .42
                    elif team1['WforSum'] == 1:
                        team1['WinTable'] = 0.39
                    else:
                        team1['WinTable'] = 0.32
                elif team1['Games_played'] == 7:
                    if  team1['WforSum'] == 7:
                        team1['WinTable'] = .688889
                    elif team1['WforSum'] == 6:
                        team1['WinTable'] = .63333
                    elif team1['WforSum'] == 5:
                        team1['WinTable'] = .577778
                    elif team1['WforSum'] == 4:
                        team1['WinTable'] = .522222
                    elif team1['WforSum'] == 3:
                        team1['WinTable'] = .477778
                    elif  team1['WforSum'] == 2:
                        team1['WinTable'] = .4
                    elif team1['WforSum'] == 1:
                        team1['WinTable'] = 0.38889
                    else:
                        team1['WinTable'] = 0.32222
                elif team1['Games_played'] == 8:
                    if team1['WforSum'] == 8.0:
                        team1['WinTable'] = .675
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .675
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .6
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .5875
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .4875
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .4375
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .3625
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .35
                    else:
                        team1['WinTable'] = .3125
                elif team1['Games_played'] == 9:
                    if team1['WforSum'] == 9.0:
                        team1['WinTable'] = .642857
                    elif team1['Wfor'] == 8.0:
                         team1['WinTable'] = .7
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .628571
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .6
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .557143
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .442857
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .414286
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .357142
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .314286
                    else:
                        team1['WinTable'] = .242857
                elif team1['Games_played'] == 10:
                    if team1['WforSum'] == 10.0:
                        team1['WinTable'] = .666667
                    elif team1['Wfor'] == 9.0:
                         team1['WinTable'] = .65
                    elif team1['Wfor'] == 8.0:
                         team1['WinTable'] = .65
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .616667
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .566667
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .516667
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .433333
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .4
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .3
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .3
                    else:
                        team1['WinTable'] = .283333
                elif team1['Games_played'] == 11:
                    if team1['WforSum'] == 11.0:
                        team1['WinTable'] = .68
                    elif team1['Wfor'] == 10.0:
                         team1['WinTable'] = .62
                    elif team1['Wfor'] == 9.0:
                         team1['WinTable'] = .7
                    elif team1['Wfor'] == 8.0:
                         team1['WinTable'] = .62
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .58
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .54
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .46
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .44
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .4
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .3
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .3
                    else:
                        team1['WinTable'] = .283333
                elif team1['Games_played'] == 12:
                    if team1['WforSum'] == 12.0:
                        team1['WinTable'] = .6
                    elif team1['Wfor'] == 11.0:
                         team1['WinTable'] = .575
                    elif team1['Wfor'] == 10.0:
                         team1['WinTable'] = .7
                    elif team1['Wfor'] == 9.0:
                         team1['WinTable'] = .65
                    elif team1['Wfor'] == 8.0:
                         team1['WinTable'] = .575
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .55
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .55
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .45
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .4
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .35
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .3
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .325
                    else:
                        team1['WinTable'] = .3
                elif team1['Games_played'] == 13:
                    if team1['WforSum'] == 13.0:
                        team1['WinTable'] = .466667
                    elif team1['Wfor'] == 12.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 11.0:
                         team1['WinTable'] = .633333
                    elif team1['Wfor'] == 10.0:
                         team1['WinTable'] = .666667
                    elif team1['Wfor'] == 9.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 8.0:
                         team1['WinTable'] = .566667
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .5
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .5
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .466667
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .333333
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .333333
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .333333
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .2
                    else:
                        team1['WinTable'] = .333333
                elif team1['Games_played'] == 14:
                    if team1['WforSum'] == 14.0:
                        team1['WinTable'] = .5
                    elif team1['Wfor'] == 13.0:
                         team1['WinTable'] = .55
                    elif team1['Wfor'] == 12.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 11.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 10.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 9.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 8.0:
                         team1['WinTable'] = .55
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .5
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .5
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .45
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .3
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .4
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .25
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .2
                    else:
                        team1['WinTable'] = 0.0
                elif team1['Games_played'] == 15:
                    if team1['WforSum'] == 15.0:
                        team1['WinTable'] = 1
                    elif team1['Wfor'] == 14.0:
                         team1['WinTable'] = .8
                    elif team1['Wfor'] == 13.0:
                         team1['WinTable'] = .4
                    elif team1['Wfor'] == 12.0:
                         team1['WinTable'] = .7
                    elif team1['Wfor'] == 11.0:
                         team1['WinTable'] = .7
                    elif team1['Wfor'] == 10.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 9.0:
                         team1['WinTable'] = .6
                    elif team1['Wfor'] == 8.0:
                         team1['WinTable'] = .5
                    elif team1['Wfor'] == 7.0:
                         team1['WinTable'] = .5
                    elif team1['WforSum'] == 6.0:
                         team1['WinTable'] = .4
                    elif team1['WforSum'] == 5.0:
                         team1['WinTable'] = .4
                    elif team1['WforSum'] == 4.0:
                         team1['WinforSum'] = .2
                    elif team1['WforSum'] == 3.0:
                         team1['WinTable'] = .4
                    elif team1['WforSum'] == 2.0:
                         team1['WinTable'] = .1
                    elif team1['WforSum'] == 1.0:
                         team1['WinTable'] = .2
                    else:
                        team1['WinTable'] = 0.0


                # Values for Team 2
                if   team2['Games_played']== 0:
                     team2['WinTable'] = 0.5
                elif team2['Games_played'] == 1:
                    if  team2['WforSum'] == 1:
                        team2['WinTable'] = 0.54
                    else:
                        team2['WinTable'] = 0.46
                elif team2['Games_played'] == 2:
                    if  team2['WforSum'] == 2:
                        team2['WinTable'] = .564286
                    elif team2['WforSum'] == 1:
                        team2['WinTable'] = 0.514286
                    else:
                        team2['WinTable'] = 0.407143
                elif team2['Games_played'] == 3:
                    if  team2['WforSum'] == 3:
                        team2['WinTable'] = .592308
                    elif  team2['WforSum'] == 2:
                        team2['WinTable'] = .538462
                    elif team2['WforSum'] == 1:
                        team2['WinTable'] = 0.476923
                    else:
                        team2['WinTable'] = 0.376923
                elif team2['Games_played'] == 4:
                    if  team2['WforSum'] == 4:
                        team2['WinTable'] = .600833
                    elif team2['WforSum'] == 3:
                        team2['WinTable'] = .566667
                    elif  team2['WforSum'] == 2:
                        team2['WinTable'] = .508333
                    elif team2['WforSum'] == 1:
                        team2['WinTable'] = 0.433333
                    else:
                        team2['WinTable'] = 0.366667
                elif team2['Games_played'] == 5:
                    if  team2['WforSum'] == 5:
                        team2['WinTable'] = .645455
                    elif team2['WforSum'] == 4:
                        team2['WinTable'] = .6
                    elif team2['WforSum'] == 3:
                        team2['WinTable'] = .527273
                    elif  team2['WforSum'] == 2:
                        team2['WinTable'] = .463636
                    elif team2['WforSum'] == 1:
                        team2['WinTable'] = 0.409091
                    else:
                        team2['WinTable'] = 0.363636
                elif team2['Games_played'] == 6:
                    if  team2['WforSum'] == 6:
                        team2['WinTable'] = .66
                    elif team2['WforSum'] == 5:
                        team2['WinTable'] = .6
                    elif team2['WforSum'] == 4:
                        team2['WinTable'] = .55
                    elif team2['WforSum'] == 3:
                        team2['WinTable'] = .52
                    elif  team2['WforSum'] == 2:
                        team2['WinTable'] = .42
                    elif team2['WforSum'] == 1:
                        team2['WinTable'] = 0.39
                    else:
                        team2['WinTable'] = 0.32
                elif team2['Games_played'] == 7:
                    if  team2['WforSum'] == 7:
                        team2['WinTable'] = .688889
                    elif team2['WforSum'] == 6:
                        team2['WinTable'] = .63333
                    elif team2['WforSum'] == 5:
                        team2['WinTable'] = .577778
                    elif team2['WforSum'] == 4:
                        team2['WinTable'] = .522222
                    elif team2['WforSum'] == 3:
                        team2['WinTable'] = .477778
                    elif  team2['WforSum'] == 2:
                        team2['WinTable'] = .4
                    elif team2['WforSum'] == 1:
                        team2['WinTable'] = 0.38889
                    else:
                        team2['WinTable'] = 0.32222
                elif team2['Games_played'] == 8:
                    if team2['WforSum'] == 8.0:
                        team2['WinTable'] = .675
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .675
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .6
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .5875
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .4875
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .4375
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .3625
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .35
                    else:
                        team2['WinTable'] = .3125
                elif team2['Games_played'] == 9:
                    if team2['WforSum'] == 9.0:
                        team2['WinTable'] = .642857
                    elif team2['Wfor'] == 8.0:
                         team2['WinTable'] = .7
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .628571
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .6
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .557143
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .442857
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .414286
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .357142
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .314286
                    else:
                        team2['WinTable'] = .242857
                elif team2['Games_played'] == 10:
                    if team2['WforSum'] == 10.0:
                        team2['WinTable'] = .666667
                    elif team2['Wfor'] == 9.0:
                         team2['WinTable'] = .65
                    elif team2['Wfor'] == 8.0:
                         team2['WinTable'] = .65
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .616667
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .566667
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .516667
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .433333
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .4
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .3
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .3
                    else:
                        team2['WinTable'] = .283333
                elif team2['Games_played'] == 11:
                    if team2['WforSum'] == 11.0:
                        team2['WinTable'] = .68
                    elif team2['Wfor'] == 10.0:
                         team2['WinTable'] = .62
                    elif team2['Wfor'] == 9.0:
                         team2['WinTable'] = .7
                    elif team2['Wfor'] == 8.0:
                         team2['WinTable'] = .62
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .58
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .54
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .46
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .44
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .4
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .3
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .3
                    else:
                        team2['WinTable'] = .283333
                elif team2['Games_played'] == 12:
                    if team2['WforSum'] == 12.0:
                        team2['WinTable'] = .6
                    elif team2['Wfor'] == 11.0:
                         team2['WinTable'] = .575
                    elif team2['Wfor'] == 10.0:
                         team2['WinTable'] = .7
                    elif team2['Wfor'] == 9.0:
                         team2['WinTable'] = .65
                    elif team2['Wfor'] == 8.0:
                         team2['WinTable'] = .575
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .55
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .55
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .45
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .4
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .35
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .3
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .325
                    else:
                        team2['WinTable'] = .3
                elif team2['Games_played'] == 13:
                    if team2['WforSum'] == 13.0:
                        team2['WinTable'] = .466667
                    elif team2['Wfor'] == 12.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 11.0:
                         team2['WinTable'] = .633333
                    elif team2['Wfor'] == 10.0:
                         team2['WinTable'] = .666667
                    elif team2['Wfor'] == 9.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 8.0:
                         team2['WinTable'] = .566667
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .5
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .5
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .466667
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .333333
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .333333
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .333333
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .2
                    else:
                        team2['WinTable'] = .333333
                elif team2['Games_played'] == 14:
                    if team2['WforSum'] == 14.0:
                        team2['WinTable'] = .5
                    elif team2['Wfor'] == 13.0:
                         team2['WinTable'] = .55
                    elif team2['Wfor'] == 12.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 11.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 10.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 9.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 8.0:
                         team2['WinTable'] = .55
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .5
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .5
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .45
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .3
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .4
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .25
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .2
                    else:
                        team2['WinTable'] = 0.0
                elif team2['Games_played'] == 15:
                    if team2['WforSum'] == 15.0:
                        team2['WinTable'] = 1
                    elif team2['Wfor'] == 14.0:
                         team2['WinTable'] = .8
                    elif team2['Wfor'] == 13.0:
                         team2['WinTable'] = .4
                    elif team2['Wfor'] == 12.0:
                         team2['WinTable'] = .7
                    elif team2['Wfor'] == 11.0:
                         team2['WinTable'] = .7
                    elif team2['Wfor'] == 10.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 9.0:
                         team2['WinTable'] = .6
                    elif team2['Wfor'] == 8.0:
                         team2['WinTable'] = .5
                    elif team2['Wfor'] == 7.0:
                         team2['WinTable'] = .5
                    elif team2['WforSum'] == 6.0:
                         team2['WinTable'] = .4
                    elif team2['WforSum'] == 5.0:
                         team2['WinTable'] = .4
                    elif team2['WforSum'] == 4.0:
                         team2['WinforSum'] = .2
                    elif team2['WforSum'] == 3.0:
                         team2['WinTable'] = .4
                    elif team2['WforSum'] == 2.0:
                         team2['WinTable'] = .1
                    elif team2['WforSum'] == 1.0:
                         team2['WinTable'] = .2
                    else:
                        team2['WinTable'] = 0.0
