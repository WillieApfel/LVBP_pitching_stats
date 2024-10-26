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


@st.cache_data
def pitching_stats_format(stats):

    stats['ERA'] =  round( stats['ERA'] , 2 ).apply(lambda x: f'{x:.2f}')
    stats['WHIP'] = round( stats['WHIP'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['AVG'] = round( stats['AVG'] , 3 ).apply(lambda x: f"{x:.3f}".lstrip('0'))
    stats['K/9'] = round( stats['K/9'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['BB/9'] = round( stats['BB/9'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['HR/9'] = round( stats['HR/9'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['K/BB'] = round( stats['K/BB'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['K%'] = round( stats['K%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['BB%'] = round(stats['BB%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['K-BB%'] = round( stats['K-BB%'] , 1 ).apply(lambda x: f"{x:.1f}")

    stats['BABIP'] = round( stats['BABIP'] , 2 ).apply(lambda x: f"{x:.3f}".lstrip('0'))
    stats['LOB%'] = round( stats['LOB%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['FIP'] = round( stats['FIP'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['xFIP'] = round( stats['xFIP'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['SIERA'] = round( stats['SIERA'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['ERA-FIP'] = round( stats['ERA-FIP'] , 2 ).apply(lambda x: f"{x:.2f}")

    stats['ERA+'] = round( stats['ERA+'] , 0 ).apply(lambda x: f"{x:.0f}")
    stats['FIP+'] = round( stats['FIP+'] , 0 ).apply(lambda x: f"{x:.0f}")
    stats['xFIP+'] = round( stats['xFIP+'] , 0 ).apply(lambda x: f"{x:.0f}")
    stats['SIERA+'] = round( stats['SIERA+'] , 0 ).apply(lambda x: f"{x:.0f}")

    stats['GB/FB'] = round( stats['GB/FB'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['LD%'] = round( stats['LD%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['GB%'] = round( stats['GB%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['FB%'] = round( stats['FB%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['PU%'] = round( stats['PU%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['HR/FB'] = round( stats['HR/FB'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['P/IP'] = round( stats['P/IP'] , 2 ).apply(lambda x: f"{x:.2f}")
    stats['Strike%'] = round( stats['Strike%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['Ball%'] = round( stats['Ball%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['Whiff%'] = round( stats['Whiff%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['SwStr%'] = round( stats['SwStr%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['CStr%'] = round( stats['CStr%'] , 1 ).apply(lambda x: f"{x:.1f}")
    stats['CSW%'] = round( stats['CSW%'] , 1 ).apply(lambda x: f"{x:.1f}")

    stats['WPA'] = round( stats['WPA'] , 3 ).apply(lambda x: f"{x:.3f}")
    stats['-WPA'] = round( stats['-WPA'] , 3 ).apply(lambda x: f"{x:.3f}")
    stats['+WPA'] = round( stats['+WPA'] , 3 ).apply(lambda x: f"{x:.3f}")

    return stats

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
