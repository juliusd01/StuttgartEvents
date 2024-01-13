import pandas as pd
import matplotlib.pyplot as plt
import ijson
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#######################
# Parse Data and create DataFrame
#######################

def parse_json(file_path, num_events):
    """
    parses the json file and returns a list of events

    :param file_path: path to the json file
    :param num_events: number of events that should be parsed
    """
    with open(file_path, 'rb') as f:
        events = ijson.items(f, 'item')
        limited_events = [next(events) for _ in range(num_events)]
        logger.info('All events parsed. Total number of events: {}'.format(len(limited_events)))
        return limited_events

# specify the number of events that should be preprocessed, max number of events is 264395
num_events = 264395
events = parse_json('stuttgart_events.json', num_events)

# Handle the nested structure of the original json file
events_df = pd.DataFrame(events)
all_keys = set().union(*events_df["eventData"].apply(lambda x: x.keys()))
for key in all_keys:
    events_df[key] = events_df["eventData"].apply(lambda x: x.get(key, None))

keys_location = set().union(*events_df["location"].apply(lambda x: x.keys()))
for key in keys_location:
    events_df[f'location.{key}'] = events_df["location"].apply(lambda x: x.get(key, None))

keys_location_location = set().union(*events_df["location.location"].apply(lambda x: x.keys()))
for key in keys_location_location:
    events_df[f'location.location.{key}'] = events_df["location.location"].apply(lambda x: x.get(key, None))

keys_location_location_address = set().union(*events_df["location.location.address"].apply(lambda x: x.keys()))
for key in keys_location_location_address:
    events_df[f'location.location.address.{key}'] = events_df["location.location.address"].apply(lambda x: x.get(key, None))

#######################
# Data Cleaning
#######################
# delete dictionary columns
events_df = events_df.drop('eventData', axis=1)
events_df = events_df.drop('location', axis=1)
events_df = events_df.drop('location.location', axis=1)
events_df = events_df.drop('location.location.address', axis=1)

# Create a heatmap of missing values
# plt.figure(figsize=(25, 6))  # Adjust the figure size as needed
# sns.heatmap(events_df.isnull(), cmap='viridis', cbar=False)
# plt.title('Missing Values Heatmap')
# plt.show()
# # drop columns with more than 80% missing values
# events_df = events_df.dropna(thresh=events_df.shape[0]*0.2, axis=1)
# logging.info('Shape of the DataFrame after dropping columns with more than 80% missing values: {}'.format(events_df.shape))

# # again plot missing values after cleaning
# plt.figure(figsize=(15, 6))  # Adjust the figure size as needed
# sns.heatmap(events_df.isnull(), cmap='viridis', cbar=False)
# plt.title('Missing Values Heatmap')
# plt.show()

# # Only keep events that were not cancelled
# events_df = events_df[events_df['cancelled'] == False]

# # Only keep events where the location is actually in Stuttgart
# events_df = events_df[events_df['location.location.address.city'] == 'Stuttgart']


#######################
# Feature Engineering
#######################
if 'startDate' in events_df.columns and events_df['startDate'].dtype != 'datetime64[ns]':
    events_df['startDate'] = pd.to_datetime(events_df['startDate'], format='mixed', utc=True)

# add column for day of week
events_df['dayofweek'] = events_df['startDate'].dt.dayofweek
# only consider events on Wednesdays
events_df = events_df[events_df['dayofweek'] == 2]
events_df.reset_index(drop=True, inplace=True)
# log the number of events remaining
logging.info('Number of events after filtering for Wednesdays: {}'.format(events_df.shape[0]))


# sample the data to reduce the number of events, e.g. only select 2000 events
events_df = events_df.sample(n=2000, random_state=42)
events_df.reset_index(drop=True, inplace=True)
logging.info('Number of events after sampling: {}'.format(events_df.shape[0]))

# Create year column
events_df['year'] = events_df['startDate'].dt.year
# Create month column
events_df['month'] = events_df['startDate'].dt.month
# Create column with startHour
events_df['starting_hour'] = events_df['startDate'].apply(lambda x: x.hour)
#plot starting_hour
events_df['starting_hour'].hist(bins=24)
plt.show()

# create a function to determine the season
def get_season(date: pd.Timestamp) -> str:
    """
    returns the season of a given date
    :param date: date for which the season should be determined
    :return: season of the given date
    """
    # spring
    if date.month >= 3 and date.month <= 5:
        return 'spring'
    # summer
    elif date.month >= 6 and date.month <= 8:
        return 'summer'
    # autumn
    elif date.month >= 9 and date.month <= 11:
        return 'autumn'
    # winter
    else:
        return 'winter'

# apply the function to the startDate column
events_df['season'] = events_df['startDate'].apply(get_season)

# instead of having to choose location based on postcal code, it would be way nicer to choose location based on district
# therefore we need to add a column containing the district of the event
# we can get the district by using a mapping from postcal code to district
# https://home.meinestadt.de/stuttgart/postleitzahlen

zip_code_to_district = {
    "70173": "Europaviertel",
    "70174": "Relenberg",
    "70178": "Karlshöhe",
    "70191": "Am Rosensteinpark",
    "70193": "Kräherwald",
    "70195": "Botnang-West",
    "70197": "Vogelsang",
    "70199": "Südheim",
    "70372": "Bad Cannstatt",
    "70567": "Sternhäule",
    "70569": "Pfaffenwald",
    "70437": "Freiberg",
    "70176": "Rosenberg",
    "70188": "Uhlandshöhe",
    "70374": "Im Geiger",
    "70439": "Zuffenhausen-Elbelen",
    "70190": "Stöckach",
    "70180": "Weinsteige",
    "70182": "Heusteigviertel",
    "70376": "Neckarvorstadt",
    "70378": "Mönchfeld",
    "70597": "Waldau",
    "70565": "Möhringen-Süd",
    "70469": "Feuerbach-Ost",
    "70199": "Südheim"
}


def get_district_from_postcal_code(postcalCode: int):
    """
    returns the district of a given postal code
    :param postcalCode: postal code for which the district should be determined
    :return: district of the given postal code
    """
    try:
        district = zip_code_to_district[str(postcalCode)]
    except KeyError:
        district = "Other"
    return district
    
# apply the function to the postal code column
events_df['district'] = events_df['location.location.address.postalCode'].apply(get_district_from_postcal_code)
 
# create features supercategory and subcategory
# split entry in eventData.location.category by / 
def extract_categories(df: pd.DataFrame):
    """
    extracts the supercategory and subcategory from the eventData.location.category column
    :param df: dataframe containing the events
    :return: dataframe containing the events with two new columns supercategory and subcategory
    """
    events_df['supercategory'] = np.where(events_df['location.category'].notnull(), events_df['location.category'].str.split('/').str[0], 'anderes')
    events_df['subcategory'] = np.where(events_df['location.category'].notnull(), events_df['location.category'].str.split('/').str[1], 'anderes')
    # everything to lowercase
    events_df['supercategory'] = events_df['supercategory'].str.lower()
    events_df['subcategory'] = events_df['subcategory'].str.lower()
    return events_df

events_df = extract_categories(events_df)


# create a column that classifies the events into morning, afternoon and evening
def get_time_of_day(time: int) -> str:
    """
    returns the time of day of a given start time
    :param time: time for which the time of day should be determined
    :return: time of day of the given time
    """
    # morning
    if time >= 6 and time < 12:
        return 'morning'
    # afternoon
    elif time >= 12 and time < 18:
        return 'afternoon'
    # evening
    elif time >= 18 and time < 24:
        return 'evening'
    # night
    else:
        return 'night'
    
# apply the function to the starting_hour column
events_df['time_of_day'] = events_df['starting_hour'].apply(get_time_of_day)
# plot time_of_day
events_df['time_of_day'].hist(bins=4)
plt.show()

#######################
# Save DataFrame
#######################
events_df.to_csv('2000_events_sample.csv', index=False)
logger.info('DataFrame saved to csv file.')

