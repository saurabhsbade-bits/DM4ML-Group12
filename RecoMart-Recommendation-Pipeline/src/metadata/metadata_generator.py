"""
Metadata Generator
Creates ingestion metadata for CSV and API datasets.
"""

from datetime import datetime

from src.config.config import METADATA_FILE
from src.utils.helper import (
    save_json,
    file_size_mb,
    csv_record_count,
    count_json_records,
)
from src.utils.logger import logger


class MetadataGenerator:

    def __init__(self):
        self.metadata = []

    def add_csv_metadata(
        self,
        dataset_name,
        source_file,
        destination_file,
        status="SUCCESS",
    ):

        self.metadata.append(
            {
                "dataset": dataset_name,
                "source_type": "CSV",
                "source_file": str(source_file),
                "destination": str(destination_file),
                "records": csv_record_count(destination_file),
                "file_size_mb": file_size_mb(destination_file),
                "status": status,
                "ingestion_time": datetime.now().isoformat(),
            }
        )

    def add_api_metadata(
        self,
        dataset_name,
        destination_file,
        json_data,
        status="SUCCESS",
    ):

        self.metadata.append(
            {
                "dataset": dataset_name,
                "source_type": "REST API",
                "destination": str(destination_file),
                "records": count_json_records(json_data),
                "file_size_mb": file_size_mb(destination_file),
                "status": status,
                "ingestion_time": datetime.now().isoformat(),
            }
        )

    def save(self):
        save_json(self.metadata, METADATA_FILE)
        logger.info(f"Metadata saved -> {METADATA_FILE}")