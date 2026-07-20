"""
RecoMart Recommendation Pipeline

Collaborative Filtering using Matrix Factorization (Truncated SVD)
Experiment Tracking using MLflow
"""

import logging
import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ==========================================================
# Configuration
# ==========================================================

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "ratings_processed.csv"

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_FILE = "svd_recommender.pkl"

TOP_K = 10
TEST_SIZE = 0.2
RANDOM_STATE = 42


# ==========================================================
# Metrics
# ==========================================================

def precision_recall_at_k(actual, predicted, k=10):

    precision_scores = []
    recall_scores = []

    for user in actual.keys():

        actual_items = set(actual[user])

        predicted_items = predicted.get(user, [])[:k]

        if len(predicted_items) == 0:
            continue

        hits = len(actual_items.intersection(predicted_items))

        precision_scores.append(hits / k)

        recall_scores.append(hits / len(actual_items))

    precision = np.mean(precision_scores) if precision_scores else 0
    recall = np.mean(recall_scores) if recall_scores else 0

    return precision, recall


def ndcg_at_k(actual, predicted, k=10):

    ndcg_scores = []

    for user in actual.keys():

        actual_items = set(actual[user])

        predicted_items = predicted.get(user, [])[:k]

        dcg = 0

        for rank, item in enumerate(predicted_items):

            if item in actual_items:
                dcg += 1 / np.log2(rank + 2)

        ideal_dcg = sum(
            1 / np.log2(i + 2)
            for i in range(min(len(actual_items), k))
        )

        if ideal_dcg == 0:
            continue

        ndcg_scores.append(dcg / ideal_dcg)

    return np.mean(ndcg_scores) if ndcg_scores else 0


# ==========================================================
# Training Entry Point
# ==========================================================

def train_svd_model(
    data_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    top_k: int = TOP_K,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> Dict[str, Any]:
    """Train the real Member 4 collaborative-filtering model (TruncatedSVD).

    Loads `ratings_processed.csv` (produced by `src.validation.prepare_data`
    and DVC-tracked), builds a user-item interaction matrix, fits a
    TruncatedSVD model, evaluates it with Precision/Recall/NDCG@K, saves the
    model + id mappings to `output_dir/svd_recommender.pkl`, and (best
    effort) logs the run to MLflow.

    Args:
        data_path: Path to the processed ratings CSV. Defaults to
            `data/processed/ratings_processed.csv` under the project root.
            If missing, run `dvc pull` (or `python -m src.validation` /
            the DAG's preparation stage) to (re)generate it.
        output_dir: Directory to save the trained model to. Defaults to
            `models/` under the project root.
        top_k: K used for Precision/Recall/NDCG@K.
        test_size: Fraction of interactions held out for evaluation.
        random_state: Random seed for the train/test split and TruncatedSVD.

    Returns:
        Dict with status, model_path and metrics (precision_at_k, recall_at_k,
        ndcg_at_k, n_components, train_rows, test_rows).
    """
    data_file = Path(data_path) if data_path else DATA_PATH
    out_dir = Path(output_dir) if output_dir else MODEL_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    if not data_file.exists():
        raise FileNotFoundError(
            f"{data_file} not found. This file is produced by "
            "src.validation.prepare_data() and versioned with DVC. "
            "Run the preparation stage (or `dvc pull`) before training."
        )

    logger.info(f"Loading ratings from {data_file}")
    ratings = pd.read_csv(data_file)
    logger.info(f"Ratings shape: {ratings.shape}")

    # IDs may have been normalized by preprocessing. Recreate integer
    # indices while preserving uniqueness.
    ratings["user_idx"], user_mapping = pd.factorize(ratings["userId"])
    ratings["movie_idx"], movie_mapping = pd.factorize(ratings["movieId"])

    train_df, test_df = train_test_split(
        ratings,
        test_size=test_size,
        random_state=random_state,
    )
    logger.info(f"Train rows: {len(train_df)}, Test rows: {len(test_df)}")

    # User-item interaction matrix
    interaction_matrix = train_df.pivot_table(
        index="user_idx",
        columns="movie_idx",
        values="rating",
        fill_value=0,
    )
    matrix = csr_matrix(interaction_matrix.values)

    # Train TruncatedSVD
    n_components = min(50, matrix.shape[0] - 1, matrix.shape[1] - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=random_state)
    latent_matrix = svd.fit_transform(matrix)
    reconstructed = latent_matrix @ svd.components_

    prediction_matrix = pd.DataFrame(
        reconstructed,
        index=interaction_matrix.index,
        columns=interaction_matrix.columns,
    )

    # Ground truth + recommendations
    actual = test_df.groupby("user_idx")["movie_idx"].apply(list).to_dict()

    predicted = {}
    for user in actual.keys():
        if user not in prediction_matrix.index:
            continue

        already_seen = set(
            train_df.loc[train_df.user_idx == user, "movie_idx"]
        )

        recommendations = (
            prediction_matrix
            .loc[user]
            .drop(labels=list(already_seen), errors="ignore")
            .sort_values(ascending=False)
            .head(top_k)
            .index
            .tolist()
        )
        predicted[user] = recommendations

    precision, recall = precision_recall_at_k(actual, predicted, top_k)
    ndcg = ndcg_at_k(actual, predicted, top_k)

    logger.info(
        f"Precision@{top_k}: {precision:.4f}, Recall@{top_k}: {recall:.4f}, "
        f"NDCG@{top_k}: {ndcg:.4f}"
    )

    # Save model
    model_path = out_dir / MODEL_FILE
    with open(model_path, "wb") as f:
        pickle.dump(
            {
                "model": svd,
                "user_mapping": user_mapping,
                "movie_mapping": movie_mapping,
            },
            f,
        )
    logger.info(f"Model saved to {model_path}")

    metrics = {
        "precision_at_10": float(precision),
        "recall_at_10": float(recall),
        "ndcg_at_10": float(ndcg),
        "n_components": int(n_components),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
    }

    # Best-effort MLflow logging: must never fail the training run just
    # because no tracking server is configured/reachable.
    try:
        import mlflow
        import mlflow.sklearn

        mlflow.set_experiment("RecoMart Recommendation")
        with mlflow.start_run():
            mlflow.log_param("algorithm", "TruncatedSVD")
            mlflow.log_param("n_components", n_components)
            mlflow.log_param("top_k", top_k)
            mlflow.log_param("test_size", test_size)
            mlflow.log_metric("precision_at_10", float(precision))
            mlflow.log_metric("recall_at_10", float(recall))
            mlflow.log_metric("ndcg_at_10", float(ndcg))
            mlflow.sklearn.log_model(svd, artifact_path="recommendation_model")
        logger.info("MLflow run complete")
    except Exception as e:
        logger.warning(f"MLflow logging skipped: {e}")

    return {
        "status": "success",
        "model_path": str(model_path),
        "metrics": metrics,
    }


if __name__ == "__main__":
    result = train_svd_model()
    print("=" * 60)
    print("Training Complete")
    print("=" * 60)
    print(result)