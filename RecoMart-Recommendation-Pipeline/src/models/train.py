"""
RecoMart Recommendation Pipeline

Collaborative Filtering using Matrix Factorization (Truncated SVD)
Experiment Tracking using MLflow
"""

import os
import pickle
import warnings

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")


# ==========================================================
# Configuration
# ==========================================================

DATA_PATH = "data/processed/ratings_processed.csv"

MODEL_DIR = "models"
MODEL_FILE = "svd_recommender.pkl"

TOP_K = 10
TEST_SIZE = 0.2
RANDOM_STATE = 42

os.makedirs(MODEL_DIR, exist_ok=True)


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
# Load Dataset
# ==========================================================

print("=" * 60)
print("Loading Dataset")
print("=" * 60)

ratings = pd.read_csv(DATA_PATH)

print(ratings.head())

print("\nShape:", ratings.shape)

print("\nOriginal Unique Users :", ratings["userId"].nunique())
print("Original Unique Movies:", ratings["movieId"].nunique())


# ==========================================================
#
# IDs were normalized by preprocessing.
# Recreate integer indices while preserving uniqueness.
#
# ==========================================================

ratings["user_idx"], user_mapping = pd.factorize(ratings["userId"])

ratings["movie_idx"], movie_mapping = pd.factorize(ratings["movieId"])

print("\nAfter Factorization")

print("Users :", ratings["user_idx"].nunique())
print("Movies:", ratings["movie_idx"].nunique())


# ==========================================================
# Train Test Split
# ==========================================================

train_df, test_df = train_test_split(
    ratings,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
)

print("\nTrain:", len(train_df))
print("Test :", len(test_df))


# ==========================================================
# User Item Matrix
# ==========================================================

interaction_matrix = train_df.pivot_table(
    index="user_idx",
    columns="movie_idx",
    values="rating",
    fill_value=0,
)

matrix = csr_matrix(interaction_matrix.values)

print("\nInteraction Matrix Shape")

print(matrix.shape)


# ==========================================================
# Train Model
# ==========================================================

print("\nTraining Truncated SVD...")

n_components = min(
    50,
    matrix.shape[0] - 1,
    matrix.shape[1] - 1,
)

svd = TruncatedSVD(
    n_components=n_components,
    random_state=RANDOM_STATE,
)

latent_matrix = svd.fit_transform(matrix)

reconstructed = latent_matrix @ svd.components_

prediction_matrix = pd.DataFrame(
    reconstructed,
    index=interaction_matrix.index,
    columns=interaction_matrix.columns,
)

print("Training Complete")


# ==========================================================
# Prepare Ground Truth
# ==========================================================

actual = (
    test_df
    .groupby("user_idx")["movie_idx"]
    .apply(list)
    .to_dict()
)

predicted = {}

for user in actual.keys():

    if user not in prediction_matrix.index:
        continue

    already_seen = set(
        train_df.loc[
            train_df.user_idx == user,
            "movie_idx"
        ]
    )

    recommendations = (
        prediction_matrix
        .loc[user]
        .drop(labels=list(already_seen), errors="ignore")
        .sort_values(ascending=False)
        .head(TOP_K)
        .index
        .tolist()
    )

    predicted[user] = recommendations


# ==========================================================
# Evaluation
# ==========================================================

precision, recall = precision_recall_at_k(
    actual,
    predicted,
    TOP_K,
)

ndcg = ndcg_at_k(
    actual,
    predicted,
    TOP_K,
)

print("\n")
print("=" * 60)
print("Evaluation")
print("=" * 60)

print(f"Precision@{TOP_K}: {precision:.4f}")
print(f"Recall@{TOP_K}:    {recall:.4f}")
print(f"NDCG@{TOP_K}:      {ndcg:.4f}")


# ==========================================================
# Save Model
# ==========================================================

model_path = os.path.join(
    MODEL_DIR,
    MODEL_FILE,
)

with open(model_path, "wb") as f:
    pickle.dump(
        {
            "model": svd,
            "user_mapping": user_mapping,
            "movie_mapping": movie_mapping,
        },
        f,
    )

print("\nModel Saved")

print(model_path)


# ==========================================================
# MLflow
# ==========================================================

print("\nLogging to MLflow...")

mlflow.set_experiment("RecoMart Recommendation")

with mlflow.start_run():
    mlflow.log_param("algorithm", "TruncatedSVD")
    mlflow.log_param("n_components", n_components)
    mlflow.log_param("top_k", TOP_K)
    mlflow.log_param("test_size", TEST_SIZE)

    mlflow.log_metric(
        "precision_at_10",
        float(precision),
    )

    mlflow.log_metric(
        "recall_at_10",
        float(recall),
    )

    mlflow.log_metric(
        "ndcg_at_10",
        float(ndcg),
    )

    mlflow.sklearn.log_model(
        svd,
        artifact_path="recommendation_model",
    )

print("MLflow Run Complete")

print("\nDone")