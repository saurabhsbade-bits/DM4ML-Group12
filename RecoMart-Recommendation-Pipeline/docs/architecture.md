# Architecture Diagram - RecoMart Recommendation Pipeline

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RecoMart Data Pipeline                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION LAYER                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │              Apache Airflow / Prefect DAG Scheduler                    │  │
│  │  - Weekly execution (Sunday 2 AM)                                      │  │
│  │  - Task dependency management                                         │  │
│  │  - Logging, monitoring, alerting                                      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                          CONNECTION LAYER                                    │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐│
│  │ CSV Files  │  │  REST APIs   │  │  Databases │  │  Cloud Storage (S3)  ││
│  │  (Local)   │  │ (External)   │  │  (MySQL)   │  │    (Optional)        ││
│  └────────────┘  └──────────────┘  └─────────────┘  └──────────────────────┘│
└──────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│              MEMBER 1: DATA INGESTION & STORAGE LAYER                        │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  • Fetch data from CSV and REST APIs                                  │  │
│  │  • Error handling and retry logic                                     │  │
│  │  • Data validation at ingestion                                       │  │
│  │  • Logging and audit trails                                          │  │
│  │  Output: data/raw/{source}/{type}/{timestamp}/                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│         MEMBER 2: DATA VALIDATION & PREPARATION LAYERS                       │
│  ┌────────────────┐          ┌───────────────┐                              │
│  │  Validation    │ ──────→  │  Preparation  │                              │
│  │                │          │               │                              │
│  │ • Schema check │          │ • Cleaning    │                              │
│  │ • Missing vals │  (DQ)    │ • Normaliztn │                              │
│  │ • Duplicates   │ Report   │ • Encoding    │                              │
│  │ • Range checks │          │ • EDA & plots │                              │
│  │                │          │               │                              │
│  │ Output:        │          │ Output:       │                              │
│  │ reports/       │          │ data/         │                              │
│  │ quality_*.pdf  │          │ processed/    │                              │
│  └────────────────┘          └───────────────┘                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│        MEMBER 3: FEATURE ENGINEERING & FEATURE STORE LAYERS                  │
│  ┌──────────────────────┐        ┌───────────────────────────────┐           │
│  │ Feature Engineering  │  ──→   │   Feature Store (Feast)       │           │
│  │                      │        │                               │           │
│  │ • User features      │        │ • Registry & versioning       │           │
│  │ • Item features      │        │ • Point-in-time queries       │           │
│  │ • Interaction feats  │        │ • Feature metadata            │           │
│  │ • Similarity metrics │        │ • Training/inference API      │           │
│  │                      │        │                               │           │
│  │ Output:              │        │ Output:                       │           │
│  │ data/features/       │        │ feature_store/registry/       │           │
│  │ transformed_*.csv    │        │ features_v*.json              │           │
│  └──────────────────────┘        └───────────────────────────────┘           │
└──────────────────────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│      MEMBER 4: MODEL TRAINING & EVALUATION LAYER                             │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  Training                          Evaluation                          │  │
│  │  ┌──────────────────────┐    ┌────────────────────────┐              │  │
│  │  │ Load features        │    │ Split train/test       │              │  │
│  │  │ Train model:         │    │ Compute metrics:       │              │  │
│  │  │  - Collab Filtering  │──→ │  - Precision@K         │──→ Dashboard│  │
│  │  │  - Content-Based     │    │  - Recall@K            │              │  │
│  │  │ Save model           │    │  - NDCG                │              │  │
│  │  │                      │    │ Track with MLflow      │              │  │
│  │  │ Output:              │    │                        │              │  │
│  │  │ mlruns/artifacts/    │    │ Output:                │              │  │
│  │  │ model_v*.pkl         │    │ reports/evaluation_*.pdf              │  │
│  │  └──────────────────────┘    └────────────────────────┘              │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│         MEMBER 5: ORCHESTRATION & DOCUMENTATION LAYER                        │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  • Airflow DAG orchestration (entire flow)                            │  │
│  │  • Task dependencies & error handling                                 │  │
│  │  • Logging & monitoring (structured logs, metrics)                    │  │
│  │  • Alerting (failure notifications, SLA checks)                       │  │
│  │  • Final documentation (architecture, runbook, final report)          │  │
│  │  • Demo video & submission package                                    │  │
│  │                                                                         │  │
│  │  Output:                                                              │  │
│  │  - airflow/dags/recom_pipeline.py (DAG orchestration)                │  │
│  │  - docs/architecture.md (this file)                                  │  │
│  │  - docs/runbook.md (operational guide)                               │  │
│  │  - reports/FINAL_REPORT.md (submission report)                       │  │
│  │  - demo_video.mp4 (5-10 min walkthrough)                             │  │
│  │  - submission.zip (all deliverables)                                 │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Raw Data Sources
    ↓
[INGESTION] → data/raw/
    ↓
[VALIDATION] → Validation Report
    ↓ (if passed)
[PREPARATION] → data/processed/
    ↓
[FEATURE ENGINEERING] → data/features/
    ↓
[FEATURE STORE] → feature_store/registry/
    ↓
[MODEL TRAINING] → mlruns/artifacts/
    ↓
[EVALUATION] → Evaluation Reports
    ↓
[DEPLOYMENT] → Ready for inference
```

## System Components

### 1. Data Layer

```
data/
├── raw/              # Ingested raw data (timestamp-partitioned)
│   ├── csv/
│   ├── api/
│   └── 2026-07-15/
├── processed/        # Validated and prepared data
│   ├── users.csv
│   ├── items.csv
│   └── interactions.csv
└── features/         # Engineered features for ML
    ├── user_features.csv
    ├── item_features.csv
    └── feature_vectors.parquet
```

### 2. Processing Layer

```
src/
├── ingestion/        # Member 1: Data collection
├── validation/       # Member 2: Quality checks
├── preparation/      # Member 2: Cleaning & EDA
├── features/         # Member 3: Feature engineering
└── models/           # Member 4: ML training
```

### 3. Orchestration Layer

```
airflow/
├── dags/
│   ├── recom_pipeline.py        # Main DAG
│   └── recom_pipeline_enhanced.py # With monitoring
├── monitoring.py                 # Logging & callbacks
├── alerts.py                     # Alerting system
├── logs/                         # Execution logs
└── requirements.txt              # Dependencies
```

### 4. Feature Store Layer

```
feature_store/
├── registry/         # Feature metadata
├── configs/          # Feast or custom config
└── .gitkeep
```

### 5. Model Layer

```
mlruns/
├── runs/            # MLflow experiment tracking
├── artifacts/       # Trained models
├── metrics/         # Evaluation metrics
└── .gitkeep
```

## Task Dependencies

```
pipeline_start
    ↓
ingestion_layer (ingest_data)
    ↓
validation_layer (validate_data)
    ↓
preparation_layer (prepare_data)
    ↓
feature_layer
    ├→ engineer_features
    └→ setup_feature_store (depends on engineer_features)
    ↓
model_layer (train_model)
    ↓
pipeline_end (trigger_rule: all_done)
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Orchestration** | Apache Airflow 2.7.3 |
| **Data Storage** | Local filesystem / CSV / Parquet |
| **Feature Store** | Feast (optional) or custom registry |
| **ML Framework** | scikit-learn (Collaborative Filtering) |
| **Experiment Tracking** | MLflow |
| **Logging** | Python logging + JSON structured logs |
| **Monitoring** | Custom PipelineMonitor + Airflow UI |
| **Alerting** | Email (SMTP) + Slack webhooks |
| **Language** | Python 3.10+ |

## Key Features

✅ **End-to-End Automation** - Weekly scheduled pipeline execution  
✅ **Error Handling** - Configurable retries and failure callbacks  
✅ **Data Lineage** - Track data sources through each stage  
✅ **Quality Checks** - Validation gates before downstream stages  
✅ **Feature Versioning** - Point-in-time feature retrieval  
✅ **Experiment Tracking** - MLflow integration for model runs  
✅ **Structured Logging** - JSON-formatted logs for easy parsing  
✅ **Alerting** - Real-time notifications on failures  
✅ **Reproducibility** - Data versioning with DVC and Git  
✅ **Modular Code** - Clear separation of concerns by member  

## Deployment Notes

1. Each member implements their module in `src/{stage}/`
2. Airflow calls module functions from DAG tasks
3. All data artifacts stored in local `data/` directory
4. Models saved to `mlruns/` for MLflow tracking
5. Logs saved to `airflow/logs/` with rotation
6. Alerts configured via email/Slack webhooks

## Future Enhancements

- [ ] Cloud storage integration (S3, GCS)
- [ ] Real-time ingestion (Kafka, Pub/Sub)
- [ ] GPU-accelerated model training
- [ ] A/B testing framework
- [ ] Model serving API (Flask/FastAPI)
- [ ] Advanced monitoring dashboards (Grafana)
- [ ] Distributed processing (Spark, Dask)
