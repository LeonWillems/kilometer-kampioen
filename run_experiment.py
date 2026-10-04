"""
Code to run an experiment: multiple starting conditions for some amount of time
each. Will get terminated after this time per run no matter what.
"""

from pathlib import Path

from run import _setup, _run_algo

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()

# Run each for x seconds
Parameters.TIMEOUT = 300

# List of starting conditions. Fill in either this one, or the two variables
# below. This one should be of type list[tuple] = [('Ht', '00:00'), ...]
STARTING_CONDITIONS = [
    ('Gvc', '00:10'), ('Ah', '00:00'), ('Ehv', '00:27'), ('Gn', '01:41'),
    ('Asn', '00:05')
]

# Lists of starting stations & times. Both list of strings
STARTING_STATIONS = []
STARTING_TIMES = []


def get_starting_conditions() -> list[tuple]:
    """Builds a list of tuples each denoting one starting condition."""
    starting_conditions = []

    for start_station in STARTING_STATIONS:
        for start_time in STARTING_TIMES:
            starting_conditions.append((start_station, start_time))

    return starting_conditions


if __name__ == "__main__":
    runs_path: Path = SETTINGS.RUNS_PATH

    if STARTING_CONDITIONS is None:
        starting_conditions = get_starting_conditions()
    else:
        starting_conditions = STARTING_CONDITIONS

    for (start_station, start_time) in starting_conditions:
        Parameters.START_STATION = start_station
        Parameters.START_TIME = start_time

        current_run_path = _setup(runs_path)
        _run_algo(current_run_path)

    print("Experiment runner finished execution.")
