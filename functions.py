import streamlit as st # type: ignore
import json
import urllib3 # type: ignore
import pandas as pd # type: ignore
import csv
import matplotlib.pyplot as plt # type: ignore

@st.cache_data
def players_breakdown(players_df):

    player_options = {}
    teams = {}

    players_df.set_index(['player.id'], inplace = True)

    for index, row in players_df.iterrows():
        player_options[index] = row['player.fullName']
        teams[row['team.id']] = { 'fullName': row['team.name'],  'abbreviation': row['team.abbreviation']}

    return player_options, teams

def show_spraychart(hit_colors, plot_data, title):
    fig, ax = plt.subplots()

    # Extract data for scatter plot
    x = plot_data['coordinates.coordX']
    y = plot_data['coordinates.coordY']
    # Check for event types not in the dictionary and tag them as 'out'
    event_types = plot_data['result.eventType'].apply(
        lambda x: x if x in hit_colors else 'out'
    )

    stadium_template = pd.read_csv('.\Static\stadium_2.csv')

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
            subset = plot_data[~plot_data['result.eventType'].isin(['single', 'double', 'triple', 'home_run', 'error'])]
        else:
            subset = plot_data[plot_data['result.eventType'] == event_type]

        ax.scatter(subset['coordinates.coordX'], subset['coordinates.coordY'], label=event_type.replace('_', ' ').title(), color=hit_colors.get(event_type, 'black'))


    # Add title and labels
    ax.set_title(title, color='white')

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

    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117') 

    # Add border to the plot
    fig.patch.set_edgecolor('#8CB5CB')
    fig.patch.set_linewidth(2)

    # Display plot in Streamlit
    st.pyplot(fig)
