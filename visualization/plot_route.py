import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from data_processing.data_utils import read_csv_to_df
from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def _get_latest_route() -> pd.DataFrame:
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


def _get_coordinates() -> dict:
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


def _read_image() -> np.array:
    """Reads in the spoorkaart image from file.

    Returns:
    - np.array: Image array of the spoorkaart
    """
    spoorkaart_path = SETTINGS.SPOORKAART_PATH
    img = plt.imread(spoorkaart_path)

    return img


def plot_route_lines(coordinates: dict, route: pd.DataFrame) -> None:
    """Will plot the route lines on the current matplotlib axis.
    Each line represents a connection between two stations in the route.

    Args:
    - coordinates (dict): Dictionary of station coordinates. Example:
        {"Ehv": [927, 1389], "Gp": [945, 1407], ...}
    - route (pd.DataFrame): DataFrame containing the route information.
    """
    for _, row in route.iterrows():
        x1, y1 = coordinates[row['Station']]
        x2, y2 = coordinates[row['To']]
        plt.plot([x1, x2], [y1, y2], color='red', linewidth=2)

    return


if __name__ == "__main__":
    """Main function to plot the latest route on the spoorkaart."""
    route_df = _get_latest_route()
    coordinates = _get_coordinates()
    spoorkaart_img = _read_image()

    plot_route_lines(coordinates, route_df)

    plt.imshow(spoorkaart_img)
    plt.axis('off')
    plt.show()
