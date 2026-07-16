"""
Scheduler Module

Automatically executes the pipeline
at the configured time every day.
"""

import time
import schedule

from main import main

from src.config.config import (
    PIPELINE_NAME,
    SCHEDULE_TIME,
    SCHEDULER_SLEEP_TIME,
)

from src.utils.logger import logger


def start_scheduler():

    logger.info("=" * 100)
    logger.info(f"{PIPELINE_NAME} Scheduler Started")
    logger.info(f"Pipeline scheduled daily at {SCHEDULE_TIME}")
    logger.info("=" * 100)

    schedule.every().day.at(SCHEDULE_TIME).do(main)

    try:

        while True:

            schedule.run_pending()

            time.sleep(SCHEDULER_SLEEP_TIME)

    except KeyboardInterrupt:

        logger.info("Scheduler stopped by user.")

    except Exception as e:

        logger.exception(f"Scheduler crashed : {e}")


if __name__ == "__main__":

    start_scheduler()