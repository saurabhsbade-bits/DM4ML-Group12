# 🎬 RecoMart Recommendation Pipeline

An automated **multi-source data ingestion pipeline** developed for the **DM4ML (Data Management for Machine Learning)** course at **BITS Pilani WILP**.

The pipeline ingests data from structured CSV datasets and REST APIs, stores raw data in a timestamp-based data lake, generates metadata, maintains execution logs, and supports automated scheduling.

---

# 📌 Project Overview

Modern recommendation systems require continuous ingestion of data from multiple heterogeneous sources before feature engineering and model training can begin.

The **RecoMart Recommendation Pipeline** automates this process by:

- Ingesting MovieLens CSV datasets
- Fetching product information from a REST API
- Organizing raw data into a scalable data lake
- Generating ingestion metadata
- Logging pipeline execution
- Supporting automated scheduling

This project demonstrates the **Data Ingestion Layer** of an end-to-end recommendation system.

---

# 🚀 Features

- ✅ Multi-source data ingestion
- ✅ CSV ingestion
- ✅ REST API ingestion
- ✅ Timestamp-based raw data lake
- ✅ Metadata generation
- ✅ Centralized logging
- ✅ Retry mechanism for API failures
- ✅ Error handling
- ✅ Automated scheduler
- ✅ Modular architecture
- ✅ Configuration-driven implementation

---

# 🏗️ Project Architecture

```text
                    MovieLens Dataset
                           │
                           ▼
                    CSV Ingestion
                           │
                           │
DummyJSON REST API ─────────┤
                           ▼
                  API Ingestion
                           │
                           ▼
                    Raw Data Lake
                           │
          ┌────────────────┴───────────────┐
          ▼                                ▼
   Metadata Generation                 Logging
          │                                │
          └────────────────┬───────────────┘
                           ▼
                     Main Pipeline
                           │
                           ▼
                      Scheduler
```

---

# 📁 Project Structure

```text
RecoMart-Recommendation-Pipeline/
│
├── dataset/
│   ├── movies.csv
│   ├── ratings.csv
│   ├── links.csv
│   └── tags.csv
│
├── data/
│   ├── raw/
│   │   ├── csv/
│   │   └── api/
│   ├── processed/
│   ├── metadata/
│   └── logs/
│
├── docs/
│   ├── 01_Business_Problem.md
│   ├── 02_Project_Objectives.md
│   ├── 03_Dataset_Documentation.md
│   ├── 04_Storage_Architecture.md
│   ├── 05_Ingestion_Workflow.md
│   └── 06_User_Guide.md
│
├── src/
│   ├── config/
│   │   └── config.py
│   │
│   ├── ingestion/
│   │   ├── csv_ingestion.py
│   │   ├── api_ingestion.py
│   │   └── scheduler.py
│   │
│   ├── metadata/
│   │   └── metadata_generator.py
│   │
│   └── utils/
│       ├── helper.py
│       └── logger.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

# 📂 Data Sources

## 1. MovieLens Dataset

The MovieLens dataset provides movie information and historical user ratings.

Files used:

- movies.csv
- ratings.csv
- links.csv
- tags.csv

Reference:

https://grouplens.org/datasets/movielens/

---

## 2. DummyJSON REST API

API Endpoint

```
https://dummyjson.com/products
```

The API provides product information including:

- Product Name
- Brand
- Category
- Price
- Rating
- Stock

---

# 🔄 Pipeline Workflow

```text
Start

↓

Read Configuration

↓

Initialize Logger

↓

CSV Ingestion

↓

REST API Ingestion

↓

Generate Metadata

↓

Store Raw Data

↓

Save Logs

↓

Pipeline Completed
```

---

# 📦 Raw Data Storage

---

**Integration Status**

- **Ingestion (Member 1):** Validated — CSV and API ingestion run successfully and metadata saved to `data/metadata/ingestion_metadata.json`.
- **Validation & Preparation (Member 2):** Validated — validation reports and EDA generated; prepared data saved in `data/processed`.
- **Feature Engineering (Member 3):** Minimal working placeholder implemented (`src/features`) that produces `data/features/features.csv`.
- **Model Training (Member 4):** Minimal working placeholder implemented (`src/models`) that trains and persists a baseline model at `models/baseline_model.joblib`.
- **Member 5 Integration:** Verified integration of ingestion/validation/preparation wrappers (Member 5 wiring validated).

Quick local E2E (developer):

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ci-requirements.txt
python scripts/run_e2e.py
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ci-requirements.txt
python scripts/run_e2e.py
```

CI: A lightweight GitHub Actions workflow is provided at `.github/workflows/e2e.yml` which installs `ci-requirements.txt` and runs `scripts/run_e2e.py` as an end-to-end smoke test.


CSV datasets are stored using timestamp-based partitioning.

Example

```text
data/
└── raw/
    └── csv/
        └── ratings/
            └── 2026/
                └── 07/
                    └── 16/
                        └── 225641/
                            └── ratings.csv
```

REST API responses

```text
data/
└── raw/
    └── api/
        └── products/
            └── 2026/
                └── 07/
                    └── 16/
                        └── 225642/
                            └── products.json
```

---

# 📊 Metadata

The pipeline automatically generates metadata.

Example

```json
{
    "dataset": "ratings",
    "source_type": "CSV",
    "records": 100836,
    "file_size_mb": 2.37,
    "status": "SUCCESS",
    "ingestion_time": "2026-07-16T22:56:41"
}
```

Metadata includes:

- Dataset name
- Source type
- File size
- Number of records
- Destination
- Status
- Timestamp

---

# 📝 Logging

Execution logs are stored in:

```text
data/logs/ingestion.log
```

Logs include:

- Pipeline start
- CSV ingestion
- API requests
- Retry attempts
- Errors
- Completion status

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/saurabhsbade-bits/DM4ML-Group12.git
```

Move to the project directory

```bash
cd DM4ML-Group12/RecoMart-Recommendation-Pipeline
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Pipeline

Execute the complete ingestion pipeline

```bash
python main.py
```

---

# ⏰ Run Scheduler

The scheduler automatically executes the pipeline at the configured time.

```bash
python -m src.ingestion.scheduler
```

---

# 📦 Python Modules Used

- pathlib
- shutil
- pandas
- requests
- json
- logging
- schedule
- datetime
- time

---

# 📈 Expected Outputs

After successful execution, the project generates:

```
✔ Raw CSV datasets

✔ Raw JSON datasets

✔ Metadata

✔ Execution logs

✔ Timestamped storage
```

---

# 📚 Documentation

Project documentation is available in the `docs/` directory.

- Business Problem
- Project Objectives
- Dataset Documentation
- Storage Architecture
- Ingestion Workflow
- User Guide

---

# 🛠️ Future Enhancements

Potential future improvements include:

- Data validation
- Incremental ingestion
- Data preprocessing
- Feature engineering
- Recommendation model training
- Docker support
- Kubernetes deployment
- Apache Airflow orchestration
- Cloud storage integration
- Apache Kafka streaming

---

# 👨‍💻 Team

**Course:** Data Management for Machine Learning (DM4ML)

**University:** BITS Pilani – Work Integrated Learning Programme (WILP)

---

# 📄 License

This project has been developed for academic purposes as part of the DM4ML course at BITS Pilani WILP.
