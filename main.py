import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import json
import urllib3 # type: ignore
import re
import csv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt # type: ignore
from matplotlib.patches import FancyBboxPatch # type: ignore
from PIL import Image, ImageOps # type: ignore
from io import BytesIO
# import pybaseball as pyb # type: ignore
# from pybaseball import statcast_batter, spraychart  # type: ignore
# from streamlit_theme import st_theme

# Importar todas las funciones desde utils.py
from functions import *

# Obtener Textos de la Pagina
structure = pd.read_csv(f'./Static/Page Structure.csv', sep = ";").set_index('Code').to_dict()

lang_list = ['EN', 'ES']

# Settings
season = '2024'
statGroup = 'pitching'
share_url = 'https://lvbp-pitching-stats.streamlit.app/'
lang = 'ES'

# Obtener los parámetros de la URL
params = st.query_params

if "lang" in params and params["lang"] in lang_list:
    lang = 'EN'

base_path = './Static/Data/'

seasonType_dict = {
    structure[lang][5]: 'RS/',
    structure[lang][6]: 'WC/',
    structure[lang][7]: 'RR/',
    structure[lang][8]: 'FN/'
}

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

def get_data(folder):
    _dir = base_path+folder+'Players/'

    # print(_dir)

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

    _dir = base_path+folder+'Stats/'
    files = os.listdir(_dir)
    files.sort(reverse=True)

    # print(_dir)

    pitching_df = pd.DataFrame()

    for file in files:
        df = pd.read_csv(f'{_dir}{file}')
        # pitching_df = pd.concat([pitching_df, df], ignore_index=True, join='outer')
        pitching_df = pd.concat([pitching_df, df], ignore_index=True, sort=False)

    _dir = base_path+folder+'Play by play/'
    files = os.listdir(_dir)
    files.sort(reverse=True)

    # print(_dir)

    play_by_play_df = pd.DataFrame()

    for file in files:
        df = pd.read_csv(f'{_dir}{file}')
        df['season'] = file.replace('.csv', '')
        play_by_play_df = pd.concat([play_by_play_df, df], ignore_index=True)

    _dir = base_path+folder+'Team/'
    files = os.listdir(_dir)
    files.sort(reverse=True)

    # print(_dir)

    team_stats_df = pd.DataFrame()

    for file in files:
        df = pd.read_csv(f'{_dir}{file}')
        df['season'] = file.replace('.csv', '')
        team_stats_df = pd.concat([team_stats_df, df], ignore_index=True)

    return player_options, teams, players_df, pitching_df, play_by_play_df, team_stats_df

player_options, teams, players_df, pitching_df, play_by_play_df, team_stats_df = get_data(seasonType_dict[structure[lang][5]])

col1, col2 = st.columns([3, 2])

# Add components to the first column (wide view)
with col1:
    # st.header(':baseball: LVBP Pitching Stats') 
    
    st.markdown(
        """
            <style>
                .page-title {
                    color: white;
                    text-decoration: none;
                }
            </style>
        """+f"""
            <h2><a class="page-title" style="color: white;" href="https://lvbp-pitching-stats.streamlit.app/">⚾ {structure[lang][1]}</a></h2>
        """,
        unsafe_allow_html=True
    )


# Add components to the second column (narrow view)
with col2:

    col_1, col_2 = st.columns([1, 1])

    with col_1:

        seasonTypeSelected = st.selectbox(
            label = structure[lang][2],
            options = [structure[lang][5], structure[lang][6], structure[lang][7], structure[lang][8]],
            index = 0,
            # format_func = lambda x: player_options[x],
            placeholder = structure[lang][9],
        )

        if seasonTypeSelected != structure[lang][5]:
            player_options, teams, players_df, pitching_df, play_by_play_df, team_stats_df = get_data(seasonType_dict[seasonTypeSelected])
        else:
            player_options, teams, players_df, pitching_df, play_by_play_df, team_stats_df = get_data(seasonType_dict[structure[lang][5]])

    with col_2:
        
        if "player" in params and int(params["player"]) in list(player_options.keys()):
            # st.write("✅ Sí, se envió el parámetro 'nombre'")
            player = st.selectbox(
            label = structure[lang][3],
            options = player_options.keys(),
            index = list(player_options.keys()).index(int(params["player"])),
            format_func = lambda x: player_options[x],
            placeholder = structure[lang][10],
        )
        else:
            # st.write("❌ No, no se envió el parámetro 'nombre'")
            player = st.selectbox(
                label = structure[lang][3],
                options = player_options.keys(),
                index = None,
                format_func = lambda x: player_options[x],
                placeholder = structure[lang][10],
            )

st.divider()

players_df.set_index(['player.id'], inplace = True)
pitching_df = pitching_stats_format(pitching_df)
team_stats_df = pitching_stats_format(team_stats_df)
team_stats_df['Team'] = team_stats_df['team.id'].map(lambda x: teams[x]['fullName'])


if player:

    share_url = f'https://lvbp-pitching-stats.streamlit.app/?player={player}'

    filtered_stat_df = pitching_df.loc[pitching_df['player.id'] == player]

    standard_ = filtered_stat_df[table_fields['pitching']['standard']]
    advanced_ = filtered_stat_df[table_fields['pitching']['advanced']]
    battedBall_ = filtered_stat_df[table_fields['pitching']['battedBall']]
    pitchedBall_ = filtered_stat_df[table_fields['pitching']['pitchedBall']]
    winProb_ = filtered_stat_df[table_fields['pitching']['winProb']]

    # st.subheader("Player Information", divider="gray")
    # st.subheader("", divider="gray")

    headshot_url = get_headshot_url(player, 'milb')

    col1, col2 = st.columns([2, 6])

    with col1:

        # Mostrar la imagen con el marco en Streamlit
        # st.image(framed_image)

        frame_size = 7
        img_w = 180
        img_h = 260

        if headshot_url != 'None':

            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{headshot_url}" alt="Imagen con marco" style="border: {frame_size}px solid #BEC2C4; border-radius: 5px; width: {img_w + frame_size}px; height: {img_h + frame_size}px;">
                </div>
                <br>
                """,
                unsafe_allow_html=True
            )

        # st.write(f'Full Name: {players_df['player.fullFMLName'][player]}')
        # st.write(f'Team: {players_df['team.name'][player]}')
        # st.write(f'Position: {players_df['position.type'][player]}')
        # st.write(f'Bats/Throws: {players_df['player.batSide.code'][player]}/{players_df['player.pitchHand.code'][player]}')
        # st.write(f'Birthdate: {datetime.strptime(players_df['player.birthDate'][player], '%Y-%m-%d').strftime('%d/%m/%Y')}')
        # st.write(f'Birthplace: {players_df['player.birthCity'][player]}, {players_df['player.birthCountry'][player]}')
        # st.write(f'Last Active Season: {players_df['season'][player]}')

    with col2:
        if not pd.isna(players_df['player.primaryNumber'][player]):
            st.title(f'{players_df['player.nameFirstLast'][player]} #{int(players_df['player.primaryNumber'][player])}')
        else:
            st.title(f'{players_df['player.nameFirstLast'][player]}')
        st.subheader(f'{players_df['team.name'][player]}')
        st.subheader(f'{players_df['position.abbreviation'][player]} | {structure[lang][11]}: {players_df['player.batSide.code'][player]}/{players_df['player.pitchHand.code'][player]} | {players_df['player.height'][player]}/{int(players_df['player.weight'][player])}')
        st.subheader(f'{structure[lang][12]}: {datetime.strptime(players_df['player.birthDate'][player], '%Y-%m-%d').strftime('%d/%m/%Y')} {structure[lang][13]} {players_df['player.birthCity'][player]}, {players_df['player.birthCountry'][player]}')


    # with col3:
    #     st.title(f'{players_df['position.type'][player]}')
    #     st.subheader(f'{players_df['team.name'][player]}')

    st.markdown('')
    st.subheader(structure[lang][14], divider="gray")
    # st.dataframe(filtered_stat_df[table_fields['pitching']['standard']], hide_index = True, use_container_width=True)
    pitching_stats_formater(standard_)

    st.markdown('')
    st.subheader(structure[lang][15], divider="gray")
    # st.dataframe(filtered_stat_df[table_fields['pitching']['advanced']], hide_index = True, use_container_width=True)
    pitching_stats_formater(advanced_)

    st.markdown('')
    st.subheader(structure[lang][16], divider="gray")
    # st.dataframe(filtered_stat_df[table_fields['pitching']['battedBall']], hide_index = True, use_container_width=True)
    pitching_stats_formater(battedBall_)

    st.markdown('')
    st.subheader(structure[lang][17], divider="gray")
    # st.dataframe(filtered_stat_df[table_fields['pitching']['pitchedBall']], hide_index = True, use_container_width=True)
    pitching_stats_formater(pitchedBall_)

    st.markdown('')
    st.subheader(structure[lang][18], divider="gray")
    # st.dataframe(filtered_stat_df[table_fields['pitching']['winProb']], hide_index = True, use_container_width=True)
    pitching_stats_formater(winProb_)

    st.markdown('')
    st.subheader(structure[lang][19], divider="gray")
    # st.pyplot(filtered_spraychart_df.plot(y='coordinates.coordY', x='coordinates.coordX', kind='scatter', title='Spray Char'))

    hit_colors = {
        'single': 'blue',
        'double': 'green',
        'triple': 'orange',
        'home_run': 'red',
        'out': 'grey',
        'field_error': 'white'
    }

    col1, col2 = st.columns([1, 4])

    filtered_spraychart_df = play_by_play_df.loc[(play_by_play_df['matchup.pitcher.id'] == player) & (play_by_play_df['trajectory'].notnull())]
    seasons_spraychart = filtered_spraychart_df['Season'].unique().tolist()
    seasons_spraychart.sort(reverse=True)

    # Add components to the first column (wide view)
    with col1:

        if len(seasons_spraychart) == 1:
            season_spraychart = st.selectbox(
                label = structure[lang][4],
                options = seasons_spraychart,
                index = 0,
                placeholder = structure[lang][10],
                disabled=True
            )
        else:
            season_spraychart = st.selectbox(
                label = structure[lang][4],
                options = seasons_spraychart,
                index = 0,
                placeholder = structure[lang][10],
                disabled=False
            )

    filtered_spraychart_df_1 = filtered_spraychart_df.loc[filtered_spraychart_df['season'] == f'{season_spraychart}']

    # Create scatter plot
    col1, col2 = st.columns([1, 1])

    lefties = filtered_spraychart_df_1.loc[filtered_spraychart_df_1['matchup.batSide.code'] == 'L']
    # lefties = plot_data = pd.DataFrame({ 'coordinates.coordX': [ -20, 0 ], 'coordinates.coordY': [ 220, 0 ], 'result.eventType': [ 'single', 'double' ] })
    righties = filtered_spraychart_df_1.loc[filtered_spraychart_df_1['matchup.batSide.code'] == 'R']

    # st.write(lefties)

    with col1:
        show_spraychart(hit_colors, lefties, f'{players_df['player.fullName'][player]} vs {structure[lang][20]}', theme)

    with col2:
        show_spraychart(hit_colors, righties, f'{players_df['player.fullName'][player]} vs {structure[lang][21]}', theme)

else:

    seasons_list = team_stats_df['Season'].unique().tolist()
    seasons_list.sort(reverse=True)


    col1, col2 = st.columns([1, 6])

    with col1:

        if len(seasons_list) == 1:
            season_selected = st.selectbox(
                label = structure[lang][4],
                options = seasons_list,
                index = 0,
                placeholder = structure[lang][10],
                disabled=True
            )
        else:
            season_selected = st.selectbox(
                label = structure[lang][4],
                options = seasons_list,
                index = 0,
                placeholder = structure[lang][10],
                disabled=False
            )
            
    # st.write(pitching_df.loc[pitching_df['Season'] == season_selected])

    # show_df = pd.merge(players_df[['player.fullName']], pitching_df.loc[pitching_df['Season'] == season_selected], on='player.id', how='inner')
    # st.write(show_df[show_df['stat.inningsPitched_1'] < 56])

    filtered_colective_stats = team_stats_df.loc[team_stats_df['Season'] == season_selected].sort_values(by=['Season', 'ERA'], ascending=[True, True])

    standard_ = filtered_colective_stats[table_fields['pitching']['standard']]
    advanced_ = filtered_colective_stats[table_fields['pitching']['advanced']]
    battedBall_ = filtered_colective_stats[table_fields['pitching']['battedBall']]
    pitchedBall_ = filtered_colective_stats[table_fields['pitching']['advanced']]

    st.markdown('')
    st.subheader(structure[lang][14], divider="gray")
    # st.dataframe(standard_, hide_index = True, use_container_width=True)
    pitching_stats_formater(standard_)

    st.markdown('')
    st.subheader(structure[lang][15], divider="gray")
    # st.dataframe(advanced_, hide_index = False, use_container_width=True)
    pitching_stats_formater(advanced_)


    st.markdown('')
    st.subheader(structure[lang][16], divider="gray")
    # st.dataframe(battedBall_, hide_index = True, use_container_width=True)
    pitching_stats_formater(battedBall_)

    st.markdown('')
    st.subheader(structure[lang][17], divider="gray")
    # st.dataframe(pitchedBall_, hide_index = True, use_container_width=True)
    pitching_stats_formater(pitchedBall_)

share_bar = """        
    <style>
        
        .icon-bar {
            position: fixed;
            bottom: 10%;
            left: 93%;
            /*width: 100%;
            display: flex;*/
            justify-content: center;
            /*background-color: #333;
            z-index: 9999;*/
        }

        .icon-bar a {
            display: block;
            text-align: center;
            padding: 8px;
            transition: all 0.3s ease;
            color: white;
            font-size: 15px;
        }

        .icon-bar a:hover {
            background-color: #000;
        }

        .facebook {
            background: #3B5998;
            color: white;
        }

        .twitter {
            background: #55ACEE;
            color: white;
        }

        .google {
            background: #dd4b39;
            color: white;
        }

        .linkedin {
            background: #007bb5;
            color: white;
        }

        .whatsapp {
            background: #25d366;
            color: white;
        }

    </style>

""" + f"""

    <!-- Load font awesome icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

    <!-- The social media icon bar -->
    <div class="icon-bar">
        <a href="http://www.facebook.com/sharer.php?u={share_url}" class="facebook"><i class="fa fa-facebook"></i></a>
        <a href="https://x.com/intent/post?url={share_url}" class="twitter"><i class="fa fa-twitter"></i></a>
        <!-- <a href="#" class="google"><i class="fa fa-google"></i></a> -->
        <!-- <a href="#" class="linkedin"><i class="fa fa-linkedin"></i></a> -->
        <a href="https://api.whatsapp.com/send?text={share_url}" class="whatsapp"><i class="fa fa-whatsapp"></i></a>
    </div>            

"""

st.markdown(share_bar, unsafe_allow_html=True)

with st.expander("Glosario"):

    split = ( max(structure[lang]) - 100 ) / 3

    col1, col2, col3 = st.columns([1, 1, 1])
    for i in range( 101, max(structure[lang])):
        if i < 101 + split:
            with col1:
                structure[lang][i]
        elif i < 101 + ( split * 2 ):
            with col2:
                structure[lang][i]
        else:
            with col3:
                structure[lang][i]