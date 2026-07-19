# Airflow Orchestration - RecoMart Pipeline

This directory contains the Apache Airflow DAG and orchestration setup for the RecoMart recommendation pipeline.

## Structure

```
airflow/
├── dags/
│   ├── __init__.py
│   └── recom_pipeline.py       # Main DAG with all pipeline stages
├── logs/                        # Airflow task logs
├── requirements.txt             # Python dependencies
├── config_template.env          # Configuration template
├── README.md                    # This file
└── .gitkeep
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r airflow/requirements.txt
```

### 2. Initialize Airflow Database

```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
```

### 3. Create Airflow Admin User
```bash
airflow users create \
    --username admin \
    --password admin123 \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@recomart.com
```

### 4. Start Airflow Services

**Terminal 1: Airflow Webserver**
```bash
airflow webserver --port 8080
```

**Terminal 2: Airflow Scheduler**
```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow scheduler
```

### 5. Access Airflow UI

Navigate to: http://localhost:8080
- Username: `admin`
- Password: `admin123`

## DAG: `recom_pipeline`

### Schedule
- **Interval:** Weekly (Sunday at 2 AM UTC)
- **Retries:** 2 attempts per task
- **Retry Delay:** 5 minutes

### Pipeline Stages

1. **Ingestion Layer** (`ingest_data`)
   - Calls Member 1's data ingestion module
   - Stores raw data with timestamp partitioning

2. **Validation Layer** (`validate_data`)
   - Calls Member 2's validation module
   - Generates data quality report

3. **Preparation Layer** (`prepare_data`)
   - Calls Member 2's data preparation module
   - Performs EDA and cleaning

4. **Feature Layer** (`engineer_features`, `setup_feature_store`)
   - Calls Member 3's feature engineering
   - Initializes Feast feature store

5. **Model Layer** (`train_model`)
   - Calls Member 4's model training script
   - Tracks experiments in MLflow

### Task Dependencies

```
pipeline_start
    ↓
ingestion_layer (ingest_data)
    ↓
validation_layer (validate_data)
    ↓
preparation_layer (prepare_data)
    ↓
feature_layer (engineer_features → setup_feature_store)
    ↓
model_layer (train_model)
    ↓
pipeline_end
```

## Triggering the Pipeline

### Manual Trigger (via UI)
1. Open Airflow UI (http://localhost:8080)
2. Locate `recom_pipeline` DAG
3. Click the play button to trigger

### Manual Trigger (via CLI)
```bash
airflow dags trigger recom_pipeline
```

### View DAG
```bash
airflow dags list
```

## Monitoring and Logs

### View Task Logs
1. In Airflow UI: Click on any task to view logs
2. Or check `airflow/logs/` directory directly

### Check DAG Status
```bash
airflow dags show recom_pipeline
airflow tasks list recom_pipeline
```

## Important Notes

- **Data Paths:** All tasks reference `../data/`, `../src/`, and `../mlruns/` relative to project root
- **Integration Points:** Each task is a Python wrapper that calls scripts in `src/{ingestion,validation,preparation,features,models}`
- **Customization:** Update task functions in `dags/recom_pipeline.py` with actual Member 1-4 scripts
- **Error Handling:** Tasks have configurable retry logic and fail gracefully with detailed logs

## TODO for Team Members

- [ ] Member 1: Create scripts in `src/ingestion/` and update `task_data_ingestion()`
- [ ] Member 2: Create scripts in `src/validation/` and `src/preparation/`, update tasks
- [ ] Member 3: Create scripts in `src/features/`, update `task_feature_engineering()` and `task_feature_store_setup()`
- [ ] Member 4: Create scripts in `src/models/`, update `task_model_training()` with MLflow integration
- [ ] Member 5: Finalize integration wrappers for ingestion/validation/preparation, validate Airflow DAG execution, and document remaining handoff steps
