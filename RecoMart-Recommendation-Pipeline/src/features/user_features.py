"""
User feature engineering.

Builds one row per user summarizing activity, rating behaviour, temporal
patterns and a genre preference vector derived from the movies the user
has rated. Consumes the raw MovieLens `ratings`, `movies` and `tags`
tables (see `src/features/__init__.py` for why raw tables are used
instead of Member 2's scaled `data/processed` output) plus the shared
genre multi-hot matrix from `common.build_genre_matrix`.
"""

import logging
from typing import List

import numpy as np
import pandas as pd

from src.features.common import shannon_entropy, percentile_rank

logger = logging.getLogger(__name__)


def build_user_features(
    ratings: pd.DataFrame,
    tags: pd.DataFrame,
    genre_matrix: pd.DataFrame,
    genre_slugs: List[str],
    raw_genre_names: List[str],
) -> pd.DataFrame:
    """Build the user_features table.

    Args:
        ratings: raw ratings with columns userId, movieId, rating, timestamp
        tags: raw tags with columns userId, movieId, tag, timestamp
        genre_matrix: movieId x genre multi-hot matrix (see common.build_genre_matrix)
        genre_slugs: SQL/CSV-safe genre column names, same order as raw_genre_names
        raw_genre_names: raw MovieLens genre labels, same order as genre_slugs

    Returns:
        DataFrame indexed by userId with activity, rating-statistics,
        temporal and `pref_<genre>` preference columns.
    """
    logger.info("Building user features for %d users", ratings["userId"].nunique())

    grouped = ratings.groupby("userId")["rating"]
    features = pd.DataFrame({
        "num_ratings": grouped.count(),
        "avg_rating": grouped.mean(),
        "median_rating": grouped.median(),
        "rating_std": grouped.std().fillna(0.0),
        "min_rating": grouped.min(),
        "max_rating": grouped.max(),
    })

    # --- Temporal activity patterns -------------------------------------
    dt = pd.to_datetime(ratings["timestamp"], unit="s")
    hour_mode = dt.dt.hour.groupby(ratings["userId"]).agg(lambda s: s.mode().iloc[0])
    dow_mode = dt.dt.dayofweek.groupby(ratings["userId"]).agg(lambda s: s.mode().iloc[0])
    features["most_active_hour"] = hour_mode
    features["most_active_dow"] = dow_mode

    span_days = dt.groupby(ratings["userId"]).agg(lambda s: (s.max() - s.min()).total_seconds() / 86400.0)
    features["activity_span_days"] = span_days
    features["avg_days_between_ratings"] = np.where(
        features["num_ratings"] > 1,
        features["activity_span_days"] / (features["num_ratings"] - 1).replace(0, np.nan),
        0.0,
    )
    features["avg_days_between_ratings"] = features["avg_days_between_ratings"].fillna(0.0)

    # --- Genre affinity: per-user rated-movie x genre multi-hot ---------
    merged = ratings[["userId", "movieId", "rating"]].merge(
        genre_matrix, left_on="movieId", right_index=True, how="left"
    )

    weighted_genres = merged[raw_genre_names].multiply(merged["rating"], axis=0)
    genre_rating_sum = weighted_genres.groupby(merged["userId"]).sum()
    genre_count = merged[raw_genre_names].groupby(merged["userId"]).sum()

    with np.errstate(invalid="ignore", divide="ignore"):
        genre_avg_rating = genre_rating_sum / genre_count.replace(0, np.nan)

    # Cold-start fallback: genres the user never rated get their own
    # overall average rating as a neutral prior instead of NaN/0.
    genre_avg_rating = genre_avg_rating.apply(lambda col: col.fillna(features["avg_rating"]))
    genre_avg_rating.columns = [f"pref_{slug}" for slug in genre_slugs]
    features = features.join(genre_avg_rating)

    # --- Top genre + genre diversity -------------------------------------
    features["num_distinct_genres_rated"] = (genre_count > 0).sum(axis=1)
    top_genre_idx = genre_count.values.argmax(axis=1)
    features["top_genre"] = [raw_genre_names[i] for i in top_genre_idx]
    genre_count_totals = genre_count.sum(axis=1).replace(0, np.nan)
    features["top_genre_share"] = (genre_count.values.max(axis=1) / genre_count_totals.values)
    features["top_genre_share"] = features["top_genre_share"].fillna(0.0)
    features["genre_entropy"] = genre_count.apply(shannon_entropy, axis=1)

    # --- Tags authored ----------------------------------------------------
    if len(tags):
        tag_counts = tags.groupby("userId")["tag"].count()
    else:
        tag_counts = pd.Series(dtype="int64")
    features["num_tags_given"] = tag_counts.reindex(features.index).fillna(0).astype(int)

    # --- Cross-user activity percentile (used by similarity features) ----
    features["activity_percentile"] = percentile_rank(features["num_ratings"])

    features.index.name = "userId"
    features = features.reset_index()
    logger.info("User features built: %d rows, %d columns", len(features), features.shape[1])
    return features
