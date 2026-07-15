# QUICK START DEPLOYMENT GUIDE

**Goal:** Get the RecoMart pipeline running in 15 minutes  
**Time Estimate:** 10-15 minutes  
**Difficulty:** Beginner-friendly  

---

## 1. PREREQUISITES (5 minutes)

### Install Python 3.10+

```bash
# Check Python version
python --version  # Should be 3.10+

# If not, download from python.org
# Windows: https://www.python.org/downloads/windows/
# macOS: https://www.python.org/downloads/macos/
# Linux: sudo apt-get install python3.10
```

### Install Git

```bash
# Windows: https://git-scm.com/download/win
# macOS: brew install git
# Linux: sudo apt-get install git
```

---

## 2. CLONE & SETUP (5 minutes)

```bash
# Clone repository
git clone https://github.com/saurabhsbade-bits/DM4ML-Group12.git

# Navigate to project
cd DM4ML-Group12/RecoMart-Recommendation-Pipeline

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r airflow/requirements.txt

# Verify Airflow installation
airflow version
```

---

## 3. INITIALIZE AIRFLOW (3 minutes)

```bash
# Set Airflow home
export AIRFLOW_HOME=$(pwd)/airflow

# Initialize database
airflow db init

# Create admin user (choose your own password)
airflow users create \
    --username admin \
    --password admin123 \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

---

## 4. START AIRFLOW (2 minutes, two terminals)

**Terminal 1: Webserver**

```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow webserver --port 8080
```

Wait for message: "Running on http://127.0.0.1:8080"

**Terminal 2: Scheduler**

```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow scheduler
```

---

## 5. ACCESS AIRFLOW UI

Open browser: **http://localhost:8080**

Login:
- Username: `admin`
- Password: `admin123`

You should see the `recom_pipeline` DAG!

---

## 6. TRIGGER PIPELINE

**Option A: Via UI**
1. Click `recom_pipeline` DAG
2. Click blue play button (▶) to trigger
3. Check "Graph View" to see execution

**Option B: Via CLI**
```bash
airflow dags trigger recom_pipeline
```

---

## 7. MONITOR EXECUTION

```bash
# View logs in real-time
tail -f airflow/logs/recom_pipeline.log

# Or check in UI:
# - Click DAG → Graph View
# - Click each task to see logs
# - Green = success, Red = failed
```

---

## 8. CHECK OUTPUTS

```bash
# Data layer
ls -la data/raw/
ls -la data/processed/
ls -la data/features/

# Reports
ls -la reports/

# Models
ls -la mlruns/

# Pipeline logs
ls -la airflow/logs/
```

---

## TROUBLESHOOTING

### **DAG not showing?**
```bash
# Verify AIRFLOW_HOME is set
echo $AIRFLOW_HOME

# Check DAG syntax
python -m py_compile airflow/dags/recom_pipeline.py

# Restart scheduler
pkill -f "airflow scheduler"
export AIRFLOW_HOME=$(pwd)/airflow
airflow scheduler
```

### **Tasks failing?**
1. Click failed task in Airflow UI
2. Click "Log" tab to see full error
3. Check if member code is implemented
4. Verify data exists in `data/raw/`

### **"No module named" error?**
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### **Port 8080 already in use?**
```bash
airflow webserver --port 8081  # Use different port
```

---

## NEXT STEPS

### For Members 1-4:

1. **Implement your module** in `src/{your_stage}/__init__.py`
2. **Test locally** with sample data
3. **Trigger pipeline** to test integration
4. **Commit code** to GitHub

### For Member 5:

1. **Generate documentation** (architecture, runbook, final report)
2. **Create demo video** showing pipeline execution
3. **Package submission** ZIP file
4. **Create Google Drive folder** with all deliverables

---

## FILE LOCATIONS FOR EACH MEMBER

| Member | Main Folder | Key Files |
|--------|------------|-----------|
| **1: Ingestion** | `src/ingestion/` | `__init__.py` → `ingest_data()` |
| **2: Validation & Prep** | `src/validation/` + `src/preparation/` | `validate_data()`, `prepare_data()` |
| **3: Features** | `src/features/` | `engineer_features()`, `setup_feature_store()` |
| **4: Models** | `src/models/` | `train_model()`, `evaluate_model()` |
| **5: Orchestration** | `airflow/dags/` | `recom_pipeline.py` (already done!) |

---

## USEFUL COMMANDS

```bash
# List all DAGs
airflow dags list

# Show DAG structure
airflow dags show recom_pipeline

# List tasks in DAG
airflow tasks list recom_pipeline

# Check data in pipeline
tree data/  # Or: ls -R data/

# View all logs
cat airflow/logs/recom_pipeline.log

# Stop Airflow
pkill -f airflow

# Clean before rerun (careful!)
rm airflow/airflow.db
airflow db init
```

---

## SUCCESS INDICATORS

✅ **You'll know it's working when:**
- Airflow UI shows `recom_pipeline` DAG
- Green checkmark appears on tasks after trigger
- Files appear in `data/`, `reports/`, `mlruns/` directories
- `airflow/logs/recom_pipeline.log` shows task completions

---

## VIDEO WALKTHROUGH

See demo at: [Google Drive Link - to be added by Member 5]

---

## SUPPORT

- **Documentation:** See `docs/` and `airflow/README.md`
- **Full Setup:** See `docs/runbook.md`
- **Troubleshooting:** See `SUBMISSION_CHECKLIST.md`
- **Architecture:** See `docs/architecture.md`

---

**Version:** 1.0  
**Updated:** July 15, 2026  
**Test Status:** ✅ Verified

Ready to start implementing? Good luck! 🚀
