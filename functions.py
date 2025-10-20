import streamlit as st # type: ignore
import json
import urllib3 # type: ignore
import pandas as pd # type: ignore
import csv
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns
import requests
from bs4 import BeautifulSoup

def get_headshot_url(player_id, web):
    try:
        url = f"https://www.{web}.com/player/{player_id}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'https://www.{web}.com',
            'Accept-Language': 'en-US,en;q=0.9'
        }

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = soup.find('img', {'class': 'player-headshot'})

            if img_tag:
                return img_tag['src']

        else:
            print(f"Failed to retrieve page for player {player_id}: Status code {response.status_code}")

    except requests. RequestException as e:
        print(f"Error fetching (player_id): {e}")
        return None

@st.cache_data
def players_breakdown(players_df):

    player_options = {}
    teams = {}

    players_df.set_index(['player.id'], inplace = True)

    for index, row in players_df.iterrows():
        player_options[index] = row['player.fullName']
        teams[row['team.id']] = { 'fullName': row['team.name'],  'abbreviation': row['team.abbreviation']}

    return player_options, teams


@st.cache_data
def pitching_stats_format(stats):

    stats['ERA'] =  round( stats['ERA'] , 2 )
    stats['IP'] =  round( stats['IP'] , 1 )
    stats['WHIP'] = round( stats['WHIP'] , 2 )
    stats['AVG'] = round( stats['AVG'] , 3 )
    stats['K/9'] = round( stats['K/9'] , 2 )
    stats['BB/9'] = round( stats['BB/9'] , 2 )
    stats['HR/9'] = round( stats['HR/9'] , 2 )
    stats['K/BB'] = round( stats['K/BB'] , 2 )
    stats['K%'] = round( stats['K%'] , 1 )
    stats['BB%'] = round(stats['BB%'] , 1 )
    stats['K-BB%'] = round( stats['K-BB%'] , 1 )

    stats['BABIP'] = round( stats['BABIP'] , 3 )
    stats['LOB%'] = round( stats['LOB%'] , 1 )
    stats['FIP'] = round( stats['FIP'] , 2 )
    stats['xFIP'] = round( stats['xFIP'] , 2 )
    stats['SIERA'] = round( stats['SIERA'] , 2 )
    stats['ERA-FIP'] = round( stats['ERA-FIP'] , 2 )

    stats['ERA+'] = round( stats['ERA+'] , 0 )
    stats['FIP+'] = round( stats['FIP+'] , 0 )
    stats['xFIP+'] = round( stats['xFIP+'] , 0 )
    stats['SIERA+'] = round( stats['SIERA+'] , 0 )

    stats['GB/FB'] = round( stats['GB/FB'] , 2 )
    stats['LD%'] = round( stats['LD%'] , 1 )
    stats['GB%'] = round( stats['GB%'] , 1 )
    stats['FB%'] = round( stats['FB%'] , 1 )
    stats['PU%'] = round( stats['PU%'] , 1 )
    stats['HR/FB'] = round( stats['HR/FB'] , 2 )
    stats['P/IP'] = round( stats['P/IP'] , 2 )
    stats['Strike%'] = round( stats['Strike%'] , 1 )
    stats['Ball%'] = round( stats['Ball%'] , 1 )
    stats['Whiff%'] = round( stats['Whiff%'] , 1 )
    stats['SwStr%'] = round( stats['SwStr%'] , 1 )
    stats['CStr%'] = round( stats['CStr%'] , 1 )
    stats['CSW%'] = round( stats['CSW%'] , 1 )

    stats['WPA'] = round( stats['WPA'] , 3 )
    stats['-WPA'] = round( stats['-WPA'] , 3 )
    stats['+WPA'] = round( stats['+WPA'] , 3 )
    stats['pLI'] = round( stats['pLI'] , 2 )
    stats['inLI'] = round( stats['inLI'] , 2 )
    stats['gmLI'] = round( stats['gmLI'] , 2 )
    stats['exLI'] = round( stats['exLI'] , 2 )
    stats['Pulls'] = round( stats['Pulls'] , 0 )
    stats['WPA/LI'] = round( stats['WPA/LI'] , 3 )
    stats['Clutch'] = round( stats['Clutch'] , 3 )
    stats['SD'] = round( stats['SD'] , 0 )
    stats['MD'] = round( stats['MD'] , 0 )

    return stats

@st.cache_data
def pitching_stats_formater(stats):

    # Define custom formatting function
    def custom_format(value):
        return f'{value:.3f}'.lstrip('0')

    styled_df = stats.style.format({
        'ERA': '{:.2f}',
        'IP': '{:.1f}',
        'WHIP': '{:.2f}',
        'AVG': custom_format,
        'K/9': '{:.2f}',
        'BB/9': '{:.2f}',
        'HR/9': '{:.2f}',
        'K/BB': '{:.2f}',
        'K%': '{:.1f}',
        'BB%': '{:.1f}',
        'K-BB%': '{:.1f}',
        'BABIP': custom_format,
        'LOB%': '{:.1f}',
        'FIP': '{:.2f}',
        'xFIP': '{:.2f}',
        'SIERA': '{:.2f}',
        'ERA-FIP': '{:.2f}',
        'ERA+': '{:.0f}',
        'FIP+': '{:.0f}',
        'xFIP+': '{:.0f}',
        'SIERA+': '{:.0f}',
        'GB/FB': '{:.2f}',
        'LD%': '{:.1f}',
        'GB%': '{:.1f}',
        'FB%': '{:.1f}',
        'PU%': '{:.1f}',
        'HR/FB': '{:.2f}',
        'P/IP': '{:.2f}',
        'Strike%': '{:.1f}',
        'Ball%': '{:.1f}',
        'Whiff%': '{:.1f}',
        'SwStr%': '{:.1f}',
        'CStr%': '{:.1f}',
        'CSW%': '{:.1f}',
        'WPA': '{:.3f}',
        '-WPA': '{:.3f}',
        '+WPA': '{:.3f}',
        'pLI': '{:.2f}',
        'inLI': '{:.2f}',
        'gmLI': '{:.2f}',
        'exLI': '{:.2f}',
        'Pulls': '{:.0f}',
        'WPA/LI': '{:.3f}',
        'Clutch': '{:.3f}',
        'SD': '{:.0f}',
        'MD': '{:.0f}'
    })

    st.dataframe(styled_df, hide_index = True, width='stretch')


def show_spraychart(hit_colors, plot_data, title, theme):
    fig, ax = plt.subplots()

    # Extract data for scatter plot
    x = plot_data['coordinates.coordX']
    y = plot_data['coordinates.coordY']
    # Check for event types not in the dictionary and tag them as 'out'
    event_types = plot_data['result.eventType'].apply(
        lambda x: x if x in hit_colors else 'out'
    )

    stadium_template = pd.read_csv('./Static/stadium_2.csv')

    y_offset = 275
    excluded_segments = ['outfield_inner']
    for segment_name in stadium_template['segment'].unique():
        if segment_name not in excluded_segments:
            segment_data = stadium_template[stadium_template['segment'] == segment_name]
            plt.plot(segment_data['x'], segment_data['y'], linewidth=2, zorder=1, color='#8CB5CB', alpha=0.5)

    # Plot each event type with a different color
    for event_type in event_types.unique():
        if event_type == 'out':
            # subset = lefties[lefties['result.eventType'] == event_type]
            subset = plot_data[~plot_data['result.eventType'].isin(['single', 'double', 'triple', 'home_run', 'field_error'])]
        else:
            subset = plot_data[plot_data['result.eventType'] == event_type]
    
        ax.scatter(
            subset['coordinates.coordX'], 
            subset['coordinates.coordY'], 
            label=event_type.replace('field_', '').replace('_', ' ').title(), 
            color=hit_colors.get(event_type, 'black'), 
            edgecolors='black'
        )

    # Add title and labels
    ax.set_title(title, color=theme['textColor'])

    # Hide axes
    ax.axis('off')

    plt.xlim(-20, 280)
    plt.ylim(0, 220)

    # Invert y-axis to make (0,0) start at the top left
    ax.invert_yaxis()

    # Add legend with specific order
    handles, labels = ax.get_legend_handles_labels()
    order = ['Single', 'Double', 'Triple', 'Home Run', 'Out', 'Error']
    ordered_handles = [handles[labels.index(event)] for event in order if event in labels]
    ordered_labels = [event for event in order if event in labels]
    ax.legend(ordered_handles, ordered_labels, title='Event Type')

    fig.patch.set_facecolor(theme['backgroundColor'])
    ax.set_facecolor(theme['backgroundColor']) 

    # Add border to the plot
    fig.patch.set_edgecolor('#8CB5CB')
    fig.patch.set_linewidth(2)

    # Display plot in Streamlit
    st.pyplot(fig)

#def show_heatmap(plot_data, title, theme):