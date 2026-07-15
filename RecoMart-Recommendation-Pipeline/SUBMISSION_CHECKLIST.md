# SUBMISSION CHECKLIST & INTEGRATION GUIDE

**Project:** RecoMart End-to-End Recommendation Pipeline  
**Submission Deadline:** 22.07.2026  
**Prepared By:** Member 5 (Pipeline Orchestration & Documentation)  
**Status:** Ready for team member integration

---

## OVERVIEW

This guide helps team members understand:
1. What has been completed (Member 5 - Orchestration & Docs)
2. What each member needs to implement (Members 1-4)  
3. How to integrate their code into the pipeline
4. Pre-submission validation steps
5. Final submission packaging

---

## SECTION 1: COMPLETED DELIVERABLES (MEMBER 5)

### ✅ Infrastructure & Orchestration

- [x] **Airflow DAG Pipeline** (`airflow/dags/recom_pipeline.py`)
  - Complete task workflow with dependencies
  - 6 pipeline stages (ingestion → validation → preparation → features → training → end)
  - Task groups for logical organization
  - Weekly schedule configuration (Sunday 2 AM UTC)
  
- [x] **Enhanced Monitoring** (`airflow/monitoring.py`)
  - Structured JSON logging configuration
  - PipelineMonitor class for execution tracking
  - Task lifecycle callbacks (success/failure/retry)
  - Automatic log rotation (10MB, 5 backups)

- [x] **Alerting System** (`airflow/alerts.py`)
  - AlertManager with email and Slack integration
  - Three alert types: TASK_FAILURE, SLA_MISS, DATA_QUALITY_ALERT
  - Alert logging and summary generation
  - Extensible for additional channels

- [x] **Source Code Stubs** (`src/{ingestion,validation,preparation,features,models}/__init__.py`)
  - Template functions with docstrings
  - TODO comments for each member
  - Consistent function signatures
  - Import-ready for DAG integration

### ✅ Documentation

- [x] **Architecture Document** (`docs/architecture.md`)
  - High-level system diagrams (ASCII art)
  - Data flow visualization
  - Component descriptions
  - Technology stack summary
  - Deployment notes

- [x] **Operational Runbook** (`docs/runbook.md`)
  - Pre-requisites and setup steps
  - Airflow initialization
  - Pipeline execution procedures
  - Monitoring and troubleshooting
  - Emergency procedures
  - Common issues matrix with solutions

- [x] **Final Report Template** (`reports/FINAL_REPORT_TEMPLATE.md`)
  - All required sections per assignment
  - Sample execution logs
  - Performance metrics template
  - Team member responsibilities matrix
  - Submission checklist and appendices

- [x] **Monitoring Guide** (`airflow/MONITORING_AND_ALERTS.md`)
  - Logging architecture explanation
  - Task callback descriptions
  - Alert types and channels
  - Monitoring dashboards
  - Log analysis scripts

- [x] **Airflow Setup Guide** (`airflow/README.md`)
  - Installation steps
  - Configuration procedures
  - DAG trigger methods
  - Log viewing instructions

### ✅ Configuration Files

- [x] **Requirements** (`airflow/requirements.txt`)
  - Apache Airflow 2.7.3
  - Provider packages
  - Python dependencies

- [x] **Config Template** (`airflow/config_template.env`)
  - SMTP settings for email alerts
  - Data path configurations
  - Optional Slack webhook setup

- [x] **DVC Configuration** (`dvc.yaml`)
  - Placeholder for data versioning stages
  - Ready for Member 1-4 to populate

### ✅ Project Structure

- [x] **Directory Layout** - All folders created with `.gitkeep` files
  - `data/{raw,processed,features}`
  - `src/{ingestion,validation,preparation,features,models}`
  - `airflow/dags` and `airflow/logs`
  - `feature_store/` and `mlruns/`
  - `reports/` and `docs/`

- [x] **Version Control** - Repository initialized and pushed
  - Initial commits with directory structure
  - DAG and monitoring layer
  - Documentation layer
  - Ready for team member code commits

---

## SECTION 2: MEMBER-SPECIFIC INTEGRATION TASKS

### MEMBER 1: Data Ingestion & Storage

**Location:** `src/ingestion/__init__.py`

**Functions to Implement:**

```python
def ingest_csv_data(source_path: str, output_path: str) -> Dict[str, Any]:
    """
    Implement CSV file ingestion.
    
    Required:
    - Read CSV files from source_path
    - Validate structure (schema, data types)
    - Apply error handling and retry logic
    - Store in output_path with timestamp partitioning
    - Return metadata dictionary
    
    Expected output directory structure:
    output_path/csv/2026-07-15/file1.csv
    output_path/csv/2026-07-15/file2.csv
    """
    pass

def ingest_rest_api_data(api_endpoints: list, output_path: str) -> Dict[str, Any]:
    """
    Implement REST API data fetching.
    
    Required:
    - Make HTTP requests to api_endpoints with retries
    - Handle rate limiting and timeouts
    - Validate API responses (JSON structure)
    - Store JSON responses in output_path
    - Log all requests and responses
    - Return metadata (records fetched, endpoints hit, errors)
    
    Expected output directory structure:
    output_path/api/2026-07-15/endpoint1.json
    output_path/api/2026-07-15/endpoint2.json
    """
    pass

def ingest_data(output_path: str) -> Dict[str, Any]:
    """
    Main orchestrator function.
    
    Required:
    - Call ingest_csv_data() with appropriate paths
    - Call ingest_rest_api_data() with API endpoints
    - Combine results
    - Log ingestion summary (total records, sources, timestamps)
    - Return combined metadata
    """
    pass
```

**Deliverables After Implementation:**
- [ ] `src/ingestion/__init__.py` - Fully implemented functions
- [ ] `data/raw/csv/` - Sample CSV files (ingestion output)
- [ ] `data/raw/api/` - Sample API response files
- [ ] `airflow/logs/ingestion_*.log` - Execution logs from Airflow
- [ ] `docs/ingestion_guide.md` - Documentation of API endpoints and CSV format

**Integration Steps:**
1. Edit `src/ingestion/__init__.py` with your implementation
2. Update DAG if function signatures change
3. Run manually: `python -c "from src.ingestion import ingest_data; ingest_data('data/raw')"`
4. Test via Airflow: Trigger `recom_pipeline` DAG and check `ingest_data` task logs
5. Verify output in `data/raw/` directory

---

### MEMBER 2: Data Validation & Preparation

**Location:** `src/validation/__init__.py` and `src/preparation/__init__.py`

**Functions to Implement:**

```python
# src/validation/__init__.py

def validate_data(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Implement comprehensive data validation.
    
    Required checks:
    - Schema compliance (column names, data types)
    - Missing values detection and reporting
    - Duplicate row identification
    - Data type validation
    - Range/format checks (e.g., rating ∈ [1,5])
    - Anomaly detection
    - Generate PDF quality report with metrics
    
    Return:
    - validation_report_path
    - data_quality_score (0-100)
    - issues_found (list of problems)
    - records_passed/failed counts
    
    Output files:
    - {output_path}/data_quality_report_{timestamp}.pdf
    """
    pass

def prepare_data(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Implement data cleaning and preprocessing.
    
    Required:
    - Handle missing values (forward fill, interpolation, or drop)
    - Remove or transform duplicates
    - Encode categorical features (one-hot, label encoding)
    - Normalize numerical variables (standard scaling, min-max)
    - Remove outliers or apply robust transformations
    - Save cleaned dataset to CSV
    
    Return: Prepared DataFrame
    Output files:
    - {output_path}/prepared_data_{timestamp}.csv
    """
    pass

def generate_eda_report(data: pd.DataFrame, output_path: str) -> None:
    """
    Implement exploratory data analysis.
    
    Required visualizations:
    - Interaction distribution (histogram)
    - Item popularity distribution
    - User activity frequency
    - Data sparsity heatmap
    - Missing value patterns
    - Correlation matrix
    - Temporal trends (if applicable)
    
    Output files:
    - {output_path}/eda_analysis_{timestamp}.ipynb (Jupyter notebook)
    OR
    - {output_path}/eda_plots_{timestamp}.pdf (PDF report with plots)
    """
    pass
```

**Deliverables After Implementation:**
- [ ] `src/validation/__init__.py` - Fully implemented validation functions
- [ ] `src/preparation/__init__.py` - Fully implemented preparation functions
- [ ] `data/processed/prepared_data_*.csv` - Sample prepared dataset
- [ ] `reports/data_quality_report_*.pdf` - Quality assurance report
- [ ] `reports/eda_analysis_*.ipynb` - Jupyter notebook with EDA plots

**Integration Steps:**
1. Edit `src/validation/__init__.py` and `src/preparation/__init__.py`
2. Test locally with sample data first
3. Test via Airflow pipeline
4. Verify reports in `reports/` directory
5. Ensure output format matches downstream expectations (Member 3)

---

### MEMBER 3: Feature Engineering & Feature Store

**Location:** `src/features/__init__.py` and `feature_store/`

**Functions to Implement:**

```python
# src/features/__init__.py

def engineer_features(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Implement feature engineering for recommendation models.
    
    Required features:
    
    User Features (dimension ~15):
    - Activity frequency (# interactions)
    - Average rating given
    - User preference vector (from past interactions)
    - Demographics (age group, location - if available)
    - Temporal patterns (most active hour/day)
    
    Item Features (dimension ~15):
    - Popularity score (# interactions)
    - Average rating received
    - Category/subcategory
    - New item flag
    - Seasonal trends
    
    Interaction Features (dimension ~5):
    - Recency (days since last interaction)
    - Frequency (# total interactions)
    - Monetary value (if transaction data) or maturity
    
    Similarity Features (dimension ~10):
    - User-user similarity (based on past ratings)
    - Item-item similarity (content-based or rating-based)
    - Cross-features (user_avg_rating * item_avg_rating)
    
    Return: Feature DataFrame with shape (n_samples, n_features)
    Output file:
    - {output_path}/engineered_features_{timestamp}.csv
    - {output_path}/engineered_features_{timestamp}.parquet (optional)
    """
    pass

def design_sql_schema(output_path: str) -> str:
    """
    Design relational database schema for transformed data.
    
    Required tables:
    - user_features (user_id, activity_frequency, avg_rating, pref_vector, ...)
    - item_features (item_id, popularity, avg_rating, category, ...)
    - interaction_features (user_id, item_id, recency, frequency, ...)
    - feature_metadata (feature_name, description, version, created_at, ...)
    
    Include:
    - PRIMARY KEYS and INDEXES for fast queries
    - Foreign key relationships
    - Version columns for feature store tracking
    - Timestamp columns for temporal analysis
    
    Output file:
    - {output_path}/schema.sql
    """
    pass

def setup_feature_store(features_path: str, config: Optional[Dict] = None) -> str:
    """
    Initialize and configure feature store (Feast or custom).
    
    If using Feast:
    - Create feature repository structure
    - Define feature views (one per entity type)
    - Configure online/offline stores
    - Register all 45+ engineered features
    - Enable point-in-time accurate retrieval
    
    If using custom registry:
    - Create JSON/YAML registry with feature metadata
    - Store feature versions
    - Document transformations
    
    Return: Path to feature store registry
    Output files:
    - {feature_store}/registry.json or feast manifest
    - {feature_store}/features_metadata_v*.json
    """
    pass

def retrieve_features(entity_ids: list, feature_names: list, 
                     timestamp: Optional[str] = None) -> pd.DataFrame:
    """
    Retrieve versioned features for training/inference.
    
    Required:
    - Query feature store for specified features
    - Apply point-in-time versioning if timestamp provided
    - Handle missing features gracefully
    - Return feature matrix ready for modeling
    
    Return: Feature DataFrame (len(entity_ids) rows, len(feature_names) columns)
    """
    pass
```

**Deliverables After Implementation:**
- [ ] `src/features/__init__.py` - Fully implemented feature engineering
- [ ] `data/features/engineered_features_*.csv` - Sample feature matrix
- [ ] `feature_store/registry.json` - Feature registry/manifest
- [ ] `feature_store/schema.sql` - Database schema (if using relational store)
- [ ] `docs/feature_engineering_guide.md` - Feature definitions and engineering details

**Integration Steps:**
1. Implement all 4 functions in `src/features/__init__.py`
2. Create feature store configuration in `feature_store/`
3. Test locally with sample data
4. Ensure output format matches Member 4 expectations (feature matrix shape, columns)
5. Test via Airflow pipeline
6. Document all engineered features and their meanings

---

### MEMBER 4: Model Training & Evaluation

**Location:** `src/models/__init__.py` and `mlruns/`

**Functions to Implement:**

```python
# src/models/__init__.py

def train_model(features_path: str, output_path: str, 
                model_type: str = "collaborative_filtering") -> Dict[str, Any]:
    """
    Implement recommendation model training.
    
    Model Options:
    1. Collaborative Filtering
       - Matrix Factorization (SVD, NMF)
       - Neural Collaborative Filtering
       - Requirements: at least 30K training samples
    
    2. Content-Based Filtering
       - Cosine similarity on engineered features
       - Simpler but potentially less accurate
    
    Required:
    - Load features from {features_path}
    - Create train/val/test split (70/15/15 or 80/10/10)
    - Hyperparameter tuning (grid search or random search)
    - Train model with best hyperparameters
    - Save trained model to pickle/joblib
    - Return model metadata (type, hyperparams, training samples)
    
    Output file:
    - {output_path}/artifacts/model_v{version}.pkl
    """
    pass

def evaluate_model(model_path: str, test_data: pd.DataFrame, 
                  k_values: list = [5, 10, 20]) -> Dict[str, float]:
    """
    Implement model evaluation with recommendation metrics.
    
    Required Metrics (compute for each K):
    - Precision@K: (# relevant items in top-K) / K
    - Recall@K: (# relevant items in top-K) / (# total relevant items)
    - NDCG@K: Normalized Discounted Cumulative Gain
    
    Optional Metrics:
    - MAP (Mean Average Precision)
    - MRR (Mean Reciprocal Rank)
    - Diversity metrics
    
    Return: Dict with metrics for all K values
    Example:
    {
        "Precision@5": 0.72,
        "Precision@10": 0.65,
        "Recall@5": 0.25,
        "Recall@10": 0.40,
        "NDCG": 0.68,
        "mean_avg_precision": 0.58
    }
    """
    pass

def track_experiment(experiment_name: str, model_name: str, 
                    params: Dict[str, Any], metrics: Dict[str, float],
                    artifacts_path: Optional[str] = None) -> str:
    """
    Track experiment with MLflow.
    
    Required:
    - Create MLflow experiment (if not exists)
    - Start MLflow run
    - Log hyperparameters: {params}
    - Log metrics: {metrics}
    - Log model artifacts: {artifacts_path}
    - Log dataset info and data splits
    - End run and return run_id
    
    MLflow will save to: mlruns/{experiment_id}/{run_id}/
    
    Return: MLflow run ID (for later reference)
    """
    pass

def generate_evaluation_report(metrics: Dict[str, float], output_path: str) -> None:
    """
    Generate PDF evaluation report.
    
    Required:
    - Summary of model type and hyperparameters
    - Table of evaluation metrics
    - Visualizations:
      - Precision/Recall curve
      - NDCG across K values
      - Confusion matrix (if binary recommendation)
      - Sample predictions
    - Conclusion and recommendations
    
    Output file:
    - {output_path}/evaluation_metrics_{timestamp}.pdf
    """
    pass
```

**Deliverables After Implementation:**
- [ ] `src/models/__init__.py` - Fully implemented model training
- [ ] `mlruns/artifacts/model_v*.pkl` - Trained model file
- [ ] `mlruns/experiments/` - MLflow experiment tracking
- [ ] `reports/evaluation_metrics_*.pdf` - PDF evaluation report
- [ ] `mlruns/metadata.json` - Model metadata and hyperparameters

**Integration Steps:**
1. Implement all 4 functions in `src/models/__init__.py`
2. Integrate with MLflow for experiment tracking
3. Test locally with sample features from Member 3
4. Run via Airflow pipeline
5. Verify model saved to `mlruns/artifacts/`
6. Check evaluation metrics in PDF report
7. Document model selection rationale and trade-offs

---

## SECTION 3: INTEGRATION WORKFLOW

### Step 1: Set Up Development Environment

```bash
# Clone repo
git clone https://github.com/saurabhsbade-bits/DM4ML-Group12.git
cd DM4ML-Group12/RecoMart-Recommendation-Pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r airflow/requirements.txt
pip install mlflow feast  # Optional: feature store and experiment tracking

# Set up git branches
git checkout -b member-{1-4}-implementation
```

### Step 2: Implement Your Module

**Member 1 Example:**

```bash
# Edit your module
vim src/ingestion/__init__.py

# Test locally
python -c "
from src.ingestion import ingest_data
result = ingest_data('data/raw')
print(result)
"

# Commit changes
git add src/ingestion/__init__.py
git commit -m "impls: implement data ingestion module (Member 1)"
git push origin member-1-implementation
```

### Step 3: Test with Airflow Pipeline

```bash
# Initialize Airflow
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init

# Create admin user
airflow users create \
    --username admin --password admin123 \
    --firstname Admin --lastname User \
    --role Admin --email admin@recomart.com

# Start services (two terminals)
# Terminal 1:
airflow webserver --port 8080

# Terminal 2:
airflow scheduler

# Trigger pipeline
airflow dags trigger recom_pipeline

# Monitor in UI: http://localhost:8080
```

### Step 4: Verify Outputs

```bash
# Check data layer
ls -la data/{raw,processed,features}/

# Check reports
ls -la reports/

# Check MLflow
ls -la mlruns/

# Check logs
tail -f airflow/logs/recom_pipeline.log
```

### Step 5: Push Code & Create Pull Request

```bash
# Commit final changes
git add .
git commit -m "impls: complete Member X implementation with tests"

# Push to GitHub
git push origin member-{1-4}-implementation

# Create Pull Request with description:
# - What was implemented
# - Which functions were updated
# - Test results and sample outputs
# - Any assumptions or limitations
```

---

## SECTION 4: PRE-SUBMISSION VALIDATION

### Checklist Before Final Submission

#### **Data Artifacts**
- [ ] `data/raw/` contains ingested sample data (Member 1)
- [ ] `data/processed/` contains validated/prepared data (Member 2)
- [ ] `data/features/` contains engineered features (Member 3)
- [ ] All data files have reasonable sizes and row counts

#### **Code Quality**
- [ ] All `.py` files are syntactically correct (no import errors)
- [ ] Functions have proper docstrings and type hints
- [ ] Code follows PEP 8 style guidelines
- [ ] No hardcoded paths (use relative paths or config)
- [ ] Error handling implemented (try-except blocks)

#### **Airflow Pipeline**
- [ ] DAG is visible in Airflow UI
- [ ] All tasks are visible in Graph View
- [ ] Manual trigger works and completes successfully
- [ ] Task logs are clear and informative
- [ ] Retries work as expected for failed tasks

#### **Documentation**
- [ ] Architecture diagram is complete (docs/architecture.md)
- [ ] Runbook has step-by-step instructions (docs/runbook.md)
- [ ] Final report is filled with project details (reports/FINAL_REPORT_TEMPLATE.md)
- [ ] Each module has a README or guide document
- [ ] Setup instructions are clear and tested

#### **Monitoring & Logging**
- [ ] Application logs appear in `airflow/logs/recom_pipeline.log`
- [ ] Task-level logs are saved and retrievable
- [ ] Monitoring alerts system is configured
- [ ] Alert test send successfully (optional but recommended)

#### **Deliverables Completeness**
- [ ] All code in `src/` modules is implemented
- [ ] All data artifacts generated and saved
- [ ] All reports created (quality, EDA, evaluation)
- [ ] MLflow experiment tracking working
- [ ] DVC/Git data versioning configured

#### **README Files**
- [ ] `RecoMart-Recommendation-Pipeline/README.md` updated
- [ ] `airflow/README.md` - Airflow setup guide
- [ ] `docs/architecture.md` - System architecture
- [ ] `docs/runbook.md` - Operations guide
- [ ] `airflow/MONITORING_AND_ALERTS.md` - Monitoring guide

---

## SECTION 5: SUBMISSION PACKAGE PREPARATION

### 5.1 Create Submission ZIP

```bash
# From project root
mkdir submission
cp -r RecoMart-Recommendation-Pipeline submission/
cd submission

# Clean up unnecessary files
rm -rf RecoMart-Recommendation-Pipeline/airflow/logs/*
rm -rf RecoMart-Recommendation-Pipeline/mlruns/0/*  # Keep only metadata
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Create ZIP
cd ..
zip -r recomart_submission_2026-07-22.zip submission/
```

### 5.2 Sample Submission Contents

```
submission/
├── RecoMart-Recommendation-Pipeline/
│   ├── data/                  # All data artifacts
│   │   ├── raw/              # Member 1: ingested data
│   │   ├── processed/         # Member 2: prepared data
│   │   └── features/          # Member 3: engineered features
│   ├── src/                   # All implementations
│   │   ├── ingestion/         # Member 1 code
│   │   ├── validation/        # Member 2 code (validation)
│   │   ├── preparation/       # Member 2 code (preparation)
│   │   ├── features/          # Member 3 code
│   │   └── models/            # Member 4 code
│   ├── airflow/               # Orchestration layer
│   │   ├── dags/
│   │   │   └── recom_pipeline.py
│   │   ├── monitoring.py
│   │   ├── alerts.py
│   │   └── README.md
│   ├── reports/               # All deliverables
│   │   ├── FINAL_REPORT_TEMPLATE.md
│   │   ├── data_quality_report.pdf
│   │   ├── eda_analysis.ipynb
│   │   └── evaluation_metrics.pdf
│   ├── docs/                  # Documentation
│   │   ├── architecture.md
│   │   └── runbook.md
│   ├── feature_store/         # Feature registry
│   ├── mlruns/                # MLflow artifacts
│   ├── dvc.yaml               # Data versioning
│   └── README.md              # Project overview
├── DEMO_VIDEO.mp4             # 5-10 min walkthrough
└── SUBMISSION_MANIFEST.md     # File listing
```

### 5.3 Create Google Drive Folder

```
RecoMart-Recommendation-Pipeline-Submission/
├── Final Report (PDF)
├── Code & Data (submission.zip)
├── Demo Video (demo_video.mp4 or YouTube link)
└── README.txt (folder description)

Make folder accessible to: anyone with BITS ID
Allow: View access (not edit)
```

---

## SECTION 6: COMMON ISSUES & TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| **DAG not showing in Airflow** | Check `DAG_FOLDER` path in airflow.cfg, restart scheduler |
| **Import errors in DAG** | Add to PYTHONPATH: `export PYTHONPATH=$PYTHONPATH:$(pwd)/src` |
| **Task fails with "No module"** | Ensure your `.py` files have `from src.X import Y` (not relative imports) |
| **Logs not writing** | Check permissions on `airflow/logs/` directory |
| **Database locked** | Delete `airflow/airflow.db` and reinitialize (dev only!) |
| **Different Python path in Airflow** | Pin Python version in DAGs to match `python3.10` or environment variable |
| **Feature shape mismatch** | Member 3 and 4 need to communicate expected dimensions |
| **Model can't pickle** | Ensure all objects are serializable (use joblib instead if needed) |

---

## SECTION 7: TEAM COMMUNICATION PROTOCOL

### Meeting Schedule

- **Kickoff:** [Date] - Discuss roles and dependencies
- **Mid-point:** [Date] - Share progress, blockers, integration points
- **Final Review:** [Date] - Integration testing, report compilation
- **Submission:** 22.07.2026 - Final ZIP and Google Drive links

### Integration Testing Workflow

1. **Member 1** completes ingestion → runs locally, shares output sample
2. **Member 2** receives Member 1 output → implements validation/prep
3. **Member 3** receives Member 2 output → implements features
4. **Member 4** receives Member 3 features → trains model
5. **Member 5** orchestrates full pipeline with all members' code
6. **All members** contribute to final report and demo video

### Dependency Handoff

```
Member 1 (ingestion)
    ↓ (data/raw/)
Member 2 (validation & preparation)
    ↓ (data/processed/)
Member 3 (features)
    ↓ (data/features/ + feature_store/)
Member 4 (model training)
    ↓ (mlruns/artifacts/)
All members (documentation & submission)
```

---

## SECTION 8: FINAL SUBMISSION CHECKLIST

**Before submitting, verify:**

### Code Quality
- [ ] All Python files are valid (no syntax errors)
- [ ] All imports work correctly
- [ ] Functions have docstrings
- [ ] Error handling is implemented
- [ ] Config is externalized (no hardcoded secrets)

### Data & Artifacts
- [ ] Sample datasets in `data/` (at least 1000 rows each)
- [ ] Reports generated (PDF format recommended)
- [ ] Models saved to `mlruns/`
- [ ] Feature store configured

### Documentation
- [ ] Architecture diagram complete
- [ ] Runbook with step-by-step instructions
- [ ] Final report with all 6+ sections
- [ ] README files for key directories
- [ ] Member responsibilities documented

### Airflow Pipeline
- [ ] DAG visible and executable
- [ ] All 6 tasks present and linked
- [ ] Monitoring and alerting configured
- [ ] Logs being generated and rotated

### Submission Package
- [ ] ZIP file created with all deliverables
- [ ] Google Drive folder created and shared
- [ ] Demo video ready (5-10 min)
- [ ] All links are accessible to BITS IDs

### Sign-Off
- [ ] All team members reviewed the submission
- [ ] No plagiarism or academic integrity issues
- [ ] References and citations are correct
- [ ] Submission deadline OK (22.07.2026)

---

## APPENDIX: QUICK REFERENCE COMMANDS

```bash
# Airflow setup
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
airflow users create --username admin --password admin123 --role Admin

# Start services
airflow webserver --port 8080 &
airflow scheduler &

# Trigger pipeline
airflow dags trigger recom_pipeline

# View logs
tail -f airflow/logs/recom_pipeline.log

# Test module locally
python -c "from src.X import function; function(args)"

# Git workflow
git checkout -b member-{1-4}-implementation
git add .
git commit -m "impls: complete member {1-4} implementation"
git push origin member-{1-4}-implementation

# Clean up before submission
rm -rf airflow/logs/*
rm -rf __pycache__ *.pyc
zip -r submission.zip RecoMart-Recommendation-Pipeline/
```

---

**Version:** 1.0  
**Last Updated:** July 15, 2026  
**Maintained By:** Member 5  
**Status:** Ready for Team Integration

---
