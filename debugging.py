import pandas as pd
import numpy as np

df = pd.read_csv('data/events_df.csv')

edf = df[df['time_of_day'] == 'Evening']
print(len(edf))
print(edf['location.category'].value_counts())

# check for null values in location.category
print(edf['location.category'].isnull().sum())