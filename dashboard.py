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
def display_percentage_change_plots(playoffs_df, regular_df, total_cols, data, season_type):
    # ... (your existing percentage change plot code)

    comp_change_df = round(100*(playoffs_change_df - rs_change_df) / rs_change_df, 3)
    comp_change_df['season_start_year'] = list(range(2010, 2021))

    # Filter by season type
    if season_type == 'Playoff':
        comp_change_df = comp_change_df[comp_change_df['season_type'] == 'Playoffs']
    elif season_type == 'Regular Season':
        comp_change_df = comp_change_df[comp_change_df['season_type'] == 'Regular Season']

    fig = go.Figure()
    for col in comp_change_df.columns[1:]:
        fig.add_trace(go.Scatter(x=comp_change_df['season_start_year'],
                                 y=comp_change_df[col], name=col))

    fig.update_layout(title='Percentage Change Over Seasons')
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

# Main function
def main():
    st.title("NBA Player Performance Dashboard")

    # Load data
    data = load_data()

    # Perform EDA and display visualizations
    playoffs_df, regular_df , total_cols = perform_eda(data)

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

    # Display histograms
    st.subheader("Player Minutes Distribution:")
    display_histograms(playoffs_df, regular_df)

    # Display correlation heatmap
    #st.subheader("Correlation Heatmap:")
    #display_correlation_heatmap(playoffs_df, regular_df, total_cols, data)

    # Display percentage change plots
    st.sidebar.subheader("Percentage Change Over Seasons:")
    season_type_filter = st.sidebar.selectbox("Select Season Type", ['Playoff', 'Regular Season'])
    display_percentage_change_plots(playoffs_df, regular_df, total_cols, data, season_type_filter)


if __name__ == "__main__":
    main()
