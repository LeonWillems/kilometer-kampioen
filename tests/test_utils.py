import os
import json
from pathlib import Path
from ..settings import Settings
from ..data_processing.data_utils import read_timetable


def _get_file_path(files_folder: Path):
    """Get name of the last file (most recent run) in a folder."""
    file_names = os.listdir(files_folder)
    last_file_name = file_names[-1]
    return files_folder / last_file_name


def get_log_contents(version: str):
    """Read in the contents of the latest log file."""
    logs_path = Settings.VERSIONED_LOGS_PATH[version]
    log_file_path = _get_file_path(logs_path)

    with open(log_file_path, 'r') as f:
        log_contents = f.read()
    return log_contents


def get_parms_contents(version: str):
    """Read in the contents of the latest parameters file."""
    parms_path = Settings.VERSIONED_PARAMETERS_PATH[version]
    parms_file_path = _get_file_path(parms_path)

    with open(parms_file_path) as f:
        parms_dict = json.load(f)
    return parms_dict


def get_route_contents(version: str):
    """Read in the contents of the latest route file."""
    routes_path = Settings.VERSIONED_ROUTES_PATH[version]
    route_file_path = _get_file_path(routes_path)

    route_df = read_timetable(
        version=version,
        timetable_path=route_file_path,
        set_index=False,
    ).reset_index()

    return route_df
