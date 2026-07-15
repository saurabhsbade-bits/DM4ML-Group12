# RecoMart Pipeline - Operational Runbook

## Table of Contents

1. [Pre-Requisites](#pre-requisites)
2. [Setup & Initialization](#setup--initialization)
3. [Running the Pipeline](#running-the-pipeline)
4. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
5. [Common Tasks](#common-tasks)
6. [Emergency Procedures](#emergency-procedures)

## Pre-Requisites

### System Requirements

- Python 3.10+
- 4GB RAM (minimum)
- 10GB disk space (for logs, data, models)
- Git and GitHub access

### Required Software

```bash
# Install Python dependencies
pip install -r airflow/requirements.txt

# Optional: Feast for feature store
pip install feast

# Optional: MLflow for experiment tracking
pip install mlflow
```

### Environment Setup

```bash
# Clone repository
git clone https://github.com/saurabhsbade-bits/DM4ML-Group12.git
cd DM4ML-Group12/RecoMart-Recommendation-Pipeline

# Create Python virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r airflow/requirements.txt
```

---

## Setup & Initialization

### 1. Initialize Airflow

```bash
# Set Airflow home directory
export AIRFLOW_HOME=$(pwd)/airflow

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --password admin123 \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@recomart.com
```

### 2. Configure Airflow (Optional)

```bash
# Edit airflow config
# export AIRFLOW_HOME=$(pwd)/airflow
# Edit airflow.cfg if needed, or set via environment variables

# Example: Configure SMTP for email alerts
export AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
export AIRFLOW__SMTP__SMTP_PORT=587
export AIRFLOW__SMTP__SMTP_USER=your-email@gmail.com
export AIRFLOW__SMTP__SMTP_PASSWORD=your-app-password
```

### 3. Initialize Feature Store (Optional)

```bash
# If using Feast feature store
cd feature_store
feast init  # or configure manually
cd ..
```

### 4. Initialize MLflow (Optional)

```bash
# MLflow automatically creates tracking server on first log
# Or start MLflow tracking server explicitly
mlflow server --backend-store-uri file:///$(pwd)/mlruns \
              --default-artifact-root /$(pwd)/mlruns/artifacts \
              --host 127.0.0.1 --port 5000
```

---

## Running the Pipeline

### 1. Start Airflow Services

**Terminal 1: Airflow Webserver**

```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow webserver --port 8080
```

**Terminal 2: Airflow Scheduler**

```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow scheduler
```

Access Airflow UI at: **http://localhost:8080**

### 2. Trigger Pipeline Manually

**Via CLI:**

```bash
airflow dags trigger recom_pipeline
```

**Via UI:**

1. Navigate to http://localhost:8080
2. Find `recom_pipeline` DAG
3. Click the play button (trigger)

### 3. Monitor Execution

**Airflow UI Views:**

- **DAG View:** Shows pipeline structure
- **Tree View:** Historical execution status
- **Graph View:** Real-time task execution
- **Logs:** Detailed task output

**Command Line:**

```bash
# List DAGs
airflow dags list

# Show DAG structure
airflow dags show recom_pipeline

# List specific DAG tasks
airflow tasks list recom_pipeline

# Get DAG status
airflow dags list-runs --dag-id recom_pipeline
```

### 4. Check Logs

**Airflow Task Logs:**

```bash
# View task log (via UI is easier - click on task)
# Or check files directly:
ls -lah airflow/logs/recom_pipeline/

# Follow main log
tail -f airflow/logs/recom_pipeline.log

# Structured execution logs
cat airflow/logs/pipeline_execution.jsonl | jq .

# Failure logs
cat airflow/logs/pipeline_failures.jsonl | jq .

# Alert logs
cat airflow/logs/alerts.jsonl | jq .
```

---

## Monitoring & Troubleshooting

### 1. Check Pipeline Health

```bash
# Get recent DAG run status
airflow dags list-runs --dag-id recom_pipeline --limit 10

# Example output:
# dag_id            | run_id                          | execution_date       | state
# recom_pipeline    | scheduled__2026-07-15T02:00:00 | 2026-07-15T02:00:00 | success

# Check specific task status
airflow tasks list-runs --dag-id recom_pipeline --task-id ingest_data
```

### 2. View Task Details

```bash
# Via CLI (limited info)
airflow tasks info recom_pipeline ingest_data

# Via UI (better):
# 1. Click DAG → Graph View
# 2. Click task → View logs
```

### 3. Analyze Failures

**Failure Investigation Steps:**

1. **Check Airflow UI**
   - Go to Graph View → click failed task → view logs
   
2. **Check Failure Log**
   ```bash
   cat airflow/logs/pipeline_failures.jsonl | jq 'select(.task_id == "ingest_data")'
   ```

3. **Check Data Directory**
   ```bash
   ls -la data/raw/    # Check ingestion output
   ls -la data/processed/  # Check validation output
   ```

4. **Verify Task Dependencies**
   ```bash
   airflow tasks list recom_pipeline --tree
   ```

### 4. Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| DAG not showing | Dags folder misconfigured | Check `AIRFLOW_HOME` and `DAG_FOLDER` settings |
| Task fails: "No module" | Python import path issue | Add to `PYTHONPATH`: `export PYTHONPATH=$PYTHONPATH:$(pwd)/src` |
| Logs not writing | Permission denied | Check write permissions on `airflow/logs/` directory |
| Scheduler not running | Process crashed | Restart: `airflow scheduler` |
| Database locked | SQLite concurrency issue | Delete `airflow/airflow.db` and reinit (dev only!) |
| Email alerts not sending | SMTP misconfigured | Verify SMTP credentials and network connectivity |

---

## Common Tasks

### 1. View DAG Definition

```bash
# Print DAG code
airflow dags show recom_pipeline

# Or edit directly
# Edit: airflow/dags/recom_pipeline.py
```

### 2. Modify Schedule

```python
# Edit airflow/dags/recom_pipeline.py
# Change schedule_interval parameter:

# Current: "0 2 * * 0"  (every Sunday 2 AM)
# Options:
# - "0 2 * * *"         (daily at 2 AM)
# - "0 2 * * 1-5"       (weekdays at 2 AM)
# - "@weekly"           (same as "0 0 * * 0")
# - "60"                (every 60 minutes)
# - None                (manual trigger only)
```

### 3. Change Retry Configuration

```python
# Edit airflow/dags/recom_pipeline.py
# Modify PythonOperator parameters:

task = PythonOperator(
    task_id="ingest_data",
    python_callable=task_data_ingestion,
    retries=3,                          # Increase retries
    retry_delay=timedelta(minutes=10),  # Increase delay between retries
    pool_slots=2,                       # Control concurrency
)
```

### 4. Add New Task

```python
# Example: Add data export task after training

export_model = PythonOperator(
    task_id="export_model",
    python_callable=export_model_func,
    provide_context=True,
    on_failure_callback=task_failure_callback,
)

# Add dependency
train >> export_model >> end
```

### 5. Clear Task History

```bash
# Clear specific task (careful!)
airflow tasks clear --dag-id recom_pipeline --task-id ingest_data

# Clear entire DAG run (careful!)
airflow dags clear --dag-id recom_pipeline --start-date 2026-07-15 --end-date 2026-07-22

# Dry run (preview what will be cleared)
airflow tasks clear --dry-run --dag-id recom_pipeline --task-id ingest_data
```

### 6. Export Data for Analysis

```bash
# Copy data to separate location
mkdir -p /tmp/recomart_export
cp -r data/ /tmp/recomart_export/
cp -r airflow/logs/ /tmp/recomart_export/logs_backup/
tar -czf recomart_data_$(date +%Y%m%d).tar.gz /tmp/recomart_export/
```

---

## Emergency Procedures

### 1. Stop All Services

```bash
# Kill scheduler
pkill -f "airflow scheduler"

# Kill webserver
pkill -f "airflow webserver"

# Kill any remaining Airflow processes
pkill -f "airflow"
```

### 2. Reset to Clean State (Dev Environment Only)

```bash
# WARNING: This deletes all Airflow history!

export AIRFLOW_HOME=$(pwd)/airflow

# Remove database
rm -f airflow/airflow.db

# Clean logs
rm -rf airflow/logs/*

# Reinitialize
airflow db init

# Recreate admin user
airflow users create \
    --username admin \
    --password admin123 \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@recomart.com
```

### 3. Recover from Failed Run

```bash
# Option 1: Rerun specific task
airflow tasks run recom_pipeline ingest_data 2026-07-15

# Option 2: Clear and rerun from Airflow UI
# DAG → Calendar → Select date → Clear task → Trigger

# Option 3: Check logs and fix root cause, then trigger again
tail -f airflow/logs/recom_pipeline/ingest_data/*/attempt-*.log
```

### 4. Backup Critical Data

```bash
# Backup before major changes
mkdir -p backups/$(date +%Y%m%d)

# Backup data
cp -r data/ backups/$(date +%Y%m%d)/data_backup/

# Backup models
cp -r mlruns/ backups/$(date +%Y%m%d)/mlruns_backup/

# Backup feature store
cp -r feature_store/ backups/$(date +%Y%m%d)/feature_store_backup/

# Create tarball
tar -czf backups/recomart_backup_$(date +%Y%m%d).tar.gz backups/$(date +%Y%m%d)/
```

### 5. Report Production Issues

**Contact Information:**

- **Data Engineer (Member 5):** [Email/Slack]
- **Pipeline Issues:** Create GitHub issue in [project repo]
- **Emergency Escalation:** [On-call contact]

**Include in Issue Report:**

```markdown
## Pipeline Failure Report

**Date/Time:** 2026-07-15 14:30 UTC
**DAG:** recom_pipeline
**Failed Task:** ingest_data
**Error:** [Paste full error from logs]
**Impact:** [Describe impact on downstream tasks]
**Steps to Reproduce:** [If known]
**Last Successful Run:** 2026-07-08 02:00 UTC

### Relevant Logs
[Paste logs from airflow/logs/ or pipeline_failures.jsonl]
```

---

## References

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Architecture Diagram](architecture.md)
- [Monitoring & Alerts Guide](../airflow/MONITORING_AND_ALERTS.md)
- [Main DAG Code](../airflow/dags/recom_pipeline.py)

---

**Last Updated:** July 15, 2026  
**Runbook Version:** 1.0  
**Maintained By:** Member 5 (Data Pipeline Engineer)
