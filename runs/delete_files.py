from pathlib import Path

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def remove_files_in_dir(run_path: Path) -> None:
    """Will remove all files for a given path.

    Args:
    - run_path (Path): To the right folder
    """
    # List all files in the current dir
    files = [f for f in run_path.iterdir() if f.is_file()]

    # Remove all files
    for file_to_remove in files:
        file_to_remove.unlink()


def remove_all_but_last_dir(runs_path: Path) -> None:
    """Will remove all but the last dir in a given path.

    Args:
    - runs_path (Path): Path containing each run for a specific version
    """
    # List all dirs for the current path
    run_paths = [path for path in runs_path.iterdir() if path.is_dir()]

    # If there's nothing or only one dir, do nothing
    if len(run_paths) <= 1:
        return

    # Keep the newest dir, remove all others
    for run_path in run_paths[:-1]:
        remove_files_in_dir(run_path)
        run_path.rmdir()


if __name__ == "__main__":
    # Define for which version to delete files
    runs_path: Path = SETTINGS.RUNS_PATH
    remove_all_but_last_dir(runs_path)
