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
data_impact = data[['player_name', 'age_completed_years', 'team', 'position', 'minutes_played', 'one_point_made', 'two_point_made',
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
                                    'defensive_rebounds','offensive_rebounds','minutes_played','steals',
                                    'blocks','turnovers','assists','PTS','REB'], inplace=True)
     print(data_impact.head(10))
     return data_impact

def filter_by_games_played(data_impact):
    #relative floor: 1/3 of the games played by the most-used player in the dataset,
    #so a partial season works too instead of hard-coding a full-season number
    data_impact = data_impact.copy()

    max_games = data_impact['games_played'].max()
    min_games = max_games / 3
    filtered = data_impact[data_impact['games_played'] >= min_games]

    print(f'games floor: {min_games:.1f} (1/3 of {max_games:.0f}) - kept {len(filtered)} of {len(data_impact)} players')

    return filtered

def impact_score_calculator(data_impact):
    data_impact = data_impact.copy()

    #players with 0 minutes per game become NaN instead of dividing by zero
    minutes = data_impact['MIN_average'].where(data_impact['MIN_average'] > 0)

    data_impact['impact_score'] = ((data_impact['PTS_average'] + 1.2 * data_impact['REB_average'] + 1.5 *
                                   data_impact['AST_average'] + 2 * data_impact['STL_average'] + 2 *
                                   data_impact['BLK_average'] - data_impact['TOV_average'])
                                   /minutes*40).round(2)

    data_impact.drop(columns = ['PTS_average', 'AST_average', 'BLK_average', 'REB_average',
                                'STL_average','TOV_average','MIN_average','games_played'], inplace=True)
    
    data_impact =  data_impact.sort_values(by='impact_score', ascending=False)

    print(data_impact.head(10))
    return data_impact

def average_top10_calc(data_impact):
    data_impact = data_impact.copy()
    data_impact =  data_impact.sort_values(by='impact_score', ascending=False)
    average_top10 = data_impact['impact_score'].head(10).mean().round(2)

    return average_top10

def age_average_calc(data_impact):
    data_impact = data_impact.copy()
    data_impact =  data_impact.sort_values(by='impact_score', ascending=False)
    age_average = data_impact['age_completed_years'].head(10).mean()

    return age_average

def age_group_build(data_impact):
    data_impact = data_impact.copy()
    
    data_impact['age_group'] = pd.cut(data_impact['age_completed_years'],
                                       bins=[18, 22, 26, 30, 34, np.inf],
                                       labels=['19-22','23-26','27-30','31-34','35+'])
    grouped = data_impact.groupby('age_group', observed=True)
    table = grouped['impact_score'].agg(['count','mean','max']).round(2).T
    table = table.rename(index={'count':'players_number',
                                   'mean':'average_impact_score',
                                   'max':'max_impact_score'})

    print(table)

    return table

def correlation_age_impact_score(data_impact):
    correlation = data_impact['age_completed_years'].corr(data_impact['impact_score']).round(2)

    return correlation

def scatter_plot_age_impact_score(data_impact, correlation):
    #polyfit returns NaN coefficients if any row is incomplete, so drop them first
    data_impact = data_impact.dropna(subset=['age_completed_years','impact_score'])

    #own figure, so this plot doesn't share axes with the cluster one
    plt.figure()
    plt.scatter(data_impact['age_completed_years'],
                 data_impact['impact_score'])
    plt.xlabel('age')
    plt.ylabel('impact_score')
    plt.title('relationship between age and impact_score')
    plt.text(0.05, 0.95,  f'Pearson correlation: {correlation:.2f}',
             transform=plt.gca().transAxes)

    #linear regression
    x = data_impact['age_completed_years']
    y = data_impact['impact_score']
    coeff = np.polyfit(x, y, 1)
    retta = np.poly1d(coeff)

    #sorted x, otherwise plot retraces the line back and forth
    x_line = np.sort(x.unique())
    plt.plot(x_line, retta(x_line), color='red')
    plt.show()
    plt.close()

def cluster_analysis_build(data_impact):
    #KMeans can't handle NaN, so drop the incomplete rows before scaling
    data_impact = data_impact.dropna(subset=['age_completed_years','impact_score']).copy()

    #standard data
    X = data_impact[['age_completed_years', 'impact_score']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #k-means
    kmeans = KMeans(n_clusters=3, random_state=42)
    data_impact['clusters'] = kmeans.fit_predict(X_scaled)

    #Scatter plot
    plt.figure()
    plt.scatter(data_impact['age_completed_years'],
                 data_impact['impact_score'],
                 c=data_impact['clusters'])
    plt.title('Cluster analysis: age and impact score')
    plt.xlabel('age')
    plt.ylabel('impact_score')
    plt.show()
    plt.close()





    
#main program
visualize_dataset(data)
print('\n')
work_dataset = visualize_impact_dataset(data_impact)  
print('\n')
average_dataset = calculate_per_game(data_impact)
print('\n')
qualified_dataset = filter_by_games_played(average_dataset)
print('\n')
impact_score = impact_score_calculator(qualified_dataset)
print('\n')
average_top10 = average_top10_calc(impact_score)
print('average_top10:', average_top10)
age_average = age_average_calc(impact_score)
print('age_average_top10:', age_average)
print('\n')
age_table = age_group_build(impact_score)
print('\n')
correlation = correlation_age_impact_score(impact_score)
scatter_plot_age_impact_score(impact_score, correlation)
cluster_analysis_build(impact_score)

