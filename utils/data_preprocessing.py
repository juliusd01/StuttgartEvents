
import pandas as pd


def remove_events_not_in_stuttgart(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove all events not in Stuttgart by looking at the evntData.location.location.city column
    :param df: dataframe containing the events
    :return: dataframe containing only events in Stuttgart (might be the same as inpt df)
    """
    df = df[df['eventData.location.location.address.city'] == 'Stuttgart']
    return df
