from pathlib import Path

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def get_paths() -> tuple[Path, Path, Path]:
    """Gets the right paths to the three kinds of files.

    Args:
    - version (str): Version of the route finding algo, example 'v0'

    Returns:
    - tuple: Three paths
    """
    logs_path = SETTINGS.LOGS_PATH
    parameters_path = SETTINGS.PARAMETERS_PATH
    routes_path = SETTINGS.ROUTES_PATH
    return (logs_path, parameters_path, routes_path)


def remove_all_but_last_file(path: Path):
    """Will remove all but the last file for a given path.

    Args:
    - path (Path): To the right folder
    """
    # List all files in the directory
    files = [f for f in path.iterdir() if f.is_file()]

    # If there's nothing or only one file, do nothing
    if len(files) <= 1:
        return

    # Keep the newest file, remove all others
    for file_to_remove in files[:-1]:
        file_to_remove.unlink()


if __name__ == "__main__":
    # Define for which version to delete files
    paths = get_paths()

    for path in paths:
        remove_all_but_last_file(path)
