"""
Feature Engineering & Feature Store Module (Member 3)

Responsibilities:
- Engineer user, item, and interaction features
- Design SQL schema for transformed data
- Implement Feast feature store (or custom registry)
- Version and retrieve features for training/inference
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def engineer_features(input_path: str, output_path: str) -> pd.DataFrame:
    """Simple, working feature engineering placeholder.

    Reads the prepared CSVs from `input_path` (expected files produced
    by `prepare_data`) and constructs a basic feature table containing
    user and item aggregated statistics. Saves the resulting features
    to `output_path/features.csv` and returns the DataFrame.
    """
    logger.info(f"Starting feature engineering from {input_path}")
    input_dir = Path(input_path)
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Expect processed CSVs named like <dataset>_processed.csv
    ratings_file = input_dir / "ratings_processed.csv"
    if not ratings_file.exists():
        # Fallback: try combined prepared file
        combined = input_dir / "prepared_combined.csv"
        if combined.exists():
            ratings_file = combined

    if not ratings_file.exists():
        raise FileNotFoundError(f"Ratings file not found under {input_dir}")

    df = pd.read_csv(ratings_file)

    # Basic aggregates
    user_avg = df.groupby("userId")["rating"].mean().rename("user_avg")
    item_avg = df.groupby("movieId")["rating"].mean().rename("item_avg")
    item_count = df.groupby("movieId")["rating"].count().rename("item_count")

    # Merge back to interactions
    features = df.merge(user_avg, on="userId", how="left")
    features = features.merge(item_avg, on="movieId", how="left")
    features = features.merge(item_count, on="movieId", how="left")

    # Keep a compact feature set
    feature_cols = ["userId", "movieId", "rating", "user_avg", "item_avg", "item_count"]
    features = features[feature_cols].drop_duplicates().reset_index(drop=True)

    out_file = output_dir / "features.csv"
    features.to_csv(out_file, index=False)
    logger.info(f"Features saved to {out_file} ({len(features)} rows)")

    return features


def design_sql_schema(output_path: str) -> str:
    logger.info("Design SQL schema (placeholder)")
    schema = "-- SQL schema placeholder for feature tables"
    out = Path(output_path) / "feature_schema.sql"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(schema)
    return str(out)


def setup_feature_store(features_path: str, config: Optional[Dict[str, Any]] = None) -> str:
    logger.info(f"Setting up simple feature store for {features_path}")
    store_dir = Path(features_path)
    store_dir.mkdir(parents=True, exist_ok=True)
    return str(store_dir.resolve())


def retrieve_features(entity_ids: list, feature_names: list, timestamp: Optional[str] = None) -> pd.DataFrame:
    logger.info(f"Retrieving features for {len(entity_ids)} entities (placeholder)")
    # Placeholder: return empty DataFrame with requested columns
    cols = ["entity_id"] + feature_names
    return pd.DataFrame(columns=cols)
