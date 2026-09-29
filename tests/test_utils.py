import json
import pandas as pd

from utils import get_file_path
from data_processing.data_utils import read_timetable
from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def get_log_contents() -> str:
    """Read in the contents of the latest log file."""
    log_file_path = get_file_path('.log')

    with open(log_file_path, 'r') as f:
        log_contents = f.read()
    return log_contents


def get_parms_contents() -> dict[str, str | int]:
    """Read in the contents of the latest parameters file."""
    parms_file_path = get_file_path('.json')

    with open(parms_file_path) as f:
        parms_dict = json.load(f)
    return parms_dict


def get_route_contents() -> pd.DataFrame:
    """Read in the contents of the latest route file."""
    route_file_path = get_file_path('.csv')

    route_df = read_timetable(timetable_path=route_file_path).reset_index()
    return route_df
