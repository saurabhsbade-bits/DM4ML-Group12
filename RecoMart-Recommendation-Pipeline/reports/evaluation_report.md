# RecoMart Recommendation Model Evaluation Report

## 1. Model

**Algorithm:** Collaborative Filtering using Matrix Factorization (Truncated SVD)

---

## 2. Dataset

Dataset: ratings_processed.csv

- Total Ratings: 100,836
- Users: 610
- Movies: 9,724

Training/Test Split:
- Train: 80%
- Test: 20%

---

## 3. Hyperparameters

| Parameter | Value |
|-----------|-------|
| Algorithm | TruncatedSVD |
| Components | 50 |
| Top-K | 10 |
| Test Size | 0.2 |

---

## 4. Evaluation Metrics

| Metric | Value |
|---------|-------|
| Precision@10 | 0.2739 |
| Recall@10 | 0.1627 |
| NDCG@10 | 0.3185 |

---

## 5. Experiment Tracking

MLflow was used to track:

- Hyperparameters
- Evaluation Metrics
- Trained Model
- Source Code Version

---

## 6. DVC Versioning

Processed datasets were versioned using DVC.

Git was used to maintain data lineage and version history.

---

## 7. Conclusion

A collaborative filtering recommendation model based on Matrix Factorization (Truncated SVD) was successfully trained using the processed MovieLens ratings dataset.

The model achieved:

- Precision@10: 0.2739
- Recall@10: 0.1627
- NDCG@10: 0.3185

Processed datasets were versioned using DVC, while MLflow was used to track experiments, model parameters, evaluation metrics, and model artifacts, ensuring reproducibility of the recommendation pipeline.