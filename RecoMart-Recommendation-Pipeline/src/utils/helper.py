"""
Utility Helper Functions
RecoMart Recommendation Pipeline
"""

from datetime import datetime
from pathlib import Path
import json
import pandas as pd


def current_timestamp():
    """
    Returns current timestamp.

    Example:
    20260716223045
    """

    return datetime.now().strftime("%Y%m%d%H%M%S")


def create_timestamp_folder(base_directory: Path,
                            dataset_name: str) -> Path:
    """
    Creates

    base_directory/dataset_name/YYYY/MM/DD/HHMMSS
    """

    now = datetime.now()

    folder = (
        base_directory
        / dataset_name
        / now.strftime("%Y")
        / now.strftime("%m")
        / now.strftime("%d")
        / now.strftime("%H%M%S")
    )

    folder.mkdir(parents=True, exist_ok=True)

    return folder


def ensure_directory(directory: Path):
    """
    Creates directory if it does not exist.
    """

    directory.mkdir(parents=True, exist_ok=True)


def file_size(file_path: Path):
    """
    Returns file size in MB.
    """

    if not file_path.exists():
        return 0

    return round(file_path.stat().st_size / (1024 * 1024), 2)


def csv_record_count(file_path: Path):
    """
    Returns number of rows in CSV.
    """

    if not file_path.exists():
        return 0

    dataframe = pd.read_csv(file_path)

    return len(dataframe)


def save_json(data, destination: Path):
    """
    Saves dictionary as JSON.
    """

    with open(destination, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            default=str
        )
import os


def count_json_records(json_data):
    """
    Count records in a JSON response.
    """

    if isinstance(json_data, list):
        return len(json_data)

    if isinstance(json_data, dict):

        # DummyJSON returns products under "products"
        if "products" in json_data:
            return len(json_data["products"])

        return len(json_data)

    return 0


def file_size_mb(file_path: Path):
    """
    Returns file size in MB.
    """

    if not file_path.exists():
        return 0

    return round(os.path.getsize(file_path) / (1024 * 1024), 2)        