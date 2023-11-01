# File to build dashboard using streamlite

import streamlit as st
import pandas as pd
import numpy as np

# Read in the csv-file
df = pd.read_csv('data/1000Events.csv', index_col=False)

# Create a title for the dashboard
st.title('Events in Stuttgart 📅 🎉')

# Create a subheader
st.subheader('A dashboard to explore great places in Stuttgart on Wednesdays!')

# the user should have multiple options to choose from
# - The season (soring, summer, autumn, winter)
# - The type of event (concert, party, singer in a bar, ...)
# - The location (größeren Viertel von Stuttgart zur Auswahl stellen (durch ZIP Code) )


# Create a multiselect widget for the type of event
event_type = st.sidebar.multiselect(
    'Which type of event do you prefer?',
    ['konzert', 'kultur', 'stadtleben', 'party', 'familie'],
    ['konzert', 'kultur', 'stadtleben', 'party', 'familie']
)

# Create a multiselect widget for the location
location_sidebar = st.sidebar.multiselect(
    'Which part of Stuttgart do you prefer?',
    ["Europaviertel","Relenberg","Karlshöhe","Am Rosensteinpark","Kräherwald","Botnang-West","Vogelsang","Südheim","Bad Cannstatt","Sternhäule","Pfaffenwald","Freiberg","Rosenberg","Uhlandshöhe","Im Geiger","Zuffenhausen-Elbelen","Stöckach","Weinsteige","Heusteigviertel","Neckarvorstadt","Mönchfeld","Waldau","Möhringen-Süd","Feuerbach-Ost","Südheim"],
    ["Europaviertel","Relenberg","Karlshöhe","Am Rosensteinpark","Kräherwald","Botnang-West","Vogelsang","Südheim","Bad Cannstatt","Sternhäule","Pfaffenwald","Freiberg","Rosenberg","Uhlandshöhe","Im Geiger","Zuffenhausen-Elbelen","Stöckach","Weinsteige","Heusteigviertel","Neckarvorstadt","Mönchfeld","Waldau","Möhringen-Süd","Feuerbach-Ost","Südheim"],
)

# Create a multiselect widget for the season
season = st.sidebar.multiselect(
    'In what season are you looking for an event?',
    ['spring', 'summer', 'autumn', 'winter'],
    ['spring', 'summer', 'autumn', 'winter']
)

# build website 
st.write('We will analyze your preferences and show you our recommendations for matching locations in Stuttgart.')

def create_link_to_GoogleMaps(row):
    google_maps_address = f"https://www.google.com/maps/search/?api=1&query={row['Address']}, Stuttgart"
    return f'<a href="{google_maps_address}" target="_blank">Find {row["Address"]} on Maps</a>'

def prepare_sub_df_for_output(df: pd.DataFrame, top5: bool):
    sub_df = df[df['season'].isin(season) & df['district'].isin(location_sidebar) & df['supercategory'].isin(event_type)]
    # Only select the relevant columns
    sub_df = sub_df[['eventData.name', 'eventData.description', 'eventData.location.name', 'eventData.location.location.address.street', 'supercategory', 'subcategory']]
    sub_df.columns = ['Event', 'Description', 'Location', 'Address', 'Type', 'Category']
    # create a dictionary with the location as key and the address and category as values
    location_dict = {}
    for index, row in sub_df.iterrows():
        if row['Location'] not in location_dict:
            location_dict[row['Location']] = [row['Address'], row['Type'], 1]
        else:
            location_dict[row['Location']][2] += 1 if location_dict[row['Location']][2] < 5 else 0
    # count number of events per location
    events_per_location_count_df = sub_df.groupby(['Location']).count()
    # sort by number of events per location
    events_per_location_count_df = events_per_location_count_df.sort_values(by=['Event'], ascending=False)

    if top5 == True:
        # get the top 5 location names
        top_5_locations = events_per_location_count_df.head(5).index.tolist()
        # create a new dataframe with only the top 5 locations using the location_dict
        top_5_locations_df = pd.DataFrame(columns=['Location', 'Address', 'Type', 'Popularity'])
        for location in top_5_locations:
            star_rating = location_dict[location][2]*'⭐'
            new_entry = pd.DataFrame([[location, location_dict[location][0], location_dict[location][1], star_rating]], columns=['Location', 'Address', 'Type', 'Popularity'])
            top_5_locations_df = pd.concat([top_5_locations_df, new_entry])
        top_5_locations = top_5_locations_df.reset_index(drop=True)
        top_5_locations['Google Maps Link 📍🗺️'] = top_5_locations.apply(create_link_to_GoogleMaps, axis=1)
        return top_5_locations
    else:
        # get all location names
        all_locations = events_per_location_count_df.index.tolist()
        # create new df with all locations using the location_dict
        all_locations_df = pd.DataFrame(columns=['Location', 'Address', 'Type', 'Popularity'])
        for location in all_locations:
            star_rating = location_dict[location][2]*'⭐'
            new_entry = pd.DataFrame([[location, location_dict[location][0], location_dict[location][1], star_rating]], columns=['Location', 'Address', 'Type', 'Popularity'])
            all_locations_df = pd.concat([all_locations_df, new_entry])
        all_locations = all_locations_df.reset_index(drop=True)
        all_locations['Google Maps Link 📍🗺️'] = all_locations.apply(create_link_to_GoogleMaps, axis=1)
        return all_locations

selected_tab = st.selectbox("Choose top location or all locations", ["Top 5 Locations", "All Locations"])

if selected_tab == "Top 5 Locations":
    st.subheader('Top 5 Locations for your preferences🚀')
    output_df = prepare_sub_df_for_output(df, top5=True)
    st.write(output_df.to_html(escape=False, index=False, justify='center'), unsafe_allow_html=True)

    st.markdown('&nbsp;')
    st.write('When you are from outside of Stuttgart, you can find the best way to get to Stuttgart here:')
    # Google Maps iframe code 
    google_maps_iframe = """
    <iframe
    width="600"
    height="450"
    frameborder="0"
    style="border:0"
    src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d194810.4263677699!2d9.073201596210784!3d48.7758451766426!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4799c00fb81e49cf%3A0x66ba215d16b9970c!2sStuttgart!5e0!3m2!1sen!2sus!4v1633772401089!5m2!1sen!2sus"
    allowfullscreen
    ></iframe>
    """
    # Display the Google Maps iframe in Streamlit
    st.markdown(google_maps_iframe, unsafe_allow_html=True)

elif selected_tab == "All Locations":
    st.subheader('All locations that correspond to your preferences')
    output_df = prepare_sub_df_for_output(df, top5=False)
    st.write(output_df.to_html(escape=False, index=False, justify='center'), unsafe_allow_html=True)

st.markdown('&nbsp;')
st.markdown('<div style="text-align:center;">Copyright © 2023 Julius Döbelt and Haoran Huang. All rights reserved.</div>', unsafe_allow_html=True)