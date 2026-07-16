"""
REST API Ingestion Module

Downloads product data from an external API
and stores it in the Raw Data Lake.
"""

import time
import requests

from src.config.config import (
    PRODUCT_API_URL,
    API_TIMEOUT,
    API_RETRY_COUNT,
    API_RETRY_DELAY,
    API_RAW_DIR,
)

from src.utils.logger import logger

from src.utils.helper import (
    create_timestamp_folder,
    save_json,
)


def fetch_api_data():
    """
    Downloads data from REST API
    with retry mechanism.
    """

    for attempt in range(1, API_RETRY_COUNT + 1):

        try:

            logger.info(f"API Request Attempt {attempt}")

            response = requests.get(
                PRODUCT_API_URL,
                timeout=API_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:

            logger.warning(f"Attempt {attempt} failed : {e}")

            time.sleep(API_RETRY_DELAY)

    logger.error("API request failed.")

    return None


def run_api_ingestion(metadata):
    """
    Downloads API data and stores it in the Raw Data Lake.
    """

    logger.info("=" * 80)
    logger.info("API INGESTION STARTED")
    logger.info("=" * 80)

    data = fetch_api_data()

    if data is None:

        logger.error("No API data downloaded.")

        return

    destination = create_timestamp_folder(
        API_RAW_DIR,
        "products",
    )

    output_file = destination / "products.json"

    save_json(
        data,
        output_file,
    )

    metadata.add_api_metadata(
        dataset_name="products",
        destination_file=output_file,
        json_data=data,
    )

    logger.info(f"API data stored at {output_file}")

    logger.info("=" * 80)
    logger.info("API INGESTION COMPLETED")
    logger.info("=" * 80)