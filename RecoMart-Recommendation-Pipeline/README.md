# 🎬 RecoMart Recommendation Pipeline

> **An End-to-End Data Management & MLOps Pipeline for Recommendation Systems**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)]()
[![MLflow](https://img.shields.io/badge/MLflow-Experiment%20Tracking-orange)]()
[![DVC](https://img.shields.io/badge/DVC-Data%20Versioning-purple)]()
[![Apache Airflow](https://img.shields.io/badge/Airflow-Orchestration-red)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

---

## 📌 Project Overview

RecoMart Recommendation Pipeline is an **end-to-end MLOps workflow** developed as part of the **Data Management for Machine Learning (DM4ML)** course at **BITS Pilani WILP**.

Name	                                        BITS Email ID	
Ajay Nath B	                        2025AA05210@wilp.bits-pilani.ac.in	
Anjali Bhardwaj	                        2025AA05214@wilp.bits-pilani.ac.in	
Saurabh Sudhir Bade	                2025aa05203@wilp.bits-Pilani.ac.in	
Rohit Aditya Rambhatla	                2025aa05205@wilp.bits-pilani.ac.in	
Prabhakaran S	                        2025aa05223@wilp.bits-pilani.ac.in	



The project demonstrates the complete lifecycle of a recommendation system, from multi-source data ingestion to model training, experiment tracking, feature management, and workflow orchestration.

The pipeline integrates modern MLOps technologies including:

- Apache Airflow
- MLflow
- Data Version Control (DVC)
- Custom Offline Feature Store
- TruncatedSVD Recommendation Model

---


The pipeline consists of the following stages:

```
MovieLens CSV
        +
 DummyJSON REST API
        │
        ▼
 Data Ingestion
        │
        ▼
 Data Validation
        │
        ▼
 Data Preparation
        │
        ▼
 Feature Engineering
        │
        ▼
 Versioned Feature Store
        │
        ▼
 Recommendation Model
        │
        ▼
 MLflow Experiment Tracking
        │
        ▼
 DVC Data Versioning
        │
        ▼
 Apache Airflow Orchestration
```

---

# 📂 Repository Structure

```
RecoMart-Recommendation-Pipeline
│
├── airflow/
│   ├── dags/
│   └── logs/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── reports/
│
├── dataset/
│
├── docs/
│
├── feature_store/
│
├── models/
│
├── reports/
│
├── scripts/
│
├── src/
│   ├── ingestion/
│   ├── validation/
│   ├── preparation/
│   ├── features/
│   ├── models/
│   └── utils/
│
├── dvc.yaml
├── processed.dvc
├── requirements.txt
└── README.md
```

---

# 📊 Dataset

The project uses two data sources:

### 🎥 MovieLens Dataset

- Movies
- Ratings
- Tags
- Links

Dataset:

https://grouplens.org/datasets/movielens/

### 🌐 REST API

DummyJSON Products API

https://dummyjson.com/products

---

# ⚙️ Features

## ✅ Multi-source Data Ingestion

- CSV ingestion
- REST API ingestion
- Retry mechanism
- Metadata generation
- Logging

---

## ✅ Data Validation

Automated validation includes:

- Schema validation
- Missing value checks
- Duplicate detection
- Data type validation
- Rating range validation

---

## ✅ Data Preparation

- Cleaning
- Normalization
- Formatting
- Processed dataset generation

---

## ✅ Exploratory Data Analysis

Includes:

- Rating distribution
- Top-rated movies
- User-item sparsity analysis

---

## ✅ Feature Engineering

Generated features include:

- User Features
- Movie Features
- Interaction Features
- Genre Features
- Temporal Features

---

## ✅ Offline Feature Store

Features are stored with version control.

Supports:

- Version registry
- Metadata
- Feature retrieval
- Point-in-time lookup

---

## ✅ Data Versioning (DVC)

DVC is used for:

- Dataset lineage
- Version control
- Pipeline reproducibility

---

## ✅ Recommendation Model

Collaborative Filtering using

**Truncated Singular Value Decomposition (TruncatedSVD)**

Evaluation Metrics

| Metric | Score |
|---------|------:|
| Precision@10 | **0.2739** |
| Recall@10 | **0.1627** |
| NDCG@10 | **0.3185** |

---

## ✅ MLflow

Experiment tracking includes:

- Parameters
- Metrics
- Artifacts
- Model Registry

---

## ✅ Apache Airflow

Pipeline orchestration includes:

- Data Ingestion
- Validation
- Preparation
- Feature Engineering
- Feature Store Setup
- Model Training

---



# 🛠️ Technology Stack

| Category | Technologies |
|-----------|--------------|
| Language | Python |
| Data Processing | Pandas, NumPy |
| Recommendation | Scikit-learn (TruncatedSVD) |
| Feature Store | Custom Offline Store |
| Versioning | DVC |
| Experiment Tracking | MLflow |
| Workflow | Apache Airflow |
| Visualization | Matplotlib |
| API | Requests |
| Logging | Python Logging |

---

# ▶️ Running the Project

## Install

```bash
git clone https://github.com/<your-username>/RecoMart-Recommendation-Pipeline.git

cd RecoMart-Recommendation-Pipeline

pip install -r requirements.txt
```

### Execute Complete Pipeline

```bash
python run_e2e.py
```

### Execute Airflow

```bash
airflow standalone
```

Open:

```
http://localhost:8080
```

---

# 📈 Results

The implemented pipeline successfully demonstrates:

- End-to-end automated workflow
- Multi-source ingestion
- Automated validation
- Versioned feature storage
- Dataset versioning
- Recommendation model training
- Experiment tracking
- Workflow orchestration

---

# 👥 Team

**Group 12**

Data Management for Machine Learning (DM4ML)

BITS Pilani WILP

---

# 📚 References

- MovieLens Dataset — https://grouplens.org/datasets/movielens/
- Apache Airflow — https://airflow.apache.org/
- MLflow — https://mlflow.org/
- DVC — https://dvc.org/
- Scikit-learn — https://scikit-learn.org/

---

# ⭐ Highlights

✔ End-to-End MLOps Pipeline

✔ Recommendation System

✔ Apache Airflow

✔ MLflow

✔ DVC

✔ Feature Store

✔ TruncatedSVD Recommendation Engine

✔ Reproducible Data Pipeline

✔ BITS Pilani DM4ML Assignment
