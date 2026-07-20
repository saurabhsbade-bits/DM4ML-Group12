"""
Interaction, similarity and cross features.

Builds one row per rating event (interaction) with recency/frequency
signals plus a set of similarity-derived and cross features:

- user-user collaborative similarity (cosine over the rating matrix)
- item-item content similarity (cosine over the genre multi-hot matrix)
- a simple collaborative-filtering "predicted rating" from the user's
  nearest neighbours
- cross features combining user/item statistics (avg-rating product,
  genre affinity, popularity x recency, activity x popularity)

Implemented with plain numpy/pandas (no scikit-learn/scipy dependency)
so it stays lightweight and portable; dataset sizes here (~600 users,
~10K items, ~100K interactions) are small enough for dense numpy ops.
"""

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

TOP_K_NEIGHBORS = 5
ITEM_SIMILARITY_CHUNK_SIZE = 1000
RECENCY_DECAY_DAYS = 365.0


def _cosine_similarity_dense(matrix: np.ndarray) -> np.ndarray:
    """Row-wise cosine similarity of a dense matrix (n x d) -> (n x n)."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = matrix / norms
    return normalized @ normalized.T


def _top_k_neighbors(similarity: np.ndarray, ids: np.ndarray, k: int) -> Dict:
    """For each row, return up to k (neighbor_id, score) pairs excluding self,
    sorted by descending similarity."""
    neighbors: Dict = {}
    n = similarity.shape[0]
    k = min(k, n - 1) if n > 1 else 0
    for i in range(n):
        row = similarity[i].copy()
        row[i] = -np.inf
        if k == 0:
            neighbors[ids[i]] = []
            continue
        top_idx = np.argpartition(row, -k)[-k:]
        top_idx = top_idx[np.argsort(-row[top_idx])]
        neighbors[ids[i]] = [(ids[j], float(row[j])) for j in top_idx if np.isfinite(row[j])]
    return neighbors


def compute_user_user_similarity(ratings: pd.DataFrame, k: int = TOP_K_NEIGHBORS) -> Dict:
    """Cosine similarity between users over their (movie -> rating) vectors.

    Returns: {user_id: [(neighbor_user_id, similarity), ...]} (top-k, desc).
    """
    logger.info("Computing user-user similarity")
    pivot = ratings.pivot_table(index="userId", columns="movieId", values="rating", fill_value=0.0)
    user_ids = pivot.index.values
    similarity = _cosine_similarity_dense(pivot.values)
    return _top_k_neighbors(similarity, user_ids, k), pivot


def compute_item_content_similarity(genre_matrix: pd.DataFrame, k: int = 1) -> Dict:
    """Cosine similarity between items over their genre multi-hot vectors,
    computed in chunks to avoid materializing the full (n_items x n_items)
    matrix in memory.

    Returns: {movie_id: [(neighbor_movie_id, similarity), ...]} (top-k, desc).
    """
    logger.info("Computing item-item content similarity for %d items", len(genre_matrix))
    ids = genre_matrix.index.values
    values = genre_matrix.values.astype("float64")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = values / norms

    neighbors: Dict = {}
    n = len(ids)
    for start in range(0, n, ITEM_SIMILARITY_CHUNK_SIZE):
        end = min(start + ITEM_SIMILARITY_CHUNK_SIZE, n)
        batch_similarity = normalized[start:end] @ normalized.T
        for local_i, global_i in enumerate(range(start, end)):
            row = batch_similarity[local_i].copy()
            row[global_i] = -np.inf
            top_idx = np.argpartition(row, -k)[-k:]
            top_idx = top_idx[np.argsort(-row[top_idx])]
            neighbors[ids[global_i]] = [(ids[j], float(row[j])) for j in top_idx if np.isfinite(row[j])]
    return neighbors


def _cf_predicted_ratings(
    ratings: pd.DataFrame,
    user_neighbors: Dict,
    item_avg_lookup: pd.Series,
) -> np.ndarray:
    """Weighted-average rating of each user's nearest neighbours for the
    same movie; falls back to the item's overall average when no neighbour
    has rated it."""
    rating_lookup = {
        (u, m): r for u, m, r in zip(ratings["userId"], ratings["movieId"], ratings["rating"])
    }
    predictions = np.empty(len(ratings), dtype="float64")
    for idx, (user_id, movie_id) in enumerate(zip(ratings["userId"].values, ratings["movieId"].values)):
        weighted_sum, weight_total = 0.0, 0.0
        for neighbor_id, similarity in user_neighbors.get(user_id, []):
            neighbor_rating = rating_lookup.get((neighbor_id, movie_id))
            if neighbor_rating is not None and similarity > 0:
                weighted_sum += similarity * neighbor_rating
                weight_total += similarity
        if weight_total > 0:
            predictions[idx] = weighted_sum / weight_total
        else:
            predictions[idx] = item_avg_lookup.get(movie_id, ratings["rating"].mean())
    return predictions


def build_interaction_features(
    ratings: pd.DataFrame,
    user_features: pd.DataFrame,
    item_features: pd.DataFrame,
    genre_matrix: pd.DataFrame,
    genre_slugs: List[str],
    raw_genre_names: List[str],
) -> pd.DataFrame:
    """Build the interaction_features table: one row per rating event with
    recency/frequency features plus similarity-derived and cross features.
    """
    logger.info("Building interaction features for %d ratings", len(ratings))

    interactions = ratings.copy().reset_index(drop=True)
    interactions["interaction_id"] = interactions.index.astype("int64")

    # --- Recency / frequency -------------------------------------------
    max_ts = interactions["timestamp"].max()
    interactions["event_datetime"] = pd.to_datetime(interactions["timestamp"], unit="s")
    interactions["recency_days"] = (max_ts - interactions["timestamp"]) / 86400.0

    interactions = interactions.sort_values(["userId", "timestamp"]).reset_index(drop=True)
    interactions["user_interaction_seq_num"] = interactions.groupby("userId").cumcount() + 1
    interactions["days_since_user_prev_rating"] = (
        interactions.groupby("userId")["timestamp"].diff() / 86400.0
    )

    # --- Join user / item summary stats ----------------------------------
    user_lookup = user_features.set_index("userId")
    item_lookup = item_features.set_index("movieId")

    interactions = interactions.merge(
        user_lookup[["avg_rating", "activity_percentile"]].rename(
            columns={"avg_rating": "user_avg_rating", "activity_percentile": "user_activity_percentile"}
        ),
        left_on="userId", right_index=True, how="left",
    )
    interactions = interactions.merge(
        item_lookup[["avg_rating", "popularity_percentile", "num_genres"]].rename(
            columns={"avg_rating": "item_avg_rating", "popularity_percentile": "item_popularity_percentile"}
        ),
        left_on="movieId", right_index=True, how="left",
    )

    interactions["rating_dev_from_user_avg"] = interactions["rating"] - interactions["user_avg_rating"]
    interactions["rating_dev_from_item_avg"] = interactions["rating"] - interactions["item_avg_rating"]
    interactions["user_item_cross_rating"] = interactions["user_avg_rating"] * interactions["item_avg_rating"]
    interactions["user_activity_x_item_popularity"] = (
        interactions["user_activity_percentile"] * interactions["item_popularity_percentile"]
    )
    interactions["item_trending_score"] = interactions["item_popularity_percentile"] * np.exp(
        -interactions["recency_days"] / RECENCY_DECAY_DAYS
    )

    # --- User genre affinity for the rated item's genre mix ---------------
    pref_cols = [f"pref_{slug}" for slug in genre_slugs]
    user_pref_matrix = user_lookup[pref_cols].reindex(interactions["userId"].values).values
    item_genre_onehot = genre_matrix.reindex(interactions["movieId"].values).fillna(0).values
    num_genres = interactions["num_genres"].replace(0, np.nan).values
    affinity = (user_pref_matrix * item_genre_onehot).sum(axis=1) / num_genres
    interactions["user_genre_affinity_for_item"] = np.nan_to_num(affinity, nan=0.0)
    interactions = interactions.drop(columns=["num_genres"])

    # --- Similarity-derived features ---------------------------------------
    user_neighbors, _ = compute_user_user_similarity(ratings)
    item_neighbors = compute_item_content_similarity(genre_matrix, k=1)

    top1_user_id = {u: (n[0][0] if n else np.nan) for u, n in user_neighbors.items()}
    top1_user_sim = {u: (n[0][1] if n else np.nan) for u, n in user_neighbors.items()}
    interactions["top_similar_user_id"] = interactions["userId"].map(top1_user_id)
    interactions["top_similar_user_similarity"] = interactions["userId"].map(top1_user_sim)

    top1_item_id = {m: (n[0][0] if n else np.nan) for m, n in item_neighbors.items()}
    top1_item_sim = {m: (n[0][1] if n else np.nan) for m, n in item_neighbors.items()}
    interactions["top_similar_item_id"] = interactions["movieId"].map(top1_item_id)
    interactions["top_similar_item_similarity"] = interactions["movieId"].map(top1_item_sim)

    item_avg_lookup = item_lookup["avg_rating"]
    interactions["cf_predicted_rating"] = _cf_predicted_ratings(interactions, user_neighbors, item_avg_lookup)

    logger.info("Interaction features built: %d rows, %d columns", len(interactions), interactions.shape[1])
    return interactions
