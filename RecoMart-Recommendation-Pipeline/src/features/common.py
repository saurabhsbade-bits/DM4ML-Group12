"""
Shared helpers for the feature engineering module.

Centralizes the genre vocabulary / multi-hot matrix construction and a
couple of small numeric helpers reused by the user, item and
interaction/similarity feature builders so the three stay consistent
(e.g. the same genre column ordering everywhere).
"""

import re
from typing import List, Tuple

import numpy as np
import pandas as pd

RATING_SCALE_MAX = 5.0


def slugify_genre(genre: str) -> str:
    """Turn a raw MovieLens genre label into a safe column-name fragment.

    "Sci-Fi" -> "sci_fi", "(no genres listed)" -> "no_genres_listed"
    """
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", genre.strip().lower())
    return slug.strip("_")


def build_genre_matrix(movies: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Build a multi-hot (movieId x genre) matrix from the pipe-separated
    `genres` column in the raw MovieLens `movies.csv`.

    Returns:
        (genre_matrix, genre_slugs, raw_genre_names) where genre_matrix is
        indexed by movieId with one 0/1 column per genre (column names are
        the raw genre labels; use `genre_slugs` for SQL/CSV-safe names in
        the same order).
    """
    genre_lists = movies["genres"].fillna("(no genres listed)").str.split("|")
    all_genres = sorted({g for genres in genre_lists for g in genres})
    slugs = [slugify_genre(g) for g in all_genres]

    matrix = pd.DataFrame(
        0,
        index=movies["movieId"].values,
        columns=all_genres,
        dtype="int8",
    )
    for movie_id, genres in zip(movies["movieId"].values, genre_lists):
        matrix.loc[movie_id, genres] = 1

    matrix.index.name = "movieId"
    return matrix, slugs, all_genres


def shannon_entropy(counts: pd.Series) -> float:
    """Shannon entropy (base 2) of a distribution given as raw counts.

    Returns 0.0 for an empty or single-category distribution.
    """
    total = counts.sum()
    if total <= 0:
        return 0.0
    probs = counts[counts > 0] / total
    if len(probs) <= 1:
        return 0.0
    return float(-(probs * np.log2(probs)).sum())


def percentile_rank(series: pd.Series) -> pd.Series:
    """Rank a series into a [0, 1] percentile (higher value -> higher rank)."""
    if len(series) <= 1:
        return pd.Series(1.0, index=series.index)
    return series.rank(pct=True, method="average")
