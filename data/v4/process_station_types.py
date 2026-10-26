import json
import pandas as pd

from data_processing.data_utils import read_csv_to_df

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()

TYPE_CONVERSION = {
    "facultatiefStation": 0,
    "intercitystation": 0,
    "knooppuntIntercitystation": 1,
    "knooppuntSneltreinstation": 1,
    "knooppuntStoptreinstation": 1,
    "megastation": 1,
    "sneltreinstation": 0,
    "stoptreinstation": 0,
}


def build_indicator_dict(stations_df: pd.DataFrame) -> dict[str, int]:
    """Builds a dict with indicators for each station: knooppunt (1) or not (0)

    Args:
    - stations_df (pd.DataFrame): DataFrame containing at least station code
        and station type, e.g. "Ht" and "knooppuntIntercitystation"

    - dict[str, int]: Containing and indicator 1/0 for each station being a
        "knooppunt" or not (see type conversion above), example:
        {'Ht': 1, 'Ehv': 1, 'Vg': 0, 'Ehs': 0, ...}

    """
    indicator_dict = {}

    for _, row in stations_df.iterrows():
        station_code = row['code'].title()
        station_type = row['type']
        knooppunt_indicator = TYPE_CONVERSION[station_type]

        indicator_dict[station_code] = knooppunt_indicator

    return indicator_dict


def process():
    """Function to process the station types."""
    stations_file_name = "stations-2023-09.csv"
    file_path = SETTINGS.INFORMATION_DIR / stations_file_name

    stations_df = read_csv_to_df(file_path)
    indicator_dict = build_indicator_dict(stations_df)
    indicator_file_name = "knooppunt_indicator.json"

    with open(SETTINGS.DATA_PATH / indicator_file_name, mode='w') as f:
        json.dump(indicator_dict, f, indent=4)


if __name__ == "__main__":
    process()
