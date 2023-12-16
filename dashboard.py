import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt




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
    ###data.columns
    #columns we can take the sum of
    total_cols = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 
                'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF','PTS']
    return playoffs_df, regular_df, total_cols


# Function for displaying histograms
def display_histograms(playoffs_df,regular_df):
    # Your histogram code here
    # ...
###
    
    #histogram for percent of players that played a range of total minutes playoffs
    fig = px.histogram(x=playoffs_df['MIN'], histnorm='percent', title = 'Playoffs Minutes Distribution')
    st.plotly_chart(fig)

    fig = px.histogram(x=regular_df['MIN'], histnorm='percent', title = 'Regular Season Minutes Distribution')
    st.plotly_chart(fig)

    def hist_data(df=regular_df, min_MIN=0, min_GP=0):
        return df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'MIN']/ df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'GP']
    
###
    #bench_rotation = st.checkbox("Show Bench Rotation")
    #hist_data_df = hist_data(regular_df, 50, 5) if not bench_rotation else hist_data(regular_df, 20, 5)
    
    #rotation of bench and starter minutes in playoff vs regular season. 
    #fig = go.Figure()
    #fig.add_trace(go.Histogram(x=hist_data(regular_df,50,5), histnorm='percent', name='RS',
    #                        xbins={'start':0,'end':45,'size':1}))
    #fig.add_trace(go.Histogram(x=hist_data(playoffs_df,5,1), histnorm='percent',
    #                        name='Playoffs', xbins={'start':0,'end':46,'size':1}))
    #fig.update_layout(barmode='overlay', title = 'Rotation of Bench and Starter Minutes')
    #fig.update_traces(opacity=0.5)
    #st.plotly_chart(fig)

# Function for displaying percentage change plots
def display_percentage_change_plots(playoffs_df, regular_df, total_cols, data):
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
    #playoffs_change_df

    comp_change_df = round(100*(playoffs_change_df-rs_change_df)/rs_change_df,3)
    comp_change_df['season_start_year'] = list(range(2010,2021))
    #comp_change_df

    fig = go.Figure()
    for col in comp_change_df.columns[1:]:
        fig.add_trace(go.Scatter(x=comp_change_df['season_start_year'],
                             y=comp_change_df[col], name=col))
    fig.update_layout(title = 'Percentage Change Over Seasons')
    st.plotly_chart(fig)

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

    #fig = go.Figure()
    #for col in change_per48_df.columns[1:]:
    #    fig.add_trace(go.Scatter(x=change_per48_df['season_start_year'],
    #                            y=change_per48_df[col], name=col))
    #fig.update_layout(title='Change Per 48 Minutes Over Seasons')
    #st.plotly_chart(fig)

    change_per100_df = change_df.copy()

    for col in change_per100_df.columns[3:18]:
        change_per100_df[col] = (change_per100_df[col]/change_per100_df['POSS_est'])*100

    change_per100_df.drop(columns=['MIN','POSS_est'], inplace=True)
    #change_per100_df

    #fig = go.Figure()
    #for col in change_per100_df.columns[1:]:
    #    fig.add_trace(go.Scatter(x=change_per100_df['season_start_year'],
    #                            y=change_per100_df[col], name=col))
    #fig.update_layout(title='Change Per 100 Possessions Over Seasons')
    #st.plotly_chart(fig)

def team_performance_analysis(data, season_type):
    team_performance = data[data['Season_type'] == season_type].groupby('TEAM').agg(
        Average_PTS=('PTS', 'mean'),
        Average_MIN=('MIN', 'mean'),
        Average_FG_PCT=('FG_PCT', 'mean'),
        Average_FG3_PCT=('FG3_PCT', 'mean'),
        Total_REB=('REB', 'sum')
    ).reset_index()

    return team_performance

# Main function
def main():
    st.title("NBA Player Performance Dashboard")

    # Load data
    data = load_data()

    # Perform EDA and display visualizations
    playoffs_df, regular_df , total_cols = perform_eda(data)

    # Display histograms
    st.subheader("Player Minutes Distribution:")
    display_histograms(playoffs_df, regular_df)

    # Display correlation heatmap
    #st.subheader("Correlation Heatmap:")
    #display_correlation_heatmap(playoffs_df, regular_df, total_cols, data)

    # Display percentage change plots
    st.subheader("Percentage Change Over Seasons:")
    display_percentage_change_plots(playoffs_df, regular_df, total_cols, data)


   # Dropdown to select season type
    season_type = st.sidebar.selectbox("Select Season Type", data['Season_type'].unique())

    # Team performance analysis
    team_performance = team_performance_analysis(data, season_type)

    # Plotting Team-wise Metrics
    st.subheader('Average Points per Team')
    chart_pts = alt.Chart(team_performance).mark_bar().encode(
        x='TEAM',
        y='Average_PTS',
        color=alt.value('blue')
    ).properties(width=600)
    st.altair_chart(chart_pts, use_container_width=True)


if __name__ == "__main__":
    main()
