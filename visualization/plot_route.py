import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .vis_utils import (
    get_coordinates, read_image, get_latest_route, get_corners
)
from data_processing.data_utils import load_intermediate_stations
from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()

IMG_DPI = 96  # Check manually


class RoutePlotter:
    """Plots the latest route (for version denoted in settings.py) on the
    spoorkaart image. This iteration consists of plotting lines and numbers
    denoted the i-th station visited. The attributes below will each contain
    a brief description.
    """
    def __init__(self):
        # Three files to read in
        self.coordinates: dict = get_coordinates()
        self.spoorkaart_img: np.ndarray = read_image()
        self.route_df: pd.DataFrame = get_latest_route()
        self.intermediate_stations: dict = load_intermediate_stations()
        self.corners: dict = get_corners()

        # Create the Matplotlib figure and axes
        self.fig: Figure = plt.figure(
            figsize=(
                self.spoorkaart_img.shape[1] / IMG_DPI,  # Width
                self.spoorkaart_img.shape[0] / IMG_DPI,  # Height
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
            (self.h_delta, -self.v_delta),   # Bottomright
            (-self.h_delta, -self.v_delta),  # Bottomleft
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
            # First, focus on the numbered labels
            x1, y1 = self.coordinates[row['Station']]
            x2, y2 = self.coordinates[row['To']]
            coords = (x1, y1)

            # Rotate the direction of the offset
            if coords in coordinate_count:
                coordinate_count[coords] += 1
            else:
                coordinate_count[coords] = 0

            # Get the offset tuple
            offset = self.offsets[coordinate_count[coords] % 4]
            self._annotate_numbered_station(i, x1, y1, offset)

            # After numbered labels, deal with section lines
            # Color & width depending on train type
            color = 'r' if row['Type'] == 'Int' else 'b'
            linewidth = 4 if row['Type'] == 'Int' else 2
            zorder = 1 if row['Type'] == 'Int' else 2

            # List of codes of all intermediate stations (including start/stop)
            stations = self.intermediate_stations[row['Station']][row['To']]

            # Go over each consecutive pair
            for start, stop in zip(stations[:-1], stations[1:]):                
                x1, y1 = self.coordinates[start]
                x2, y2 = self.coordinates[stop]

                if start in self.corners and stop in self.corners[start]:
                    # If there are corners, plot them as well
                    corner_coords = self.corners[start][stop]

                    for corner_x, corner_y in corner_coords:
                        self.ax.plot(
                            [x1, corner_x], [y1, corner_y], color=color,
                            linewidth=linewidth, zorder=zorder,
                        )
                        x1, y1 = corner_x, corner_y

                # Plot the line between two neighboring stations
                self.ax.plot(
                    [x1, x2], [y1, y2], color=color,
                    linewidth=linewidth, zorder=zorder,
                )

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
