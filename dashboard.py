import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time
from matplotlib import pyplot as plt



# Function to load data
def load_data():
    data = pd.read_csv('nba_player_data.csv')
    return data

# Function for EDA and visualizations
def perform_eda(data):
    # Your EDA and visualization code here
    # ...

    data.isna().sum()
    #drop usless columns
    data.drop(columns=['RANK', 'EFF'], inplace=True)
    #change format of season year
    data['season_start_year'] = data['Year'].str[:4].astype(int)
    data.TEAM.unique()
    #Teams that changed names need the info combinded
    data['TEAM'].replace(to_replace=['NOP','NOH'], value = 'NO', inplace=True)
    #readability of season type fix
    data['Season_type'].replace('Regular%20Season', 'Regular Season', inplace=True)
    regular_df = data[data['Season_type'] == 'Regular Season']
    playoffs_df = data[data['Season_type'] == 'Playoffs']
    data.columns
    #columns we can take the sum of
    total_cols = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 
                'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF','PTS']


# Function for displaying histograms
def display_histograms(df):
    # Your histogram code here
    # ...

    #histogram for percent of players that played a range of total minutes playoffs
    fig = px.histogram(x=playoffs_df['MIN'], histnorm='percent')
    fig.show()

    fig = px.histogram(x=regular_df['MIN'], histnorm='percent')
    fig.show()

    def hist_data(df=regular_df, min_MIN=0, min_GP=0):
        return df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'MIN']/\
        df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'GP']

    #rotation of bench and starter minutes in playoff vs regular season. 
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=hist_data(regular_df,50,5), histnorm='percent', name='RS',
                            xbins={'start':0,'end':45,'size':1}))
    fig.add_trace(go.Histogram(x=hist_data(playoffs_df,5,1), histnorm='percent',
                            name='Playoffs', xbins={'start':0,'end':46,'size':1}))
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.5)
    fig.show()

# Function for displaying correlation heatmap
def display_correlation_heatmap(df):
    # Your correlation heatmap code here
    # ...

    # altering data to show stat per min played for better comparability 
#filter out players with less then 50 min/season total
    data_per_min = data.groupby(['PLAYER','PLAYER_ID','Year'])[total_cols].sum().reset_index()
    for col in data_per_min.columns[4:]:
        data_per_min[col] = data_per_min[col]/data_per_min['MIN']

    data_per_min['FG%'] = data_per_min['FGM']/data_per_min['FGA'] #shooting percentage
    data_per_min['3PT%'] = data_per_min['FG3M']/data_per_min['FG3A'] #shooting percentage
    data_per_min['FT%'] = data_per_min['FTM']/data_per_min['FTA'] #shooting percentage
    data_per_min['FG3A%'] = data_per_min['FG3A']/data_per_min['FGA'] #percentage of 3pt attems
    data_per_min['PTS/FGA'] = data_per_min['PTS']/data_per_min['FGA'] #avg points per attempt
    data_per_min['FG3M/FGM'] = data_per_min['FG3M']/data_per_min['FGM'] #percentage of field goal makes from behind arc
    data_per_min['FTA/FGA'] = data_per_min['FTA']/data_per_min['FGA'] #free throw rate
    data_per_min['TRU%'] = data_per_min['PTS']/(data_per_min['FGA']+0.475*data_per_min['FTA']) #true shooting percentage(not actual percetage)
    data_per_min['AST_TOV'] = data_per_min['AST']/data_per_min['TOV'] #turnaover ratio

    data_per_min = data_per_min[data_per_min['MIN']>=50]
    data_per_min.drop(columns='PLAYER_ID', inplace=True)

    fig = px.imshow(data_per_min.corr())

    fig.show()
    #dark purple shows negative correlation between stats
    #bright yellow shows positive correlation between stats

# Function for displaying percentage change plots
def display_percentage_change_plots(df):
    # Your percentage change plots code here
    # ...

    rs_change_df = regular_df.groupby('season_start_year')[total_cols].sum().reset_index()
    playoffs_change_df = playoffs_df.groupby('season_start_year')[total_cols].sum().reset_index()

    for i in [rs_change_df,playoffs_change_df]:
        i['POSS_est'] = i['FGA']-i['OREB']+i['TOV']+0.44*i['FTA']
        i['POSS_per_48'] = (i['POSS_est']/i['MIN'])*48*5
        
        i['FG%'] = i['FGM']/i['FGA']
        i['3PT%'] = i['FG3M']/i['FG3A']
        i['FT%'] = i['FTM']/i['FTA']
        i['AST%'] = i['AST']/i['FGM']
        i['FG3A%'] = i['FG3A']/i['FGA']
        i['PTS/FGA'] = i['PTS']/i['FGA']
        i['FG3M/FGM'] = i['FG3M']/i['FGM']
        i['FTA/FGA'] = i['FTA']/i['FGA']
        i['TRU%'] = 0.5*i['PTS']/(i['FGA']+0.475*i['FTA'])
        i['AST_TOV'] = i['AST']/i['TOV']
        for col in total_cols:
            i[col] = 100*i[col]/i['POSS_est']
        i.drop(columns=['MIN','POSS_est'], inplace=True)
    
    #rs_change_df
    playoffs_change_df

    comp_change_df = round(100*(playoffs_change_df-rs_change_df)/rs_change_df,3)
    comp_change_df['season_start_year'] = list(range(2010,2021))
    comp_change_df

    fig = go.Figure()
    for col in comp_change_df.columns[1:]:
        fig.add_trace(go.Scatter(x=comp_change_df['season_start_year'],
                             y=comp_change_df[col], name=col))
    fig.show()

    change_df = data.groupby('season_start_year')[total_cols].sum().reset_index()
    change_df['POSS_est'] = change_df['FGA']-change_df['OREB']+change_df['TOV']+0.44*change_df['FTA']
    change_df = change_df[list(change_df.columns[0:2])+['POSS_est']+list(change_df.columns[2:-1])]

    change_df['FG%'] = change_df['FGM']/change_df['FGA']
    change_df['3PT%'] = change_df['FG3M']/change_df['FG3A']
    change_df['FT%'] = change_df['FTM']/change_df['FTA']
    change_df['AST%'] = change_df['AST']/change_df['FGM']
    change_df['FG3A%'] = change_df['FG3A']/change_df['FGA']
    change_df['PTS/FGA'] = change_df['PTS']/change_df['FGA']
    change_df['FG3M/FGM'] = change_df['FG3M']/change_df['FGM']
    change_df['FTA/FGA'] = change_df['FTA']/change_df['FGA']
    change_df['TRU%'] = 0.5*change_df['PTS']/(change_df['FGA']+0.475*change_df['FTA'])
    change_df['AST_TOV'] = change_df['AST']/change_df['TOV']

    change_per48_df = change_df.copy()
    for col in change_per48_df.columns[2:18]:
        change_per48_df[col] = (change_per48_df[col]/change_per48_df['MIN'])*48*5

    change_per48_df.drop(columns='MIN', inplace=True)

    fig = go.Figure()
    for col in change_per48_df.columns[1:]:
        fig.add_trace(go.Scatter(x=change_per48_df['season_start_year'],
                                y=change_per48_df[col], name=col))
    fig.show()

    change_per100_df = change_df.copy()

    for col in change_per100_df.columns[3:18]:
        change_per100_df[col] = (change_per100_df[col]/change_per100_df['POSS_est'])*100

    change_per100_df.drop(columns=['MIN','POSS_est'], inplace=True)
    change_per100_df

    fig = go.Figure()
    for col in change_per100_df.columns[1:]:
        fig.add_trace(go.Scatter(x=change_per100_df['season_start_year'],
                                y=change_per100_df[col], name=col))
    fig.show()


# Main function
def main():
    st.title("NBA Player Performance Dashboard")

    # Load data
    data = load_data()

    # Perform EDA and display visualizations
    perform_eda(data)

    # Display histograms
    st.subheader("Player Minutes Distribution:")
    display_histograms(data)

    # Display correlation heatmap
    st.subheader("Correlation Heatmap:")
    display_correlation_heatmap(data)

    # Display percentage change plots
    st.subheader("Percentage Change Over Seasons:")
    display_percentage_change_plots(data)

if __name__ == "__main__":
    main()
