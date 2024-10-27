import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import json
import urllib3 # type: ignore
import re
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt # type: ignore
from matplotlib.patches import FancyBboxPatch # type: ignore
# import pybaseball as pyb # type: ignore
# from pybaseball import statcast_batter, spraychart  # type: ignore
# from streamlit_theme import st_theme

# Importar todas las funciones desde utils.py
from functions import *

# Settings
season = '2024'
statGroup = 'pitching'

teams = {
    "692":{
        "fullName":"Aguilas del Zulia",
        "abbreviation":"ZUL"
    },
    "693":{
        "fullName":"Cardenales de Lara",
        "abbreviation":"LAR"
        },
    "694":{
        "fullName":"Caribes de Anzoategui",
        "abbreviation":"ANZ"
    },
    "695":{
        "fullName":"Leones del Caracas",
        "abbreviation":"CAR"
    },
    "696":{
        "fullName":"Navegantes del Magallanes",
        "abbreviation":"MAG"
        },
    "697":{
        "fullName":"Bravos de Margarita",
        "abbreviation":"MAR"
        },
    "698":{
        "fullName":"Tiburones de La Guaira",
        "abbreviation":"LAG"
        },
    "699":{
        "fullName":"Tigres de Aragua",
        "abbreviation":"ARA"
    }
}


# theme = st_theme()
theme = {
    "primaryColor":"#ff4b4b",
    "backgroundColor":"#0e1117",
    "secondaryBackgroundColor":"#262730",
    "textColor":"#fafafa",
    "base":"dark",
    "font":"\"Source Sans Pro\", sans-serif",
    "linkText":"hsla(209, 100%, 59%, 1)",
    "fadedText05":"rgba(250, 250, 250, 0.1)",
    "fadedText10":"rgba(250, 250, 250, 0.2)",
    "fadedText20":"rgba(250, 250, 250, 0.3)",
    "fadedText40":"rgba(250, 250, 250, 0.4)",
    "fadedText60":"rgba(250, 250, 250, 0.6)",
    "bgMix":"rgba(26, 28, 36, 1)",
    "darkenedBgMix100":"hsla(228, 16%, 72%, 1)",
    "darkenedBgMix25":"rgba(172, 177, 195, 0.25)",
    "darkenedBgMix15":"rgba(172, 177, 195, 0.15)",
    "lightenedBg05":"hsla(220, 24%, 10%, 1)",
    "borderColor":"rgba(250, 250, 250, 0.2)",
    "borderColorLight":"rgba(250, 250, 250, 0.1)"
}

table_fields = {
    'pitching': {
        'standard': ['Season', 'Team', 'W', 'L', 'ERA', 'G', 'GS', 'QS', 'CG', 'SV', 'SVo', 'HLD', 'BS', 'IP', 'BF', 'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'HBP', 'SO'],
        'advanced': ['Season', 'Team', 'K/9', 'BB/9', 'K/BB', 'HR/9', 'K%', 'BB%', 'K-BB%', 'AVG', 'WHIP', 'BABIP', 'LOB%', 'FIP', 'ERA-FIP', 'xFIP', 'SIERA'],
        'battedBall': ['Season', 'Team', 'LD', 'GB', 'FB', 'PU', 'LD%', 'GB%', 'FB%', 'PU%', 'GB/FB', 'HR/FB', 'ERA+', 'FIP+', 'xFIP+', 'SIERA+'],
        'pitchedBall': ['Season', 'Team', 'Strikes', 'Balls', 'Pitches', 'P/IP', 'Strike%', 'Ball%', 'Whiffs', 'Contacts', 'Swings', 'Whiff%', 'SwStr%', 'CStr%', 'CSW%', 'WP', 'BK'],
        'winProb': ['Season', 'Team', 'WPA', '-WPA', '+WPA', 'pLI', 'inLI', 'gmLI', 'exLI', 'Pulls', 'WPA/LI', 'Clutch', 'SD', 'MD']
    }
}

# Set the page layout to wide
st.set_page_config(
    page_title="LVBP Stats",
    page_icon=":baseball:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Custom CSS to add percentual padding
st.markdown(
    """
    <style>
    .main {
        padding-left: 5%;
        padding-right: 5%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

_dir = './Static/Data/Players/'

# List all files in the directory
files = os.listdir(_dir)
files.sort(reverse=True)

players_df = pd.DataFrame()
players_list = []

for file in files:
    df = pd.read_csv(f'{_dir}{file}')

    if players_df.empty:
        players_df = df
    else:
        players_list = players_df['player.id'].unique().tolist()
        players_df = pd.concat([players_df, df.loc[~df['player.id'].isin(players_list)]], ignore_index=True)

players_df.loc[players_df['team.abbreviation'] == 'ORI', 'team.abbreviation'] = 'ANZ'
   
player_options, teams = players_breakdown(players_df.sort_values(by=['season', 'player.lastName'], ascending=[False, True]))

_dir = './Static/Data/Stats/'
files = os.listdir(_dir)
files.sort(reverse=True)

pitching_df = pd.DataFrame()

for file in files:
    df = pd.read_csv(f'{_dir}{file}')
    # pitching_df = pd.concat([pitching_df, df], ignore_index=True, join='outer')
    pitching_df = pd.concat([pitching_df, df], ignore_index=True, sort=False)

_dir = './Static/Data/Play by play/'
files = os.listdir(_dir)
files.sort(reverse=True)

play_by_play_df = pd.DataFrame()

for file in files:
    df = pd.read_csv(f'{_dir}{file}')
    df['season'] = file.replace('.csv', '')
    play_by_play_df = pd.concat([play_by_play_df, df], ignore_index=True)

_dir = './Static/Data/Team/'
files = os.listdir(_dir)
files.sort(reverse=True)

team_stats_df = pd.DataFrame()

for file in files:
    df = pd.read_csv(f'{_dir}{file}')
    df['season'] = file.replace('.csv', '')
    team_stats_df = pd.concat([team_stats_df, df], ignore_index=True)


col1, col2 = st.columns([3, 1])

# Add components to the first column (wide view)
with col1:
    st.header(':baseball: LVBP Pitching Stats') 

# Add components to the second column (narrow view)
with col2:
    player = st.selectbox(
        label = "Select a Pitcher",
        options = player_options.keys(),
        index = None,
        format_func = lambda x: player_options[x],
        placeholder = "type the name of the player...",
    )

st.divider()

# st.write(pitching_df)

players_df.set_index(['player.id'], inplace = True)
pitching_df = pitching_stats_format(pitching_df)
team_stats_df = pitching_stats_format(team_stats_df)
team_stats_df['Team'] = team_stats_df['team.id'].map(lambda x: teams[x]['fullName'])


if player:

    filtered_stat_df = pitching_df.loc[pitching_df['player.id'] == player]
    filtered_stat_df = filtered_stat_df.astype(str)

    # st.write(player)

    st.subheader("Player Information", divider="gray")

    st.write(f'Full Name: {players_df['player.fullFMLName'][player]}')
    st.write(f'Team: {players_df['team.name'][player]}')
    st.write(f'Position: {players_df['position.type'][player]}')
    st.write(f'B/T: {players_df['player.batSide.code'][player]}/{players_df['player.pitchHand.code'][player]}')
    st.write(f'Birthdate: {datetime.strptime(players_df['player.birthDate'][player], '%Y-%m-%d').strftime('%d/%m/%Y')}')
    st.write(f'Birthplace: {players_df['player.birthCity'][player]}, {players_df['player.birthCountry'][player]}')
    st.write(f'Last Active Season: {players_df['season'][player]}')

    st.markdown('')
    st.subheader("Standard Stats", divider="gray")
    st.dataframe(filtered_stat_df[table_fields['pitching']['standard']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Advanced Stats", divider="gray")
    st.dataframe(filtered_stat_df[table_fields['pitching']['advanced']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Batted Ball Stats", divider="gray")
    st.dataframe(filtered_stat_df[table_fields['pitching']['battedBall']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Pitched Ball Stats", divider="gray")
    st.dataframe(filtered_stat_df[table_fields['pitching']['pitchedBall']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Win Probability", divider="gray")
    st.dataframe(filtered_stat_df[table_fields['pitching']['winProb']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Spray Charts", divider="gray")
    # st.pyplot(filtered_spraychart_df.plot(y='coordinates.coordY', x='coordinates.coordX', kind='scatter', title='Spray Char'))

    hit_colors = {
        'single': 'blue',
        'double': 'green',
        'triple': 'orange',
        'home_run': 'red',
        'out': 'grey',
        'field_error': 'white'
    }

    filtered_spraychart_df = play_by_play_df.loc[(play_by_play_df['matchup.pitcher.id'] == player) & (play_by_play_df['trajectory'].notnull())]
    plot_seasons_list = filtered_spraychart_df['season'].unique().tolist()
    # plot_seasons_list.reverse()

    col1, col2 = st.columns([1, 4])

    # Add components to the first column (wide view)
    with col1:

        if len(plot_seasons_list) == 1:
            season_plot = st.selectbox(
                label = "Select a Season",
                options = plot_seasons_list,
                index = 0,
                placeholder = "type the name of the player...",
                disabled=True
            )
        else:
            season_plot = st.selectbox(
                label = "Select a Season",
                options = plot_seasons_list,
                index = 0,
                placeholder = "type the name of the player...",
                disabled=False
            )

    # Add components to the second column (narrow view)
    # with col2:

    filtered_spraychart_df_1 = filtered_spraychart_df.loc[filtered_spraychart_df['season'] == season_plot]

    # Create scatter plot
    col1, col2 = st.columns([1, 1])

    lefties = filtered_spraychart_df_1.loc[filtered_spraychart_df_1['matchup.batSide.code'] == 'L']
    righties = filtered_spraychart_df_1.loc[filtered_spraychart_df_1['matchup.batSide.code'] == 'R']

    with col1:
        show_spraychart(hit_colors, lefties, f'{players_df['player.fullName'][player]} vs LHBs', theme)

    with col2:
        show_spraychart(hit_colors, righties, f'{players_df['player.fullName'][player]} vs RHBs', theme)

else:
    
    seasons_list = team_stats_df['Season'].unique().tolist()

    col1, col2 = st.columns([1, 6])

    with col1:

        if len(seasons_list) == 1:
            season_selected = st.selectbox(
                label = "Select a Season",
                options = seasons_list,
                index = 0,
                placeholder = "type the name of the player...",
                disabled=True
            )
        else:
            season_selected = st.selectbox(
                label = "Select a Season",
                options = seasons_list,
                index = 0,
                placeholder = "type the name of the player...",
                disabled=False
            )
            
    filtered_colective_stats = team_stats_df.loc[team_stats_df['Season'] == season_selected].sort_values(by=['Season', 'ERA'], ascending=[True, True])
    filtered_colective_stats = filtered_colective_stats.astype(str)

    st.markdown('')
    st.subheader("Standard Stats", divider="gray")
    st.dataframe(filtered_colective_stats[table_fields['pitching']['standard']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Advanced Stats", divider="gray")
    st.dataframe(filtered_colective_stats[table_fields['pitching']['advanced']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Batted Ball Stats", divider="gray")
    st.dataframe(filtered_colective_stats[table_fields['pitching']['battedBall']], hide_index = True, use_container_width=True)

    st.markdown('')
    st.subheader("Pitched Ball Stats", divider="gray")
    st.dataframe(filtered_colective_stats[table_fields['pitching']['pitchedBall']], hide_index = True, use_container_width=True)