#libraries

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

#the default Windows console (cp1252) can't print names like "Luka Dončić"
sys.stdout.reconfigure(encoding='utf-8')

#variable to store the dataset
data = pd.read_csv("nba_players_25_26_regular_season_wide_data.csv")
data_impact = data[['player_name', 'age_completed_years','position', 'team', 'minutes_played', 'one_point_made', 'two_point_made',
                 'three_point_made', 'offensive_rebounds', 'defensive_rebounds', 'assists','steals', 'blocks',
                   'turnovers', 'wins', 'losses']].copy()

#Initializing the dataset visualization functions

def visualize_dataset(data):
    print(data.head(10))
    print(data.dtypes)

def visualize_impact_dataset(data_impact):
    #work on a copy so the caller's dataset keeps its original columns
    data_impact = data_impact.copy()

    #missing wins/losses count as 0 games played
    data_impact.insert(5,'games_played', data_impact['wins'].fillna(0) + data_impact['losses'].fillna(0)) 
    #weight each shot by what it's worth, same as calculate_per_game
    data_impact.insert(6,'PTS', data_impact['one_point_made'] + data_impact['two_point_made']*2 + data_impact['three_point_made']*3)
    data_impact.insert(7,'REB', data_impact['offensive_rebounds'] + data_impact['defensive_rebounds'])

    data_impact.drop(columns = ['one_point_made', 'two_point_made', 'three_point_made', 'wins', 'losses',
                                'defensive_rebounds','offensive_rebounds'], inplace=True)
    print(data_impact.head(10)) 
    return data_impact

def calculate_per_game(data_impact):
     #work on a copy so the caller's dataset keeps its original columns
     data_impact = data_impact.copy()
     data_impact['PTS'] = (data_impact['one_point_made'] + data_impact['two_point_made']*2 + data_impact['three_point_made']*3)
     #missing wins/losses count as 0 games played
     data_impact['games_played'] = (data_impact['wins'].fillna(0) + data_impact['losses'].fillna(0))
     data_impact['REB'] = (data_impact['offensive_rebounds'] + data_impact['defensive_rebounds'])

     #players with 0 games played become NaN instead of dividing by zero
     games = data_impact['games_played'].where(data_impact['games_played'] > 0)

     data_impact['PTS_average'] = (data_impact['PTS']/games).round(2)
     data_impact['REB_average'] = (data_impact['REB']/games).round(2)
     data_impact['AST_average'] = (data_impact['assists']/games).round(2)
     data_impact['STL_average'] = (data_impact['steals']/games).round(2)
     data_impact['BLK_average'] = (data_impact['blocks']/games).round(2)
     data_impact['TOV_average'] = (data_impact['turnovers']/games).round(2)
     data_impact['MIN_average'] = (data_impact['minutes_played']/games).round(2)

     data_impact.drop(columns = ['one_point_made', 'two_point_made', 'three_point_made', 'wins', 'losses',
                                    'defensive_rebounds','offensive_rebounds','steals',
                                    'blocks','turnovers','assists','PTS','REB'], inplace=True)
     #minutes_played stays in the dataset for the correlation and the plots, it's just hidden from the table
     print(data_impact.drop(columns='minutes_played').head(10))
     return data_impact

def filter_by_games_played(data_impact):
    data_impact = data_impact.copy()

    max_games = data_impact['games_played'].max()
    min_games = max_games / 3
    filtered = data_impact[data_impact['games_played'] >= min_games]

    print(f'games floor: {min_games:.1f} (1/3 of {max_games:.0f}) - kept {len(filtered)} of {len(data_impact)} players')

    return filtered

def impact_score_40_minutes_calculator(data_impact):
    data_impact = data_impact.copy()

    #players with 0 minutes per game become NaN instead of dividing by zero
    minutes = data_impact['MIN_average'].where(data_impact['MIN_average'] > 0)

    data_impact['impact_score_40'] = ((data_impact['PTS_average'] + 1.2 * data_impact['REB_average'] + 1.5 *
                                   data_impact['AST_average'] + 2 * data_impact['STL_average'] + 2 *
                                   data_impact['BLK_average'] - data_impact['TOV_average'])
                                   /minutes*40).round(2)

    #minutes_played stays: the correlation and the plots below are built on it
    data_impact.drop(columns = ['PTS_average', 'AST_average', 'BLK_average', 'REB_average',
                                'STL_average','TOV_average','MIN_average','games_played'], inplace=True)

    data_impact =  data_impact.sort_values(by='impact_score_40', ascending=False)

    print(data_impact.drop(columns='minutes_played').head(10))
    return data_impact

def impact_score_game(data_impact):
     data_impact = data_impact.copy()

     data_impact['impact_score_game'] = (data_impact['PTS_average'] + 1.2 * data_impact['REB_average'] + 1.5 *
                                   data_impact['AST_average'] + 2 * data_impact['STL_average'] + 2 *
                                   data_impact['BLK_average'] - data_impact['TOV_average']).round(2)

     #minutes_played stays: the correlation and the plots below are built on it
     data_impact.drop(columns = ['PTS_average', 'AST_average', 'BLK_average', 'REB_average',
                                     'STL_average','TOV_average','MIN_average','games_played'], inplace=True)

     data_impact =  data_impact.sort_values(by='impact_score_game', ascending=False)

     print(data_impact.drop(columns='minutes_played').head(10))
     return data_impact

def average_top10_40_calc(data_impact):
    data_impact = data_impact.copy()
    data_impact =  data_impact.sort_values(by='impact_score_40', ascending=False)
    average_top10 = data_impact['impact_score_40'].head(10).mean().round(2)

    return average_top10

def age_average_40_calc(data_impact):
    data_impact = data_impact.copy()
    data_impact =  data_impact.sort_values(by='impact_score_40', ascending=False)
    age_average = data_impact['age_completed_years'].head(10).mean()

    return age_average

def age_group_40_build(data_impact):
    data_impact = data_impact.copy()
    
    data_impact['age_group'] = pd.cut(data_impact['age_completed_years'],
                                       bins=[18, 22, 26, 30, 34, np.inf],
                                       labels=['19-22','23-26','27-30','31-34','35+'])
    grouped = data_impact.groupby('age_group', observed=True)
    table = grouped['impact_score_40'].agg(['count','mean','max']).round(2).T
    table = table.rename(index={'count':'players_number',
                                   'mean':'average_impact_score',
                                   'max':'max_impact_score'})

    print(table)

    return table

def average_top10_game_calc(data_impact):
    data_impact = data_impact.copy()
    data_impact =  data_impact.sort_values(by='impact_score_game', ascending=False)
    average_top10_game = data_impact['impact_score_game'].head(10).mean().round(2)

    return average_top10_game

def age_average_game_calc(data_impact):
    data_impact = data_impact.copy()
    data_impact =  data_impact.sort_values(by='impact_score_game', ascending=False)
    age_average_game = data_impact['age_completed_years'].head(10).mean()

    return age_average_game

def age_group_game_build(data_impact):
    data_impact = data_impact.copy()
    
    data_impact['age_group'] = pd.cut(data_impact['age_completed_years'],
                                       bins=[18, 22, 26, 30, 34, np.inf],
                                       labels=['19-22','23-26','27-30','31-34','35+'])
    grouped = data_impact.groupby('age_group', observed=True)
    table = grouped['impact_score_game'].agg(['count','mean','max']).round(2).T
    table = table.rename(index={'count':'players_number',
                                   'mean':'average_impact_score',
                                   'max':'max_impact_score'})

    print(table)

    return table

def correlation_minutes_impact_score_game(data_impact):
    correlation = data_impact['minutes_played'].corr(data_impact['impact_score_game']).round(2)
    
    return correlation

def correlation_minutes_impact_score_40(data_impact):
    correlation = data_impact['minutes_played'].corr(data_impact['impact_score_40']).round(2)
    
    return correlation


def correlation_analysis(data_impact_game, data_impact):
    
    correlation = {'corr_minutes_game': correlation_minutes_impact_score_game(data_impact_game),
                   'corr_minutes_40': correlation_minutes_impact_score_40(data_impact)
                   }

    return correlation

def scatter_plot_minutes_impact_score_game(data_impact_game, correlation):
    #polyfit returns NaN coefficients if any row is incomplete, so drop them first
    data_impact_game = data_impact_game.dropna(subset=['minutes_played','impact_score_game'])

    #own figure, so this plot doesn't share axes with the cluster one
    plt.figure()
    plt.scatter(data_impact_game['minutes_played'],
                 data_impact_game['impact_score_game'])
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_game')
    plt.title('relationship between minutes_played and impact_score_game')
    plt.text(0.05, 0.95,  f'Pearson correlation: {correlation:.2f}',
             transform=plt.gca().transAxes)

    #linear regression
    x = data_impact_game['minutes_played']
    y = data_impact_game['impact_score_game']
    coeff = np.polyfit(x, y, 1)
    retta = np.poly1d(coeff)

    #sorted x, otherwise plot retraces the line back and forth
    x_line = np.sort(x.unique())
    plt.plot(x_line, retta(x_line), color='red')

def scatter_plot_minutes_impact_score_40(data_impact, correlation):
    #polyfit returns NaN coefficients if any row is incomplete, so drop them first
    data_impact = data_impact.dropna(subset=['minutes_played','impact_score_40'])

    #own figure, so this plot doesn't share axes with the cluster one
    plt.figure()
    plt.scatter(data_impact['minutes_played'],
                 data_impact['impact_score_40'])
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_40')
    plt.title('relationship between minutes_played and impact_score_40')
    plt.text(0.05, 0.95,  f'Pearson correlation: {correlation:.2f}',
             transform=plt.gca().transAxes)

    #linear regression
    x = data_impact['minutes_played']
    y = data_impact['impact_score_40']
    coeff = np.polyfit(x, y, 1)
    retta = np.poly1d(coeff)

    #sorted x, otherwise plot retraces the line back and forth
    x_line = np.sort(x.unique())
    plt.plot(x_line, retta(x_line), color='red')

def cluster_analysis_minutes_impact_score_game(data_impact_game):
    #KMeans can't handle NaN, so drop the incomplete rows before scaling
    data_impact_game = data_impact_game.dropna(subset=['minutes_played','impact_score_game']).copy()

    #standard data
    X = data_impact_game[['minutes_played', 'impact_score_game']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #k-means: 3 clusters, best silhouette score on this dataset
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    data_impact_game['clusters'] = kmeans.fit_predict(X_scaled)

    #Scatter plot, own figure so it doesn't share axes with the other one
    plt.figure()
    plt.scatter(data_impact_game['minutes_played'],
                 data_impact_game['impact_score_game'],
                 c=data_impact_game['clusters'])
    plt.title('Cluster analysis: minutes_played and impact_score_game')
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_game')

def cluster_analysis_minutes_impact_score_40(data_impact):
    #KMeans can't handle NaN, so drop the incomplete rows before scaling
    data_impact = data_impact.dropna(subset=['minutes_played','impact_score_40']).copy()

    #standard data
    X = data_impact[['minutes_played', 'impact_score_40']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #k-means: 3 clusters, best silhouette score on this dataset
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    data_impact['clusters'] = kmeans.fit_predict(X_scaled)

    #Scatter plot, own figure so it doesn't share axes with the other one
    plt.figure()
    plt.scatter(data_impact['minutes_played'],
                 data_impact['impact_score_40'],
                 c=data_impact['clusters'])
    plt.title('Cluster analysis: minutes_played and impact_score_40')
    plt.xlabel('minutes_played')
    plt.ylabel('impact_score_40')

def compare_top10_game(average_dataset):
    #players with 0 minutes per game become NaN instead of dividing by zero
    minutes = average_dataset['MIN_average'].where(average_dataset['MIN_average'] > 0)
    
    average_dataset['impact_score_game'] = (average_dataset['PTS_average'] + 1.2 * average_dataset['REB_average'] + 1.5 *
                                   average_dataset['AST_average'] + 2 * average_dataset['STL_average'] + 2 *
                                   average_dataset['BLK_average'] - average_dataset['TOV_average']).round(2)
    
    average_dataset.drop(columns = ['age_completed_years', 'team','minutes_played','games_played'], inplace = True)
    average_dataset =  average_dataset.sort_values(by='impact_score_game', ascending=False)
        
    print(average_dataset.head(10))
    return average_dataset

def compare_top10_40(average_dataset):
    #players with 0 minutes per game become NaN instead of dividing by zero
    minutes = average_dataset['MIN_average'].where(average_dataset['MIN_average'] > 0)
    
    average_dataset['impact_score_40'] = ((average_dataset['PTS_average'] + 1.2 * average_dataset['REB_average'] + 1.5 *
                                       average_dataset['AST_average'] + 2 * average_dataset['STL_average'] + 2 *
                                       average_dataset['BLK_average'] - average_dataset['TOV_average'])
                                       /minutes*40).round(2)
    
    average_dataset.drop(columns = ['impact_score_game'], inplace = True)
    average_dataset =  average_dataset.sort_values(by='impact_score_40', ascending=False)
        
    print(average_dataset.head(10))
    return average_dataset

def bar_chart_top10_40(data_impact):
    top10 = data_impact.sort_values(by='impact_score_40', ascending=False).head(10)

    plt.figure()
    plt.bar(top10['player_name'], top10['impact_score_40'])
    plt.xlabel('player')
    plt.ylabel('impact score 40')
    plt.title('Top 10 players by Impact Score per 40 minutes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.27)

def bar_chart_top10_game(data_impact):
    top10 = data_impact.sort_values(by='impact_score_game', ascending=False).head(10)

    plt.figure()
    plt.bar(top10['player_name'], top10['impact_score_game'])
    plt.xlabel('player')
    plt.ylabel('impact score game')
    plt.title('Top 10 players by Impact Score per game')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.27)



    
#main program
visualize_dataset(data)
print('\n')
visualize_impact_dataset(data_impact)  
print('\n')
average_dataset = calculate_per_game(data_impact)
print('\n')
qualified_dataset = filter_by_games_played(average_dataset)
print('\n')
impact_score_40 = impact_score_40_minutes_calculator(qualified_dataset)
print('\n')
average_top10_40 = average_top10_40_calc(impact_score_40)
print('average_top10_40:', average_top10_40)
age_average_top10_40 = age_average_40_calc(impact_score_40)
print('age_average_top10_40:', age_average_top10_40)
print('\n')
age_table_40 = age_group_40_build(impact_score_40)
print('\n')
data_impact_game = impact_score_game(qualified_dataset)
print('\n')
average_top10_game = average_top10_game_calc(data_impact_game)
print('average_top10_game:', average_top10_game)
age_average_top10_game = age_average_game_calc(data_impact_game)
print('age_average_top10_game:', age_average_top10_game)
print('\n')
age_table_game = age_group_game_build(data_impact_game)
print('\n')
correlation = correlation_analysis(data_impact_game, impact_score_40)
print(correlation)
scatter_plot_minutes_impact_score_game(data_impact_game, correlation['corr_minutes_game'])
cluster_analysis_minutes_impact_score_game(data_impact_game)
scatter_plot_minutes_impact_score_40(impact_score_40, correlation['corr_minutes_40'])
cluster_analysis_minutes_impact_score_40(impact_score_40)
print('\n')
compare_top10_game(average_dataset)
print('\n')
compare_top10_40(average_dataset)
bar_chart_top10_40(impact_score_40)
bar_chart_top10_game(data_impact_game)

plt.show()

