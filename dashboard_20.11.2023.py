# File to build dashboard using streamlite

import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import plotly.express as px

def display_title():
    # Create a title for the dashboard
    st.title('Events in Stuttgart 📅 🎉')

    # Create a subheader
    st.subheader('A dashboard to explore great places in Stuttgart on Wednesdays!')

# the user should have multiple options to choose from
# - The season (soring, summer, autumn, winter)
# - The type of event (concert, party, singer in a bar, ...)
# - The location (größeren Viertel von Stuttgart zur Auswahl stellen (durch ZIP Code) )

def get_user_preferences():
    # Create a multiselect widget for the type of event
    event_type = st.sidebar.multiselect(
        'Which type of event do you prefer?',
        ['konzert', 'kultur', 'stadtleben', 'party', 'familie'],
        ['konzert', 'party']
    )

    # Create a multiselect widget for the location
    location_sidebar = st.sidebar.multiselect(
        'Which part of Stuttgart do you prefer?',
        ["Europaviertel","Relenberg","Karlshöhe","Am Rosensteinpark","Kräherwald","Botnang-West","Vogelsang","Südheim","Bad Cannstatt","Sternhäule","Pfaffenwald","Freiberg","Rosenberg","Uhlandshöhe","Im Geiger","Zuffenhausen-Elbelen","Stöckach","Weinsteige","Heusteigviertel","Neckarvorstadt","Mönchfeld","Waldau","Möhringen-Süd","Feuerbach-Ost","Südheim"],
        ["Europaviertel","Relenberg","Karlshöhe","Am Rosensteinpark"],
    )

    # Create a multiselect widget for the season
    season = st.sidebar.multiselect(
        'In what season are you looking for an event?',
        ['spring', 'summer', 'autumn', 'winter'],
        ['spring', 'summer', 'autumn', 'winter']
    )

    preferred_time = st.sidebar.radio("Select your preferred time:", ["Morning", "Afternoon", "Evening", "Night", "I don't have time :("])

    return event_type, location_sidebar, season, preferred_time

    


def create_link_to_GoogleMaps(row):
    google_maps_address = f"https://www.google.com/maps/search/?api=1&query={row['Address']}, Stuttgart"
    return f'<a href="{google_maps_address}" target="_blank">Find {row["Address"]} on Maps</a>'

def prepare_sub_df_for_output(df: pd.DataFrame, top5: bool, event_type: list, location_sidebar: list, season: list, preferred_time: str):
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


def display_locations(df: pd.DataFrame, selected_tab: str, event_type, location_sidebar, season, preferred_time):
    if selected_tab == "Top 5 Locations":
        st.subheader('Top 5 Locations for your preferences🚀')
        output_df = prepare_sub_df_for_output(df, top5=True, event_type=event_type, location_sidebar=location_sidebar, season=season, preferred_time=preferred_time)
        st.write(output_df.to_html(escape=False, index=False, justify='center'), unsafe_allow_html=True)

    elif selected_tab == "All Locations":
        st.subheader('All locations that correspond to your preferences')
        output_df = prepare_sub_df_for_output(df, top5=False, event_type=event_type, location_sidebar=location_sidebar, season=season, preferred_time=preferred_time)
        st.write(output_df.to_html(escape=False, index=False, justify='center'), unsafe_allow_html=True)

def show_no_of_events_used(df: pd.DataFrame):
    st.markdown('&nbsp;')
    num_events = len(df)
    # Display the number of events in a visually appealing way
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; border-top: 3px solid #ddd; align-items: flex-end;">
            <div style="text-align: left; font-size: 36px; color: #4CAF50; transform: rotate(90deg); margin-bottom: 70px;">
                #Wednesdays
            </div>
            <div style="text-align: center; font-size: 120px; color: #ff6347; padding-top: 10px;">
                {num_events}
                <div style="font-size: 24px; color: #808080; margin-top: 10px;">Events Used for Training</div>
            </div>
            <div style="text-align: right; font-size: 36px; color: #4CAF50; transform: rotate(-90deg); margin-bottom: 70px;">
                Stuttgart
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Create a frame to visually separate sections
    st.markdown('<hr style="border: 2px solid #ddd;">', unsafe_allow_html=True)


def show_google_maps_stuttgart():
   
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

def display_wordcloud_with_colnames(df: pd.DataFrame):
    st.markdown('&nbsp;')
    # Assuming df is your DataFrame
    df = df
    # List of columns created by feature engineering
    feature_engineering_cols = ['dayofweek', 'year', 'month', 'season', 'district', 'supercategory', 'subcategory', 'starting_hour']
    # Display a title
    st.text('Columns used for creating dashboard:')
    # Create a frame for all columns
    st.markdown('<div style="border: 2px solid #ddd; padding: 10px; border-radius: 10px;">', unsafe_allow_html=True)
    # Display all columns
    st.text('All Columns:')
    st.text(', '.join(df.columns))
    # Close the frame for all columns
    st.markdown('</div>', unsafe_allow_html=True)
    # Create a frame for feature engineering columns with a different color
    st.markdown('<div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 10px; margin-top: 20px;">', unsafe_allow_html=True)
    # Display feature engineering columns
    st.text('Feature Engineering Columns:')
    st.text(', '.join(feature_engineering_cols))
    # Close the frame for feature engineering columns
    st.markdown('</div>', unsafe_allow_html=True)

def dislpay_frequent_words_from_description(df: pd.DataFrame):
    # download german stopwords
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')

    st.markdown('&nbsp;')
    st.title('Wordcloud of event descriptions')
    # Assuming df is your DataFrame
    df = df
    # Concatenate all text from the specified column
    text_data = ' '.join(df['eventData.description'].dropna())
    # Tokenize the text
    tokens = word_tokenize(text_data)
    # Remove stopwords
    german_stopwords = set(stopwords.words('german'))
    custom_stopwords = {"br", "href", "s", "u", "S"}
    german_stopwords.update(custom_stopwords)
    filtered_tokens = [word.lower() for word in tokens if word.lower() not in german_stopwords]
    # Join the filtered tokens back into text
    filtered_text = ' '.join(filtered_tokens)
    # Generate a word cloud with German stopwords filtered out
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(filtered_text)
    # Display the word cloud using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    # Display the figure in Streamlit
    st.pyplot(fig)

# Diagramm
def generate_activity_type_chart(df: pd.DataFrame):
    st.markdown("&nbsp;")
    st.title("Activity Type Distribution 📊")

    # Zahlen rechnen
    activity_counts = df['supercategory'].value_counts()

    # Diagramm malen
    fig, ax = plt.subplots()
    activity_counts.plot(kind='bar', ax=ax)
    ax.set_xlabel('Activity Type')
    ax.set_ylabel('Number of Events')
    ax.set_title('Distribution of Activity Types')

    # Diagramm zeigen
    st.pyplot(fig)

# Diagramm_Kreis
def generate_activity_type_pie_chart(df: pd.DataFrame):
    st.markdown("&nbsp;")
    st.title("Activity Type Distribution 📊")

    # Rechnen
    activity_counts = df['supercategory'].value_counts()

    # plotly.express
    fig = px.pie(activity_counts, values=activity_counts, names=activity_counts.index, title='Distribution of Activity Types')

    # Zeigen
    st.plotly_chart(fig)

# Diagramm_Month
def generate_activity_time_chart(df: pd.DataFrame):
    st.markdown("&nbsp;")
    st.title("Activity Time Distribution 📊")

    # Month
    activity_time_counts = df['month'].value_counts()

    # plotly.express
    fig = px.bar(activity_time_counts, x=activity_time_counts.index, y=activity_time_counts.values, 
                 labels={'x': 'month', 'y': 'Number of Events'},
                 title='Distribution of Activity Times')

    # Zeigen
    st.plotly_chart(fig)

def main():
    # Read in the csv-file
    df = pd.read_csv('data/1000Events.csv', index_col=False)
    print(df)
    display_title()
    event_type, location_sidebar, season, preferred_time = get_user_preferences()
    st.write('We will analyze your preferences and show you our recommendations for matching locations in Stuttgart.')
    selected_tab = st.selectbox("Choose top location or all locations", ["Top 5 Locations", "All Locations"])
    display_locations(df, selected_tab, event_type, location_sidebar, season, preferred_time)
    show_no_of_events_used(df)
    show_google_maps_stuttgart()
    display_wordcloud_with_colnames(df)
    dislpay_frequent_words_from_description(df)

    generate_activity_type_chart(df)
    generate_activity_type_pie_chart(df)
    generate_activity_time_chart(df)

    st.markdown('&nbsp;')
    st.markdown('<div style="text-align:center;">Copyright © 2023 Julius Döbelt and Haoran Huang. All rights reserved.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
