"""
RecoMart Recommendation Pipeline

Main Entry Point
"""

from src.ingestion.csv_ingestion import run_csv_ingestion
from src.ingestion.api_ingestion import run_api_ingestion
from src.metadata.metadata_generator import MetadataGenerator
from src.utils.logger import logger


def main():

    logger.info("=" * 100)
    logger.info("RecoMart Recommendation Pipeline Started")
    logger.info("=" * 100)

    # Create one metadata object for the entire pipeline
    metadata = MetadataGenerator()

    # Run ingestion modules
    run_csv_ingestion(metadata)
    run_api_ingestion(metadata)

    # Save metadata once after all ingestion is complete
    metadata.save()

    logger.info("=" * 100)
    logger.info("RecoMart Recommendation Pipeline Completed")
    logger.info("=" * 100)


if __name__ == "__main__":
    main()