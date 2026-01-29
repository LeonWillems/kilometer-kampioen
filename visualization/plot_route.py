import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from data_processing.data_utils import read_csv_to_df
from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()

IMG_DPI = 96  # Check manually


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


class RoutePlotter:
    """Plots the latest route (for version denoted in settings.py) on the
    spoorkaart image. This iteration consists of plotting lines and numbers
    denoted the i-th station visited. The attributes below will each contain
    a brief description.
    """
    def __init__(self):
        # Three files to read in
        self.coordinates: dict = _get_coordinates()
        self.spoorkaart_img: np.ndarray = _read_image()
        self.route_df: pd.DataFrame = _get_latest_route()

        # Create the Matplotlib figure and axes
        self.fig: Figure = plt.figure(
            figsize=(
                self.spoorkaart_img.shape[0] / IMG_DPI,  # w
                self.spoorkaart_img.shape[1] / IMG_DPI,  # h
            ),
            dpi=IMG_DPI
        )
        self.ax: Axes = self.fig.add_axes([0, 0, 1, 1])  # Fill whole figure
        self.ax.imshow(self.spoorkaart_img)

        # Horizontal and vertical deltas for the textbox offset
        self.h_delta = 6
        self.v_delta = 5

        # Loop over the directions in the following order
        self.offsets = [
            (self.h_delta, self.v_delta),    # Topright
            (-self.h_delta, self.v_delta),   # Topleft
            (-self.h_delta, -self.v_delta),  # Bottomleft
            (self.h_delta, -self.v_delta),   # Bottomright
        ]

    def _annotate_numbered_station(
        self, i: int, x1: int, y1: int, offset: tuple
    ):
        """Puts the numbered visit next to a station."""
        self.ax.annotate(
            i, (x1, y1), xytext=offset,
            textcoords='offset points',
            ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.13', fc='yellow', alpha=0.8)
        )

    def plot_route_lines(self):
        """Will plot the route lines on the current matplotlib axis.
        Each line represents a connection between two stations in the route.
        """
        # Will be used to choose the offset direction at a given station
        coordinate_count = {}

        for i, row in self.route_df.iterrows():
            x1, y1 = self.coordinates[row['Station']]
            x2, y2 = self.coordinates[row['To']]
            coords = (x1, y1)

            # Rotate the direction of the offset
            if coords in coordinate_count:
                coordinate_count[coords] += 1
            else:
                coordinate_count[coords] = 0

            # Get the offset tuple, and color & width depending on train type
            offset = self.offsets[coordinate_count[coords] % 4]
            color = 'r' if row['Type'] == 'Int' else 'b'
            linewidth = 4 if row['Type'] == 'Int' else 2
            zorder = 1 if row['Type'] == 'Int' else 2

            # Plot the line, then the numbered station visit
            self.ax.plot(
                [x1, x2], [y1, y2], color=color, 
                linewidth=linewidth, zorder=zorder,
            )
            self._annotate_numbered_station(i, x1, y1, offset)

        # Annotate for the final station as well
        self._annotate_numbered_station(i+1, x2, y2, offset)

    def show_and_save_fig(self):
        """Turns off axis, saves fig and show it on screen."""
        plt.axis('off')
        plt.savefig(
            SETTINGS.VISUALIZATION_DIR / 'route_plotted.png',
            dpi=IMG_DPI, bbox_inches='tight', pad_inches=0,
        )
        plt.show()


if __name__ == "__main__":
    """Main function to plot the latest route on the spoorkaart."""
    route_plotter = RoutePlotter()
    route_plotter.plot_route_lines()
    route_plotter.show_and_save_fig()
