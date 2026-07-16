"""
Configuration File
RecoMart Recommendation Pipeline

This module centralizes all project configuration including:
- Dataset paths
- Data lake paths
- Logging
- API configuration
- Scheduler configuration
"""

from pathlib import Path

# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ==========================================================
# DATASET DIRECTORY (Original Downloaded Files)
# ==========================================================

DATASET_DIR = PROJECT_ROOT / "dataset"

MOVIES_FILE = DATASET_DIR / "movies.csv"
RATINGS_FILE = DATASET_DIR / "ratings.csv"
LINKS_FILE = DATASET_DIR / "links.csv"
TAGS_FILE = DATASET_DIR / "tags.csv"

# All CSV datasets
CSV_FILES = {
    "movies": MOVIES_FILE,
    "ratings": RATINGS_FILE,
    "links": LINKS_FILE,
    "tags": TAGS_FILE,
}

# ==========================================================
# DATA DIRECTORIES
# ==========================================================

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CSV_RAW_DIR = RAW_DATA_DIR / "csv"
API_RAW_DIR = RAW_DATA_DIR / "api"

# ==========================================================
# LOGGING
# ==========================================================

LOG_DIR = DATA_DIR / "logs"
LOG_FILE = LOG_DIR / "ingestion.log"

# ==========================================================
# METADATA
# ==========================================================

METADATA_DIR = DATA_DIR / "metadata"
METADATA_FILE = METADATA_DIR / "ingestion_metadata.json"

# ==========================================================
# API CONFIGURATION
# ==========================================================

PRODUCT_API_URL = "https://dummyjson.com/products"

API_TIMEOUT = 10          # seconds
API_RETRY_COUNT = 3
API_RETRY_DELAY = 2       # seconds

# ==========================================================
# SCHEDULER
# ==========================================================

SCHEDULE_TIME = "10:00"

# ==========================================================
# FILE EXTENSIONS
# ==========================================================

CSV_EXTENSION = ".csv"
JSON_EXTENSION = ".json"

# ==========================================================
# CREATE REQUIRED DIRECTORIES
# ==========================================================

REQUIRED_DIRECTORIES = [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    CSV_RAW_DIR,
    API_RAW_DIR,
    LOG_DIR,
    METADATA_DIR,
]

for directory in REQUIRED_DIRECTORIES:
    directory.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Scheduler Configuration
# ==========================================================

SCHEDULE_TIME = "10:00"

SCHEDULER_SLEEP_TIME = 1

PIPELINE_NAME = "RecoMart Recommendation Pipeline"