import pandas as pd

df = pd.read_csv('data/2000_events_sample.csv')

liste = df['supercategory'].unique()

for list in liste:
    print(list)