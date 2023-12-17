import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import altair as alt
import seaborn as sns



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

def team_performance_analysis(data, season_type):
    team_performance = data[data['Season_type'] == season_type].groupby('TEAM').agg(
        Average_PTS=('PTS', 'mean'),
        Average_MIN=('MIN', 'mean'),
        Average_FG_PCT=('FG_PCT', 'mean'),
        Average_FG3_PCT=('FG3_PCT', 'mean'),
        Total_REB=('REB', 'sum')
    ).reset_index()

    return team_performance

# Function to display AST_TOV histogram
def display_ast_tov_histogram(selected_df):
    # Your AST_TOV histogram code here
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(selected_df['AST_TOV'], bins=30, kde=True, color='skyblue', ax=ax)
    ax.set_title('Distribution of Assist-to-Turnover Ratio (AST_TOV)')
    ax.set_xlabel('AST_TOV')
    ax.set_ylabel('Frequency')
    st.pyplot(fig)


# Main function
def main():
    st.title("NBA Player Performance Dashboard")

    # Load data
    data = load_data()

    # Perform EDA and display visualizations
    playoffs_df, regular_df , total_cols = perform_eda(data)

    # Dropdown to filter by player
    selected_player = st.sidebar.selectbox("Select Player", data['PLAYER'].unique())

    # Dropdown to select season type
    season_type = st.sidebar.selectbox("Select Season Type", data['Season_type'].unique())

    # Team performance analysis
    team_performance = team_performance_analysis(data, season_type)

    # Filter data based on selections
    selected_df = data[(data['PLAYER'] == selected_player) & (data['Season_type'] == season_type)]

    # Plotting Team-wise Metrics
    st.subheader('Average Points per Team')
    chart_pts = alt.Chart(team_performance).mark_bar().encode(
        x='TEAM',
        y='Average_PTS',
        color=alt.value('blue')
    ).properties(width=600)
    st.altair_chart(chart_pts, use_container_width=True)

    # Display histograms
    st.subheader("Player Minutes Distribution:")
    display_histograms(playoffs_df, regular_df)

    # Display correlation heatmap
    #st.subheader("Correlation Heatmap:")
    #display_correlation_heatmap(playoffs_df, regular_df, total_cols, data)

    # Display percentage change plots
    st.subheader("Percentage Change Over Seasons:")
    display_percentage_change_plots(playoffs_df, regular_df, total_cols, data)

    # Display AST_TOV histogram
    st.subheader(f'Distribution of AST_TOV for {selected_player} - {season_type}')
    display_ast_tov_histogram(selected_df)


if __name__ == "__main__":
    main()
