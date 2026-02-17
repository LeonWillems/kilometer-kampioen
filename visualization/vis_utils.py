import json
import numpy as np
import pandas as pd
from copy import deepcopy
import matplotlib.pyplot as plt

from data_processing.data_utils import read_csv_to_df

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def get_coordinates() -> dict:
    """Gets the station coordinates from the coordinates JSON
    file. Each pair of coordinates represents the middle of
    the station on the spoorkaart image. Keys are station codes.

    Returns:
    - dict: Dictionary of station coordinates. Example:
        {"Ehv": [927, 1389], "Gp": [945, 1407], ...}
    """
    coordinates_path = SETTINGS.COORDINATES_PATH
    with open(coordinates_path, mode='r') as f:
        coordinates = json.load(f)

    return coordinates


def read_image() -> np.array:
    """Reads in the spoorkaart image from file.

    Returns:
    - np.array: Image array of the spoorkaart
    """
    spoorkaart_path = SETTINGS.SPOORKAART_PATH
    img = plt.imread(spoorkaart_path)

    return img


def get_latest_route() -> pd.DataFrame:
    """Will get the latest saved route from the routes
    directory for the current version (in settings).

    Returns:
    - pd.DataFrame: DataFrame containing the latest route
    """
    routes_path = SETTINGS.ROUTES_PATH
    route_files_paths = sorted(routes_path.glob('*.csv'))
    latest_route_path = route_files_paths[-1]
    route_df = read_csv_to_df(latest_route_path)

    return route_df


def get_corners() -> dict:
    """Gets the coordinates of the corners in the spoorkaart (simple). These
    have been manually determined and are stored in a JSON file. Here we also
    inverse the direction and add to the dict to make it symmetric.

    Returns:
    - dict: Dictionary of corner coordinates. Example:
        {"Bgn": {"Rb": [[463, 1418], [463, 1440]], ..},      # [x, y] coords
         "Rb": {"Bgn": [[463, 1440], [463, 1418]], ..}, ..}
    """
    corners_path = SETTINGS.CORNERS_PATH
    with open(corners_path, mode='r') as f:
        corners: dict[str, dict] = json.load(f)

    corners_symmetric = deepcopy(corners)

    # Make symmetric by adding the reversed directions (e.g., Rtd -> Bd)
    for from_station, to_stations in corners.items():
        for to_station, corner_coords in to_stations.items():
            if to_station not in corners_symmetric:
                corners_symmetric[to_station] = {}
            if from_station not in corners_symmetric[to_station]:
                # Add the reversed coordinates for the reverse direction
                corners_symmetric[to_station][from_station] \
                    = corner_coords[::-1]

    return corners_symmetric
