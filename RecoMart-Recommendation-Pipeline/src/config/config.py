"""
Configuration settings for RecoMart Recommendation Pipeline
"""

from pathlib import Path

# ==========================================================
# Project Root Directory
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ==========================================================
# Dataset Paths
# ==========================================================

DATASET_DIR = PROJECT_ROOT / "dataset"

MOVIES_FILE = DATASET_DIR / "movies.csv"
RATINGS_FILE = DATASET_DIR / "ratings.csv"
LINKS_FILE = DATASET_DIR / "links.csv"
TAGS_FILE = DATASET_DIR / "tags.csv"

# ==========================================================
# Raw Data Lake
# ==========================================================

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

CSV_RAW_DIR = RAW_DATA_DIR / "csv"
API_RAW_DIR = RAW_DATA_DIR / "api"

# ==========================================================
# Logs
# ==========================================================

LOG_DIR = PROJECT_ROOT / "data" / "logs"

# ==========================================================
# Metadata
# ==========================================================

METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
