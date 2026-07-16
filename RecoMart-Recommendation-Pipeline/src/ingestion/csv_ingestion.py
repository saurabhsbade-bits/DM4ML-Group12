"""
CSV Data Ingestion Module

Reads CSV datasets from the dataset directory
and stores them in the Raw Data Lake.
"""

import shutil
from pathlib import Path

from src.config.config import (
    CSV_FILES,
    CSV_RAW_DIR,
)

from src.utils.logger import logger
from src.utils.helper import create_timestamp_folder


def ingest_csv(
    source_file: Path,
    dataset_name: str,
    metadata,
):
    """
    Copies one CSV file into the Raw Data Lake.
    """

    logger.info("=" * 60)
    logger.info(f"Starting ingestion : {dataset_name}")

    try:

        if not source_file.exists():
            raise FileNotFoundError(source_file)

        destination_folder = create_timestamp_folder(
            CSV_RAW_DIR,
            dataset_name,
        )

        destination_file = destination_folder / source_file.name

        shutil.copy2(source_file, destination_file)

        metadata.add_csv_metadata(
            dataset_name=dataset_name,
            source_file=source_file,
            destination_file=destination_file,
        )

        logger.info(f"Source      : {source_file}")
        logger.info(f"Destination : {destination_file}")
        logger.info("Status      : SUCCESS")

    except Exception as e:

        logger.error("Status      : FAILED")
        logger.error(str(e))

    finally:

        logger.info(f"Completed ingestion : {dataset_name}")
        logger.info("=" * 60)


def run_csv_ingestion(metadata):
    """
    Runs ingestion for all CSV datasets.
    """

    logger.info("=" * 80)
    logger.info("CSV INGESTION STARTED")
    logger.info("=" * 80)

    for dataset_name, source_file in CSV_FILES.items():

        ingest_csv(
            source_file,
            dataset_name,
            metadata,
        )

    logger.info("=" * 80)
    logger.info("CSV INGESTION COMPLETED")
    logger.info("=" * 80)