"""
Model Training & Evaluation Module (Member 4)

Responsibilities:
- Train recommendation models (Collaborative Filtering / Content-Based)
- Evaluate using Precision@K, Recall@K, NDCG
- Track experiments with MLflow
- Save and version trained models
"""


import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def train_model(
    features_path: str,
    output_path: str,
    model_type: str = "collaborative_filtering",
) -> Dict[str, Any]:
    """Train the RecoMart recommendation model.

    For `model_type="collaborative_filtering"` (the default, used by the
    DAG), this trains the real Member 4 TruncatedSVD model
    (`src.models.train.train_svd_model`) on the DVC-tracked
    `data/processed/ratings_processed.csv`, saving `svd_recommender.pkl`
    to `output_path` and returning Precision/Recall/NDCG@10 metrics.

    For `model_type="baseline"`, a lightweight LinearRegression baseline is
    trained instead, using `features.csv` from `features_path`. This is
    kept for quick smoke tests where the full ratings dataset may not be
    available.
    """
    if model_type == "baseline":
        return _train_baseline_model(features_path, output_path)

    from src.models.train import train_svd_model

    return train_svd_model(output_dir=output_path)


def _train_baseline_model(features_path: str, output_path: str) -> Dict[str, Any]:
    """Lightweight LinearRegression baseline (fallback / smoke-test model).

    Loads `features.csv` from `features_path`, trains a small
    linear regression using `user_avg` and `item_avg` to predict
    `rating`, saves the model and returns basic metrics (RMSE).
    """
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error
    import joblib

    feat_dir = Path(features_path)
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    features_file = feat_dir / "features.csv"
    if not features_file.exists():
        raise FileNotFoundError(f"features.csv not found in {feat_dir}")

    df = pd.read_csv(features_file)

    # Ensure required columns
    for col in ["user_avg", "item_avg", "rating"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column in features: {col}")

    X = df[["user_avg", "item_avg"]].fillna(0)
    y = df["rating"].fillna(df["rating"].mean())

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    # Compute RMSE manually to avoid compatibility issues with sklearn versions
    mse = ((y_test - preds) ** 2).mean()
    rmse = float(mse ** 0.5)

    model_file = out_dir / "baseline_model.joblib"
    joblib.dump(model, model_file)

    metrics = {"rmse": float(rmse), "train_rows": int(X_train.shape[0]), "test_rows": int(X_test.shape[0])}

    logger.info(f"Model trained and persisted to {model_file} (RMSE={rmse:.4f})")

    return {"status": "success", "model_path": str(model_file), "metrics": metrics}


def evaluate_model(
    model_path: str,
    test_data: pd.DataFrame,
    k_values: list = [5, 10, 20]
) -> Dict[str, float]:
    """
    Evaluate model using Precision@K, Recall@K, NDCG.
    
    Args:
        model_path: Path to trained model
        test_data: Test dataset for evaluation
        k_values: List of K values for evaluation
        
    Returns:
        Dict with evaluation metrics
    """
    logger.info(f"Evaluating model with k_values: {k_values}")
    # TODO: Implement evaluation
    # - Load trained model
    # - Generate recommendations on test set
    # - Compute Precision@K for each K
    # - Compute Recall@K for each K
    # - Compute NDCG
    # - Return metrics dict
    raise NotImplementedError("Member 4: Implement evaluation")


def track_experiment(
    experiment_name: str,
    model_name: str,
    params: Dict[str, Any],
    metrics: Dict[str, float],
    artifacts_path: Optional[str] = None
) -> str:
    """
    Track experiment metadata with MLflow.
    
    Args:
        experiment_name: Name of the experiment
        model_name: Name of the trained model
        params: Model hyperparameters
        metrics: Evaluation metrics
        artifacts_path: Optional path to model artifacts
        
    Returns:
        MLflow run ID
    """
    logger.info(f"Tracking experiment: {experiment_name}")
    # TODO: Implement MLflow tracking
    # - Create/get experiment
    # - Start MLflow run
    # - Log parameters
    # - Log metrics
    # - Log model artifacts
    # - End run and return run ID
    raise NotImplementedError("Member 4: Implement MLflow tracking")


def generate_evaluation_report(
    metrics: Dict[str, float],
    output_path: str
) -> None:
    """
    Generate model evaluation report.
    
    Args:
        metrics: Evaluation metrics
        output_path: Path to save report
    """
    logger.info(f"Generating evaluation report and saving to {output_path}")
    # TODO: Create evaluation report
    # - Summarize metrics
    # - Create visualizations
    # - Generate PDF report
    # - Save to output_path
    raise NotImplementedError("Member 4: Generate evaluation report")
