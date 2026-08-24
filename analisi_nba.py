import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

#the default Windows console (cp1252) can't print names like "Luka Dončić"
sys.stdout.reconfigure(encoding='utf-8')

raw_data = pd.read_csv("nba_players_25_26_regular_season_wide_data.csv")
season_stats = raw_data[['player_name', 'age_completed_years', 'position', 'team', 'minutes_played',
                         'one_point_made', 'two_point_made', 'three_point_made',
                         'offensive_rebounds', 'defensive_rebounds',
                         'assists', 'steals', 'blocks', 'turnovers', 'wins', 'losses']].copy()


def explore_dataset(raw_data):
    print(raw_data.head(10))
    print(raw_data.dtypes)

def build_season_totals(season_stats):
    season_totals = season_stats.copy()

    #missing wins/losses count as 0 games played
    season_totals.insert(5, 'games_played',
                         season_totals['wins'].fillna(0) + season_totals['losses'].fillna(0))
    season_totals.insert(6, 'PTS',
                         season_totals['one_point_made']
                         + season_totals['two_point_made'] * 2
                         + season_totals['three_point_made'] * 3)
    season_totals.insert(7, 'REB',
                         season_totals['offensive_rebounds'] + season_totals['defensive_rebounds'])

    season_totals.drop(columns=['one_point_made', 'two_point_made', 'three_point_made',
                                'wins', 'losses', 'defensive_rebounds', 'offensive_rebounds'],
                       inplace=True)

    print(season_totals.head(10))
    return season_totals

def calculate_per_game_averages(season_stats):
    per_game = season_stats.copy()

    per_game['PTS'] = (per_game['one_point_made']
                       + per_game['two_point_made'] * 2
                       + per_game['three_point_made'] * 3)
    #missing wins/losses count as 0 games played
    per_game['games_played'] = (per_game['wins'].fillna(0) + per_game['losses'].fillna(0))
    per_game['REB'] = (per_game['offensive_rebounds'] + per_game['defensive_rebounds'])

    #0 games played -> NaN instead of dividing by zero
    games = per_game['games_played'].where(per_game['games_played'] > 0)

    per_game['PTS_average'] = (per_game['PTS'] / games).round(2)
    per_game['REB_average'] = (per_game['REB'] / games).round(2)
    per_game['AST_average'] = (per_game['assists'] / games).round(2)
    per_game['STL_average'] = (per_game['steals'] / games).round(2)
    per_game['BLK_average'] = (per_game['blocks'] / games).round(2)
    per_game['TOV_average'] = (per_game['turnovers'] / games).round(2)
    per_game['MIN_average'] = (per_game['minutes_played'] / games).round(2)

    per_game.drop(columns=['one_point_made', 'two_point_made', 'three_point_made',
                           'wins', 'losses', 'defensive_rebounds', 'offensive_rebounds',
                           'steals', 'blocks', 'turnovers', 'assists', 'PTS', 'REB'],
                  inplace=True)

    #minutes_played stays in the dataset for the correlation and the plots, just hidden from the table
    print(per_game.drop(columns='minutes_played').head(10))
    return per_game

def filter_by_games_played(per_game_stats):
    players = per_game_stats.copy()

    max_games = players['games_played'].max()
    games_floor = max_games / 3
    qualified = players[players['games_played'] >= games_floor]

    print(f'games floor: {games_floor:.1f} (1/3 of {max_games:.0f}) - '
          f'kept {len(qualified)} of {len(players)} players')

    return qualified

def calculate_impact_score_40(qualified_players):
    ranking = qualified_players.copy()

    #0 minutes per game -> NaN instead of dividing by zero
    minutes_per_game = ranking['MIN_average'].where(ranking['MIN_average'] > 0)

    ranking['impact_score_40'] = ((ranking['PTS_average']
                                   + 1.2 * ranking['REB_average']
                                   + 1.5 * ranking['AST_average']
                                   + 2 * ranking['STL_average']
                                   + 2 * ranking['BLK_average']
                                   - ranking['TOV_average'])
                                  / minutes_per_game * 40).round(2)

    #minutes_played stays: the correlation and the plots below are built on it
    ranking.drop(columns=['PTS_average', 'AST_average', 'BLK_average', 'REB_average',
                          'STL_average', 'TOV_average', 'MIN_average', 'games_played'],
                 inplace=True)

    ranking = ranking.sort_values(by='impact_score_40', ascending=False)

    print(ranking.drop(columns='minutes_played').head(10))
    return ranking

def calculate_impact_score_game(qualified_players):
    ranking = qualified_players.copy()

    ranking['impact_score_game'] = (ranking['PTS_average']
                                    + 1.2 * ranking['REB_average']
                                    + 1.5 * ranking['AST_average']
                                    + 2 * ranking['STL_average']
                                    + 2 * ranking['BLK_average']
                                    - ranking['TOV_average']).round(2)

    #minutes_played stays: the correlation and the plots below are built on it
    ranking.drop(columns=['PTS_average', 'AST_average', 'BLK_average', 'REB_average',
                          'STL_average', 'TOV_average', 'MIN_average', 'games_played'],
                 inplace=True)

    ranking = ranking.sort_values(by='impact_score_game', ascending=False)

    print(ranking.drop(columns='minutes_played').head(10))
    return ranking

def calculate_top10_average_score_40(ranking):
    ranking = ranking.copy()
    ranking = ranking.sort_values(by='impact_score_40', ascending=False)
    average_score = ranking['impact_score_40'].head(10).mean().round(2)

    return average_score

def calculate_top10_average_age_40(ranking):
    ranking = ranking.copy()
    ranking = ranking.sort_values(by='impact_score_40', ascending=False)
    average_age = ranking['age_completed_years'].head(10).mean()

    return average_age

def build_age_group_table_40(ranking):
    ranking = ranking.copy()

    ranking['age_group'] = pd.cut(ranking['age_completed_years'],
                                  bins=[18, 22, 26, 30, 34, np.inf],
                                  labels=['19-22', '23-26', '27-30', '31-34', '35+'])
    grouped = ranking.groupby('age_group', observed=True)
    table = grouped['impact_score_40'].agg(['count', 'mean', 'max']).round(2).T
    table = table.rename(index={'count': 'players_number',
                                'mean': 'average_impact_score',
                                'max': 'max_impact_score'})

    print(table)

    return table

def calculate_top10_average_score_game(ranking):
    ranking = ranking.copy()
    ranking = ranking.sort_values(by='impact_score_game', ascending=False)
    average_score = ranking['impact_score_game'].head(10).mean().round(2)

    return average_score

def calculate_top10_average_age_game(ranking):
    ranking = ranking.copy()
    ranking = ranking.sort_values(by='impact_score_game', ascending=False)
    average_age = ranking['age_completed_years'].head(10).mean()

    return average_age

def build_age_group_table_game(ranking):
    ranking = ranking.copy()

    ranking['age_group'] = pd.cut(ranking['age_completed_years'],
                                  bins=[18, 22, 26, 30, 34, np.inf],
                                  labels=['19-22', '23-26', '27-30', '31-34', '35+'])
    grouped = ranking.groupby('age_group', observed=True)
    table = grouped['impact_score_game'].agg(['count', 'mean', 'max']).round(2).T
    table = table.rename(index={'count': 'players_number',
                                'mean': 'average_impact_score',
                                'max': 'max_impact_score'})

    print(table)

    return table

def calculate_minutes_correlation_game(ranking):
    correlation = ranking['minutes_played'].corr(ranking['impact_score_game']).round(2)

    return correlation

def calculate_minutes_correlation_40(ranking):
    correlation = ranking['minutes_played'].corr(ranking['impact_score_40']).round(2)

    return correlation

def collect_correlations(ranking_game, ranking_40):
    correlations = {'corr_minutes_game': calculate_minutes_correlation_game(ranking_game),
                    'corr_minutes_40': calculate_minutes_correlation_40(ranking_40)}

    return correlations

def plot_minutes_vs_score_game(ranking, correlation):
    #polyfit returns NaN coefficients if any row is incomplete, so drop them first
    ranking = ranking.dropna(subset=['minutes_played', 'impact_score_game'])

    plt.figure()
    plt.scatter(ranking['minutes_played'],
                ranking['impact_score_game'])
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_game')
    plt.title('relationship between minutes_played and impact_score_game')
    plt.text(0.05, 0.95, f'Pearson correlation: {correlation:.2f}',
             transform=plt.gca().transAxes)

    x = ranking['minutes_played']
    y = ranking['impact_score_game']
    coefficients = np.polyfit(x, y, 1)
    regression_line = np.poly1d(coefficients)

    #sorted x, otherwise plot retraces the line back and forth
    x_line = np.sort(x.unique())
    plt.plot(x_line, regression_line(x_line), color='red')

def plot_minutes_vs_score_40(ranking, correlation):
    #polyfit returns NaN coefficients if any row is incomplete, so drop them first
    ranking = ranking.dropna(subset=['minutes_played', 'impact_score_40'])

    plt.figure()
    plt.scatter(ranking['minutes_played'],
                ranking['impact_score_40'])
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_40')
    plt.title('relationship between minutes_played and impact_score_40')
    plt.text(0.05, 0.95, f'Pearson correlation: {correlation:.2f}',
             transform=plt.gca().transAxes)

    x = ranking['minutes_played']
    y = ranking['impact_score_40']
    coefficients = np.polyfit(x, y, 1)
    regression_line = np.poly1d(coefficients)

    #sorted x, otherwise plot retraces the line back and forth
    x_line = np.sort(x.unique())
    plt.plot(x_line, regression_line(x_line), color='red')

def plot_cluster_analysis_game(ranking):
    #KMeans can't handle NaN, so drop the incomplete rows before scaling
    ranking = ranking.dropna(subset=['minutes_played', 'impact_score_game']).copy()

    features = ranking[['minutes_played', 'impact_score_game']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    #3 clusters, best silhouette score on this dataset
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    ranking['clusters'] = kmeans.fit_predict(features_scaled)

    plt.figure()
    plt.scatter(ranking['minutes_played'],
                ranking['impact_score_game'],
                c=ranking['clusters'])
    plt.title('Cluster analysis: minutes_played and impact_score_game')
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_game')

def plot_cluster_analysis_40(ranking):
    #KMeans can't handle NaN, so drop the incomplete rows before scaling
    ranking = ranking.dropna(subset=['minutes_played', 'impact_score_40']).copy()

    features = ranking[['minutes_played', 'impact_score_40']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    #3 clusters, best silhouette score on this dataset
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    ranking['clusters'] = kmeans.fit_predict(features_scaled)

    plt.figure()
    plt.scatter(ranking['minutes_played'],
                ranking['impact_score_40'],
                c=ranking['clusters'])
    plt.title('Cluster analysis: minutes_played and impact_score_40')
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_40')

def build_top10_comparison_game(qualified_players):
    comparison = qualified_players.copy()

    comparison['impact_score_game'] = (comparison['PTS_average']
                                       + 1.2 * comparison['REB_average']
                                       + 1.5 * comparison['AST_average']
                                       + 2 * comparison['STL_average']
                                       + 2 * comparison['BLK_average']
                                       - comparison['TOV_average']).round(2)

    comparison.drop(columns=['age_completed_years', 'team',
                             'minutes_played', 'games_played'],
                    inplace=True)

    comparison = comparison.sort_values(by='impact_score_game', ascending=False)

    print(comparison.head(10))
    return comparison

def build_top10_comparison_40(qualified_players):
    comparison = qualified_players.copy()

    #0 minutes per game -> NaN instead of dividing by zero
    minutes_per_game = comparison['MIN_average'].where(comparison['MIN_average'] > 0)

    comparison['impact_score_40'] = ((comparison['PTS_average']
                                      + 1.2 * comparison['REB_average']
                                      + 1.5 * comparison['AST_average']
                                      + 2 * comparison['STL_average']
                                      + 2 * comparison['BLK_average']
                                      - comparison['TOV_average'])
                                     / minutes_per_game * 40).round(2)

    comparison.drop(columns=['age_completed_years', 'team',
                             'minutes_played', 'games_played'],
                    inplace=True)

    comparison = comparison.sort_values(by='impact_score_40', ascending=False)

    print(comparison.head(10))
    return comparison

def plot_top10_bar_chart_40(ranking):
    top10 = ranking.sort_values(by='impact_score_40', ascending=False).head(10)

    plt.figure()
    plt.bar(top10['player_name'], top10['impact_score_40'])
    plt.xlabel('player')
    plt.ylabel('impact score 40')
    plt.title('Top 10 players by Impact Score per 40 minutes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.27)

def plot_top10_bar_chart_game(ranking):
    top10 = ranking.sort_values(by='impact_score_game', ascending=False).head(10)

    plt.figure()
    plt.bar(top10['player_name'], top10['impact_score_game'])
    plt.xlabel('player')
    plt.ylabel('impact score game')
    plt.title('Top 10 players by Impact Score per game')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.27)

def calculate_score_by_position_game(ranking):
    ranking = ranking.copy()

    position_table = ranking.groupby('position')['impact_score_game'].mean().round(2)
    position_table = position_table.sort_values(ascending=False)

    print(position_table)
    return position_table

def calculate_score_by_position_40(ranking):
    ranking = ranking.copy()

    position_table = ranking.groupby('position')['impact_score_40'].mean().round(2)
    position_table = position_table.sort_values(ascending=False)

    print(position_table)
    return position_table

def build_conclusions_table(ranking_40, ranking_game, age_group_table_40, age_group_table_game,
                            correlations, position_scores_40, position_scores_game):
    #the rankings are already sorted, so the best player is the first row
    top_player_game = ranking_game.iloc[0]
    top_player_40 = ranking_40.iloc[0]

    best_age_group_game = age_group_table_game.loc['average_impact_score'].idxmax()
    best_age_group_40 = age_group_table_40.loc['average_impact_score'].idxmax()

    conclusions = pd.DataFrame(
        {'per_game': [f"{top_player_game['player_name']} ({top_player_game['impact_score_game']})",
                      calculate_top10_average_score_game(ranking_game),
                      calculate_top10_average_age_game(ranking_game),
                      f"{best_age_group_game} "
                      f"({age_group_table_game.loc['average_impact_score'].max()})",
                      correlations['corr_minutes_game'],
                      f'{position_scores_game.index[0]} ({position_scores_game.iloc[0]})'],
         'per_40_minutes': [f"{top_player_40['player_name']} ({top_player_40['impact_score_40']})",
                            calculate_top10_average_score_40(ranking_40),
                            calculate_top10_average_age_40(ranking_40),
                            f"{best_age_group_40} "
                            f"({age_group_table_40.loc['average_impact_score'].max()})",
                            correlations['corr_minutes_40'],
                            f'{position_scores_40.index[0]} ({position_scores_40.iloc[0]})']},
        index=['highest impact', 'top 10 average impact score', 'top 10 average age',
               'best age band', 'minutes played correlation', 'best position'])

    print(conclusions)
    return conclusions

def plot_position_comparison(scores_game, scores_40):
    position_order = ['G', 'G-F', 'F-G', 'F', 'F-C', 'C-F', 'C']

    scores_game = scores_game.reindex(position_order)
    scores_40 = scores_40.reindex(position_order)
    x = np.arange(len(scores_game))
    width = 0.35

    plt.figure()
    plt.bar(x - width / 2, scores_game.values, width, label='Impact Score per game')
    plt.bar(x + width / 2, scores_40.values, width, label='Impact Score per 40 minutes')
    plt.xlabel('position')
    plt.ylabel('average impact score')
    plt.title('Average Impact Score by Position')
    plt.xticks(x, scores_game.index)
    plt.legend()
    plt.tight_layout()


#main program: first the tables, then the charts


# --- data ---

#1. exploring the dataset
explore_dataset(raw_data)
print('\n')
build_season_totals(season_stats)
print('\n')

#2. per-game averages, then only the players with enough games played
per_game_stats = calculate_per_game_averages(season_stats)
print('\n')
qualified_players = filter_by_games_played(per_game_stats)
print('\n')

#3-5. impact score per 40 minutes: ranking, top 10, age bands
ranking_40 = calculate_impact_score_40(qualified_players)
print('\n')
top10_average_score_40 = calculate_top10_average_score_40(ranking_40)
print('average_top10_40:', top10_average_score_40)
top10_average_age_40 = calculate_top10_average_age_40(ranking_40)
print('age_average_top10_40:', top10_average_age_40)
print('\n')
age_group_table_40 = build_age_group_table_40(ranking_40)
print('\n')

#3-5. same steps on the impact score per game
ranking_game = calculate_impact_score_game(qualified_players)
print('\n')
top10_average_score_game = calculate_top10_average_score_game(ranking_game)
print('average_top10_game:', top10_average_score_game)
top10_average_age_game = calculate_top10_average_age_game(ranking_game)
print('age_average_top10_game:', top10_average_age_game)
print('\n')
age_group_table_game = build_age_group_table_game(ranking_game)
print('\n')

#6. correlation between minutes played and impact score
correlations = collect_correlations(ranking_game, ranking_40)
print(correlations)
print('\n')

#7. the top 10 compared on the statistics the formula is built on
build_top10_comparison_game(qualified_players)
print('\n')
build_top10_comparison_40(qualified_players)

#8. average impact score by position
position_scores_game = calculate_score_by_position_game(ranking_game)
print('\n')
position_scores_40 = calculate_score_by_position_40(ranking_40)
print('\n')

#9. conclusions
build_conclusions_table(ranking_40, ranking_game, age_group_table_40, age_group_table_game,
                        correlations, position_scores_40, position_scores_game)


# --- charts ---

plot_minutes_vs_score_40(ranking_40, correlations['corr_minutes_40'])
plot_minutes_vs_score_game(ranking_game, correlations['corr_minutes_game'])

plot_cluster_analysis_40(ranking_40)
plot_cluster_analysis_game(ranking_game)

plot_top10_bar_chart_40(ranking_40)
plot_top10_bar_chart_game(ranking_game)

plot_position_comparison(position_scores_game, position_scores_40)

plt.show()
