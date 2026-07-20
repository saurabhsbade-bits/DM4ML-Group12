"""
Feature Engineering & Feature Store Module (Member 3)

Responsibilities:
- Engineer user, item, and interaction features
- Design SQL schema for transformed data
- Implement a Feast-style feature store (custom registry, see feature_store.py)
- Version and retrieve features for training/inference

Design note - why this reads the raw MovieLens tables instead of
`data/processed/*_processed.csv`:
Member 2's preprocessing step (src/preparation/data_preprocessor.py)
auto-detects *every* numeric/categorical column and applies
MinMaxScaler/LabelEncoder to it -- including primary keys (userId,
movieId), the rating timestamp, and the pipe-separated `genres`
string (collapsed into one opaque label-encoded integer). None of the
fitted scalers/encoders are persisted, so this cannot be inverted.
That makes `data/processed` unsuitable as a base for features that
need to be interpretable, joinable and versioned (genre preference
vectors, real recency in days, human-readable ids in the feature
store/SQL schema). This module therefore sources the canonical raw
tables (`dataset/movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`
via `src.config.config.CSV_FILES`) -- which Member 2's own validation
report already confirms are clean (no missing values/duplicates) --
and still honours `input_path` by checking for Member 2's
`preparation_summary.json` as a lineage/gating signal.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.config.config import CSV_FILES
from src.features.common import build_genre_matrix
from src.features.user_features import build_user_features
from src.features.item_features import build_item_features
from src.features.similarity_features import build_interaction_features
from src.features.sql_schema import design_sql_schema
from src.features.feature_store import setup_feature_store, retrieve_features
from src.utils.helper import ensure_directory, current_timestamp

__all__ = [
    "engineer_features",
    "design_sql_schema",
    "setup_feature_store",
    "retrieve_features",
]

logger = logging.getLogger(__name__)

# Legacy column names expected by Member 4's src/models/train_model(),
# kept so the existing end-to-end pipeline (scripts/run_e2e.py) and CI
# smoke test keep working unchanged.
_LEGACY_COLUMN_MAP = {
    "user_avg_rating": "user_avg",
    "item_avg_rating": "item_avg",
}


def _load_raw_tables() -> Dict[str, pd.DataFrame]:
    movies = pd.read_csv(CSV_FILES["movies"])
    ratings = pd.read_csv(CSV_FILES["ratings"])
    tags = pd.read_csv(CSV_FILES["tags"])
    links = pd.read_csv(CSV_FILES["links"])
    return {"movies": movies, "ratings": ratings, "tags": tags, "links": links}


def _check_upstream_preparation(input_path: str) -> None:
    summary_file = Path(input_path) / "preparation_summary.json"
    if summary_file.exists():
        logger.info("Upstream preparation summary found at %s", summary_file)
    else:
        logger.warning(
            "No preparation_summary.json found under %s; proceeding with raw "
            "canonical datasets (see module docstring for rationale).",
            input_path,
        )


def engineer_features(input_path: str, output_path: str) -> pd.DataFrame:
    """Engineer user, item and interaction features for the recommender.

    Args:
        input_path: Member 2's prepared-data directory (checked for
            lineage/gating; see module docstring for why raw tables,
            not this directory's CSVs, are the actual feature source).
        output_path: directory to write engineered feature tables to.

    Returns:
        The interaction-level engineered feature DataFrame (one row per
        rating event, joined with user/item summary stats and
        similarity/cross features).
    """
    _check_upstream_preparation(input_path)

    output_dir = Path(output_path)
    ensure_directory(output_dir)

    raw = _load_raw_tables()
    logger.info(
        "Loaded raw tables: %d ratings, %d movies, %d tags, %d links",
        len(raw["ratings"]), len(raw["movies"]), len(raw["tags"]), len(raw["links"]),
    )

    genre_matrix, genre_slugs, raw_genre_names = build_genre_matrix(raw["movies"])

    user_features = build_user_features(raw["ratings"], raw["tags"], genre_matrix, genre_slugs, raw_genre_names)
    item_features = build_item_features(
        raw["movies"], raw["ratings"], raw["tags"], raw["links"], genre_matrix, genre_slugs, raw_genre_names
    )
    interaction_features = build_interaction_features(
        raw["ratings"], user_features, item_features, genre_matrix, genre_slugs, raw_genre_names
    )

    feature_version = current_timestamp()
    computed_at = pd.Timestamp.now().isoformat()
    for df in (user_features, item_features, interaction_features):
        df["feature_version"] = feature_version
        df["computed_at"] = computed_at

    user_features.to_csv(output_dir / "user_features.csv", index=False)
    item_features.to_csv(output_dir / "item_features.csv", index=False)
    interaction_features.to_csv(output_dir / "interaction_features.csv", index=False)

    versioned_file = output_dir / f"engineered_features_{feature_version}.csv"
    interaction_features.to_csv(versioned_file, index=False)
    try:
        interaction_features.to_parquet(output_dir / f"engineered_features_{feature_version}.parquet", index=False)
    except (ImportError, ValueError) as exc:
        logger.info("Skipping parquet export (optional): %s", exc)

    # Backward-compatible flat file for Member 4's placeholder trainer.
    legacy = interaction_features.rename(columns=_LEGACY_COLUMN_MAP).copy()
    legacy["item_count"] = legacy["movieId"].map(item_features.set_index("movieId")["num_ratings"])
    legacy_cols = ["userId", "movieId", "rating", "user_avg", "item_avg", "item_count"]
    legacy_extra = [c for c in legacy.columns if c not in legacy_cols]
    legacy[legacy_cols + legacy_extra].to_csv(output_dir / "features.csv", index=False)

    logger.info(
        "Feature engineering complete: user_features=%s item_features=%s interaction_features=%s -> %s",
        user_features.shape, item_features.shape, interaction_features.shape, output_dir,
    )

    return interaction_features
