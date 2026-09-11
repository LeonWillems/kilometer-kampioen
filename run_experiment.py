from pathlib import Path

from run import _setup, _run_algo

from settings import Parameters, VersionSettings
SETTINGS = VersionSettings.get_version_settings()

Parameters.TIMEOUT = 5
STARTING_CONDITIONS = [
    ('Ht', '10:00'), ('Tb', '06:00')
]


if __name__ == "__main__":
    runs_path: Path = SETTINGS.RUNS_PATH

    for (start_station, start_time) in STARTING_CONDITIONS:
        Parameters.START_STATION = start_station
        Parameters.START_TIME = start_time

        current_run_path = _setup(runs_path)
        _run_algo(current_run_path)

    print("Experiment runner finished execution.")
