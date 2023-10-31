# split up the json file stuutgart_events.json into multiple files
# each file should contain 1000 events

import ijson
import pandas as pd
import json

def extract_json_data_into_dataframe(json_file_path: str, no_of_entries: int) -> pd.DataFrame:
    """
    extracts the json data from the json file and returns a pandas dataframe
    :param json_file_path: path to the json file
    :param no_of_entries: number of entries to be extracted from the json file
    :return: pandas dataframe containing the extracted data
    """
    df = pd.DataFrame()

    f = open(json_file_path, 'r')
    for i, json_event in enumerate(ijson.items(f, 'item')):
        single_df = pd.json_normalize(json_event)
        df = pd.concat([df, single_df], ignore_index=True)
        if i == no_of_entries:
            break
    f.close()

    return df

df = extract_json_data_into_dataframe('stuttgart_events.json', 100)


