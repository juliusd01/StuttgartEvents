from utils import data_extraction as data_ext
from utils import data_preprocessing as data_prep

# load json data in pd.DataFrame
df = data_ext.extract_json_data_into_dataframe('stuttgart_events.json', 100)
print(df.shape)
# delete evenn´ts not in Stuttgart
df = data_prep.remove_events_not_in_stuttgart(df)
print(df.shape)