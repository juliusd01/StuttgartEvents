# File to build dashboard using streamlite

import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import plotly.express as px
import statistics

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
    st.sidebar.title("Dashboard Controls")
    # Create a multiselect widget for the location
    location_sidebar = st.sidebar.multiselect(
        'Which part of Stuttgart do you prefer?',
        ["Europaviertel","Relenberg","Karlshöhe","Am Rosensteinpark","Kräherwald","Botnang-West","Vogelsang","Südheim","Bad Cannstatt","Sternhäule","Pfaffenwald","Freiberg","Rosenberg","Uhlandshöhe","Im Geiger","Zuffenhausen-Elbelen","Stöckach","Weinsteige","Heusteigviertel","Neckarvorstadt","Mönchfeld","Waldau","Möhringen-Süd","Feuerbach-Ost","Südheim", "Other"],
        ["Europaviertel","Relenberg","Karlshöhe","Am Rosensteinpark","Kräherwald","Botnang-West","Vogelsang","Südheim","Bad Cannstatt","Sternhäule","Pfaffenwald","Freiberg","Rosenberg","Uhlandshöhe","Im Geiger","Zuffenhausen-Elbelen","Stöckach","Weinsteige","Heusteigviertel","Neckarvorstadt","Mönchfeld","Waldau","Möhringen-Süd","Feuerbach-Ost","Südheim", "Other"],
    )

    # Create a multiselect widget for the season
    season = st.sidebar.multiselect(
        'In what season are you looking for an event?',
        ['spring', 'summer', 'autumn', 'winter'],
        ['spring', 'summer', 'autumn', 'winter']
    )

    # Create a multiselect widget for the mood
    mood = st.sidebar.multiselect(
        'What should be the flair of the event?',
        ['Musikalisch', 'Informativ', 'Entspannt', 'Feierlich', 'Energiegeladen'],
        ['Musikalisch', 'Informativ', 'Entspannt', 'Feierlich', 'Energiegeladen']
    )

    # Create a multiselect widget for the type of event
    event_type = st.sidebar.multiselect(
        'Which type of event do you prefer?',
        ["restaurant", "kultur", "party", "performance & event venue", "public figure", "dance & night club", "bar", "anderes", "church", "university", "performance art theatre", "local business", "club", "arts", "library", "museum", "education", "business services", "government organization", "arts & entertainment", "non-profit organization", "community organization", "bookstore", "non-governmental organization (ngo)", "company", "sports"],
        []
    )

    return event_type, location_sidebar, season, mood


def display_subcategories(event_types: list, df: pd.DataFrame, default_value='No Subcategory'):
    subcategories = []
    for event_type in event_types:
        subcategory = df[df['supercategory'] == event_type]['subcategory'].unique()
        # remove nan from subcategories
        subcategory = subcategory[~pd.isnull(subcategory)]
        subcategories.extend(subcategory)
    # If there are no subcategories, use the default value
    if not subcategories:
        subcategories = [default_value]
    print(subcategories)
    # Create a multiselect widget for the subtype of event
    event_subtype = st.sidebar.multiselect(
        'Which genre of event do you prefer?',
        subcategories,
        []
    )
    return event_subtype


def create_link_to_GoogleMaps(row):
    google_maps_address = f"https://www.google.com/maps/search/?api=1&query={row['Location']},{row['Address']}, Stuttgart"
    return f'<a href="{google_maps_address}" target="_blank">Find {row["Location"]} on Maps</a>'

def prepare_sub_df_for_output(df: pd.DataFrame, top5: bool, event_type: list, location_sidebar: list, season: list, event_subtype: list, mood: list):
    """ Select the data from the dataframe that corresponds to the user preferences and return a dataframe with the relevant data
    
    :param df: the dataframe with all the events
    :param top5: boolean to indicate if only the top 5 locations should be returned
    :param event_type: list of event types
    :param location_sidebar: list of district names that the user selected
    :param season: list of seasons that the user selected
    :param event_subtype: list of event subtypes that the user selected
    :param mood: list of moods that the user selected
    """
    sub_df = df[df['season'].isin(season) & df['district'].isin(location_sidebar) & df['supercategory'].isin(event_type) & (df['subcategory'].isin(event_subtype) | (df['subcategory'] == "")) & df['stimmung'].isin(mood)]
    # Only select the relevant columns
    sub_df = sub_df[['name', 'description', 'location.name', 'location.location.address.street', 'supercategory', 'subcategory', 'stimmung']]
    sub_df.columns = ['Event', 'Description', 'Location', 'Address', 'Type', 'Category', 'Flair']
    # create a dictionary with the location as key and the address and category as values
    location_dict = {}
    for index, row in sub_df.iterrows():
        if row['Location'] not in location_dict:
            location_dict[row['Location']] = [row['Address'], [row['Type']], [row['Category']], [row['Flair']], 1]
        else:
            location_dict[row['Location']][3].append(row['Flair'])
            location_dict[row['Location']][2].append(row['Category'])
            location_dict[row['Location']][1].append(row['Type'])
            location_dict[row['Location']][4] += 1

    # After creating the dictionary, find the most common flair, type and category for each location. This will be displayed in the dashboard
    for location in location_dict:
        location_dict[location][3] = statistics.mode(location_dict[location][3])
        location_dict[location][2] = statistics.mode(location_dict[location][2])
        location_dict[location][1] = statistics.mode(location_dict[location][1])
    # count number of events per location
    events_per_location_count_df = sub_df.groupby(['Location']).count()
    # sort by number of events per location
    events_per_location_count_df = events_per_location_count_df.sort_values(by=['Event'], ascending=False)
    # calculate average number of events per location
    if top5 == True:
        # get the top 5 location names
        top_5_locations = events_per_location_count_df.head(5).index.tolist()
        # create a new dataframe with only the top 5 locations using the location_dict
        top_5_locations_df = pd.DataFrame(columns=['Location', 'Address', 'Type', 'Category', 'Flair', 'Popularity'])
        for location in top_5_locations:
            star_rating = min(location_dict[location][4], 5)
            num_of_events = location_dict[location][4]
            new_entry = pd.DataFrame([[location, location_dict[location][0], location_dict[location][1], location_dict[location][2], location_dict[location][3], star_rating*'⭐', num_of_events]], columns=['Location', 'Address', 'Type', 'Category', 'Flair', 'Popularity', 'Number of Events'])
            top_5_locations_df = pd.concat([top_5_locations_df, new_entry])
        top_5_locations = top_5_locations_df.reset_index(drop=True)
        top_5_locations['Google Maps Link 📍🗺️'] = top_5_locations.apply(create_link_to_GoogleMaps, axis=1)
        return top_5_locations
    else:
        # get all location names
        all_locations = events_per_location_count_df.index.tolist()
        # create new df with all locations using the location_dict
        all_locations_df = pd.DataFrame(columns=['Location', 'Address', 'Type', 'Category', 'Flair', 'Popularity'])
        for location in all_locations:
            star_rating = min(location_dict[location][4], 5)
            num_of_events = location_dict[location][4]
            new_entry = pd.DataFrame([[location, location_dict[location][0], location_dict[location][1], location_dict[location][2], location_dict[location][3], star_rating*'⭐', num_of_events]], columns=['Location', 'Address', 'Type', 'Category', 'Flair', 'Popularity', 'Number of Events'])
            all_locations_df = pd.concat([all_locations_df, new_entry])
        all_locations = all_locations_df.reset_index(drop=True)
        all_locations['Google Maps Link 📍🗺️'] = all_locations.apply(create_link_to_GoogleMaps, axis=1)
        return all_locations


def display_locations(df: pd.DataFrame, selected_tab: str, event_type, location_sidebar, season, event_subtype, mood):
    if selected_tab == "Top 5 Locations":
        st.subheader('Top 5 Locations for your preferences🚀')
        output_df = prepare_sub_df_for_output(df, top5=True, event_type=event_type, location_sidebar=location_sidebar, season=season, event_subtype=event_subtype, mood=mood)
        st.write(output_df.to_html(escape=False, index=False, justify='center'), unsafe_allow_html=True)

    elif selected_tab == "All Locations":
        st.subheader('All locations that correspond to your preferences')
        output_df = prepare_sub_df_for_output(df, top5=False, event_type=event_type, location_sidebar=location_sidebar, season=season, event_subtype=event_subtype, mood=mood)
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

def display_colnames(df: pd.DataFrame):
    st.markdown('&nbsp;')
    # Assuming df is your DataFrame
    df = df
    # List of columns created by feature engineering
    feature_engineering_cols = ['dayofweek', 'year', 'month', 'season', 'district', 'supercategory', 'subcategory', 'starting_hour', 'time_of_day']
    # Display a title
    st.title('Columns used for creating dashboard:')
    # Create a frame for all columns
    st.markdown('<div style="border: 2px solid #ddd; padding: 10px; border-radius: 10px;">', unsafe_allow_html=True)
    # Display all columns
    st.text('All Columns:')
    st.write(', '.join(df.columns))
    # Close the frame for all columns
    st.markdown('</div>', unsafe_allow_html=True)
    # Create a frame for feature engineering columns with a different color
    st.markdown('<div style="border: 2px solid #4CAF50; padding: 10px; border-radius: 10px; margin-top: 20px;">', unsafe_allow_html=True)
    # Display feature engineering columns
    st.text('Feature Engineering Columns:')
    st.write(', '.join(feature_engineering_cols))
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
    text_data = ' '.join(df['description'].dropna())
    # Tokenize the text
    tokens = word_tokenize(text_data)
    # Remove stopwords
    german_stopwords = set(stopwords.words('german'))
    custom_stopwords = {"br", "href", "s", "u", "S", "https", "de", "nofollow", "rel"}
    german_stopwords = german_stopwords.union(custom_stopwords)
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
    st.markdown('NOTE: The above wordcloud was created using natural language processing (NLP) techniques. The wordcloud is based on the event descriptions of the events in the dataset.', help='You need help understanding the wordcloud? Ask the developers!')

# Diagramm
def generate_activity_type_chart(df: pd.DataFrame):
    st.markdown("&nbsp;")
    st.title("Events by Category 💃🏼")

    # Zahlen rechnen
    activity_counts = df['supercategory'].value_counts()

    # only plot the top 10 categories
    activity_counts = activity_counts[:10]
    # plotly.express
    fig = px.bar(
        x=activity_counts.index,
        y=activity_counts.values,
        labels={'x': 'Activity Type', 'y': 'Number of Events'},
        title='Distribution of Activity Types'
    )

    # Diagramm zeigen
    st.plotly_chart(fig)

# Diagramm_Kreis
def generate_activity_type_pie_chart(df: pd.DataFrame):
    st.markdown("&nbsp;")
    st.title("Percentage of Events by Category")
    # Rechnen
    activity_counts = df['supercategory'].value_counts()

    # plotly.express
    fig = px.pie(activity_counts, values=activity_counts, names=activity_counts.index, title='Distribution of Activity Types')

    # Zeigen
    st.plotly_chart(fig)

# Diagramm_Month
def generate_activity_time_chart(df: pd.DataFrame):
    st.markdown("&nbsp;")
    st.title("Events by Month 📅")

    # Month
    activity_time_counts = df['month'].value_counts()

    # plotly.express
    fig = px.bar(activity_time_counts, x=activity_time_counts.index, y=activity_time_counts.values, 
                 labels={'x': 'month', 'y': 'Number of Events'},
                 title='Distribution of Activity Times')

    # Zeigen
    st.plotly_chart(fig)

def generate_latitude_longitude_chart(df: pd.DataFrame):
    st.markdown("&nbsp;")
    st.title("Coordinate Plot of all Events 🌍")
    coordinate_df = df[["location.name", "location.location.coordinate.lat", "location.location.coordinate.lon"]].dropna()
    coordinate_df = coordinate_df.rename(columns={"location.name": "Location", "location.location.coordinate.lat": "latitude", "location.location.coordinate.lon": "longitude"})
    st.map(coordinate_df, color="#FAED27")


def visualize_time_of_day(df: pd.DataFrame):
    # visualize time of day with pie chart
    st.markdown("&nbsp;")
    st.title("Events by Time of Day 🕒")
    time_of_day_counts = df['time_of_day'].value_counts()
    fig = px.pie(time_of_day_counts, values=time_of_day_counts, names=time_of_day_counts.index, title='Distribution of Time of Day')
    st.plotly_chart(fig)
    st.markdown("The starting hours were grouped into the above 4 times of the day.", help="We used the following classification scheme: Morning: 6am - 12pm, Afternoon: 12pm - 6pm, Evening: 6pm - 12am, Night: 12am - 6am")

def visualize_starting_hour_of_events(df: pd.DataFrame):
    # visualize starting hour with line chart
    st.markdown("&nbsp;")
    st.title("Events by Starting Hour 🕰️")
    # Count the occurrences of each starting hour (starting hour is an integer)
    starting_hour_counts = df['starting_hour'].value_counts()
    
    # Use plotly.express to create the line chart
    fig = px.bar(
        x=starting_hour_counts.index,
        y=starting_hour_counts.values,
        title='Distribution of Starting Hour',
        labels={'x': 'Starting Hour', 'y': 'Number of Events'}
    )

    # Show the line chart
    st.plotly_chart(fig)

def visualize_subcategory_by_supercategory(df: pd.DataFrame):
    # multiple plots, one for each supercategory
    st.markdown("&nbsp;")
    st.title("Events by Event Type and Subcategory 🧨🎈")
    
    # Create a list of the supercategories
    supercategories = df['supercategory'].unique()
    # Create a frame for the plots
    st.markdown('<div style="display: flex; flex-wrap: wrap;">', unsafe_allow_html=True)

    # Create a plot for each supercategory
    for supercategory in supercategories:
        if supercategory == 'familie-kinder' or supercategory == 'anderes':
            continue
        # Filter the DataFrame for the supercategory
        filtered_df = df[df['supercategory'] == supercategory]
        
        # Count the occurrences of each subcategory for the filtered DataFrame
        subcategory_counts = filtered_df['subcategory'].value_counts()

        # Use plotly.express to create the bar chart
        try:
            fig = px.bar(
                x=subcategory_counts.index,
                # display y as percentage
                y=subcategory_counts.values,
                title=f'Distribution of Subcategories for {supercategory}',
                labels={'x': 'Subcategory', 'y': 'Number of Events'},
                color_discrete_sequence=['green']
            )
        except ValueError:
            continue
        
        # Set title for the subplot
        fig.update_layout(title_text=supercategory)

        # Show the bar chart
        st.plotly_chart(fig)

    # Close the frame for the plots
    st.markdown('</div>', unsafe_allow_html=True)



def main():
    # Read in the csv-file
    df = pd.read_csv('data/all_events_dashboard.csv')
    print(df.shape)
    display_title()
    event_type, location_sidebar, season, mood = get_user_preferences()
    # Display the also the subcategories for each supercategory that is selected
    event_subtype = display_subcategories(event_type, df)
    st.write('We will analyze your preferences and show you our recommendations for matching locations in Stuttgart.')
    selected_tab = st.selectbox("Choose top location or all locations", ["Top 5 Locations", "All Locations", "Information about subset of dataset", 'Information about whole dataset'])
    if selected_tab == "Information about subset of dataset":
        dislpay_frequent_words_from_description(df)
        expander1 = st.expander("Click to see more information about the dataset")
        with expander1:
            generate_activity_type_chart(df)
            generate_activity_type_pie_chart(df)
            visualize_subcategory_by_supercategory(df)
            visualize_starting_hour_of_events(df)
            visualize_time_of_day(df)
            generate_activity_time_chart(df)
            show_no_of_events_used(df)
            #generate_latitude_longitude_chart(df)
            #show_google_maps_stuttgart()
            display_colnames(df)
    elif selected_tab == "Information about whole dataset":
        # include images
        st.markdown("&nbsp;")
        st.title("Information about whole dataset")
        st.markdown("The wordcloud of the event descriptions shows the most frequent words in the event descriptions of all events in the dataset.")
        st.image("img/word_cloud_all_events.png", use_column_width=True)
        expander2 = st.expander("Click to see more information about the whole dataset")
        with expander2:
            st.image('img/distribution_of_activity_type_all_events.png', use_column_width=True)
            st.markdown('The yellow specifies the rows per column which contain missing values.')
            st.image('img/Missing_values_all_events.png', use_column_width=True)
            st.markdown('After cleaning the dataset, e.g. removing columns with more than 80% missing values, the heatmap of missing values looks like this:')
            st.image('img/missing_values_after_cleaning_all_events.png', use_column_width=True)
            st.image('img/starting_hour_all_events.png', use_column_width=True)
            st.image('img/time_of_day_all_events.png', use_column_width=True)

    else:
        display_locations(df, selected_tab, event_type, location_sidebar, season, event_subtype, mood)
        show_no_of_events_used(df)
        #generate_latitude_longitude_chart(df)
    



    st.markdown('&nbsp;')
    st.markdown('<div style="text-align:center;">Copyright © 2024 Julius Döbelt and Haoran Huang. All rights reserved.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
