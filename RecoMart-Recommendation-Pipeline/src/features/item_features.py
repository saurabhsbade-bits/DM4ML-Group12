"""
Item (movie) feature engineering.

Builds one row per movie summarizing popularity, rating behaviour,
release metadata, external identifiers and a genre content vector.
Consumes the raw MovieLens `movies`, `ratings`, `tags` and `links`
tables plus the shared genre multi-hot matrix from
`common.build_genre_matrix`.
"""

import logging
from typing import List

import numpy as np
import pandas as pd

from src.features.common import percentile_rank

logger = logging.getLogger(__name__)

_YEAR_PATTERN = r"\((\d{4})\)\s*$"
_RECENT_FRACTION = 0.25
_MIN_RATINGS_FOR_TREND = 4
_NEW_RELEASE_WINDOW_YEARS = 3


def build_item_features(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    tags: pd.DataFrame,
    links: pd.DataFrame,
    genre_matrix: pd.DataFrame,
    genre_slugs: List[str],
    raw_genre_names: List[str],
) -> pd.DataFrame:
    """Build the item_features table.

    Returns:
        DataFrame indexed by movieId with popularity, rating-statistics,
        release/trend and `genre_<slug>` one-hot columns.
    """
    logger.info("Building item features for %d movies", movies["movieId"].nunique())

    features = movies[["movieId", "title", "genres"]].copy()
    features["release_year"] = features["title"].str.extract(_YEAR_PATTERN).astype("float")
    max_year = features["release_year"].max()
    features["item_age_years"] = max_year - features["release_year"]
    features["is_new_release"] = features["release_year"] >= (max_year - _NEW_RELEASE_WINDOW_YEARS)
    features.loc[features["release_year"].isna(), "is_new_release"] = False

    features["num_genres"] = features["genres"].fillna("(no genres listed)").str.split("|").apply(len)
    features["primary_genre"] = features["genres"].fillna("(no genres listed)").str.split("|").str[0]
    features = features.drop(columns=["genres"])

    genre_onehot = genre_matrix.copy()
    genre_onehot.columns = [f"genre_{slug}" for slug in genre_slugs]
    features = features.merge(genre_onehot, left_on="movieId", right_index=True, how="left")

    # --- Rating statistics / popularity -----------------------------------
    grouped = ratings.groupby("movieId")["rating"]
    rating_stats = pd.DataFrame({
        "num_ratings": grouped.count(),
        "avg_rating": grouped.mean(),
        "median_rating": grouped.median(),
        "rating_std": grouped.std().fillna(0.0),
    })
    features = features.merge(rating_stats, left_on="movieId", right_index=True, how="left")
    features[["num_ratings"]] = features[["num_ratings"]].fillna(0).astype(int)
    features["popularity_percentile"] = percentile_rank(features["num_ratings"])

    # --- Recency / trend: is this item rated better recently? -------------
    def _recent_avg(group: pd.DataFrame) -> float:
        n = max(1, int(len(group) * _RECENT_FRACTION)) if len(group) >= _MIN_RATINGS_FOR_TREND else len(group)
        return group.sort_values("timestamp").tail(n)["rating"].mean()

    recent_avg = ratings.groupby("movieId").apply(_recent_avg, include_groups=False)
    recent_avg.name = "recent_avg_rating"
    features = features.merge(recent_avg, left_on="movieId", right_index=True, how="left")
    features["rating_trend"] = features["recent_avg_rating"] - features["avg_rating"]

    # --- Tags ---------------------------------------------------------------
    if len(tags):
        tag_counts = tags.groupby("movieId")["tag"].count()
        top_tag = tags.groupby("movieId")["tag"].agg(lambda s: s.mode().iloc[0])
    else:
        tag_counts = pd.Series(dtype="int64")
        top_tag = pd.Series(dtype="object")
    features["num_tags"] = features["movieId"].map(tag_counts).fillna(0).astype(int)
    features["top_tag"] = features["movieId"].map(top_tag)

    # --- External identifiers -----------------------------------------------
    links_lookup = links.set_index("movieId")
    features["imdb_id"] = features["movieId"].map(links_lookup["imdbId"]) if "imdbId" in links.columns else np.nan
    features["tmdb_id"] = features["movieId"].map(links_lookup["tmdbId"]) if "tmdbId" in links.columns else np.nan

    logger.info("Item features built: %d rows, %d columns", len(features), features.shape[1])
    return features
