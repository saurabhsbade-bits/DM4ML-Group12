# Ingestion Workflow

## Project Title

**RecoMart Recommendation Pipeline – Data Ingestion Workflow**

---

# 1. Introduction

The RecoMart Recommendation Pipeline implements an automated data ingestion workflow that collects data from multiple heterogeneous sources, stores the raw data in a centralized data lake, generates metadata, and maintains execution logs.

The workflow has been designed to be modular, scalable, and reusable. Each stage performs a specific responsibility while interacting seamlessly with the other modules.

---

# 2. Workflow Overview

The pipeline follows the sequence below.

```
                START
                   │
                   ▼
          Read Configuration
                   │
                   ▼
        Initialize Logger
                   │
                   ▼
      Create Metadata Object
                   │
                   ▼
      CSV Data Ingestion
                   │
                   ▼
      REST API Ingestion
                   │
                   ▼
      Generate Metadata
                   │
                   ▼
        Save Metadata
                   │
                   ▼
      Pipeline Completed
```

---

# 3. Overall Pipeline Execution

The entire workflow is controlled through the `main.py` file.

```
main.py

│

├── CSV Ingestion

├── API Ingestion

├── Metadata Generation

└── Logging
```

Execution begins from:

```bash
python main.py
```

---

# 4. CSV Data Ingestion Workflow

The CSV ingestion module processes all configured datasets.

Supported datasets:

- movies.csv
- ratings.csv
- links.csv
- tags.csv

Workflow:

```
Read CSV File

↓

Verify File Exists

↓

Create Timestamp Folder

↓

Copy File

↓

Generate Metadata

↓

Write Logs

↓

Next Dataset
```

The process continues until all CSV datasets have been ingested successfully.

---

# 5. REST API Ingestion Workflow

The API ingestion module retrieves product data from the DummyJSON REST API.

Workflow:

```
REST API

↓

HTTP GET Request

↓

Validate Response

↓

Retry if Failed

↓

Receive JSON

↓

Create Timestamp Folder

↓

Save JSON

↓

Generate Metadata

↓

Write Logs
```

The retry mechanism ensures temporary network failures do not terminate the pipeline immediately.

---

# 6. Metadata Generation Workflow

Metadata is generated after successful ingestion of each dataset.

The metadata module records:

- Dataset name
- Source type
- Number of records
- File size
- Storage location
- Status
- Timestamp

Workflow:

```
Successful Ingestion

↓

Collect Statistics

↓

Create Metadata Record

↓

Append Record

↓

Save metadata.json
```

Example metadata entry:

```json
{
    "dataset": "ratings",
    "source_type": "CSV",
    "records": 100836,
    "status": "SUCCESS"
}
```

---

# 7. Logging Workflow

Logging captures all significant events throughout pipeline execution.

Workflow:

```
Pipeline Started

↓

CSV Processing

↓

API Processing

↓

Metadata Saved

↓

Pipeline Completed
```

The generated log file is stored at:

```
data/logs/ingestion.log
```

Logs include:

- Information messages
- Warnings
- Errors
- Execution status

---

# 8. Scheduler Workflow

The scheduler enables automated execution of the pipeline.

Workflow:

```
Scheduler Started

↓

Wait Until Scheduled Time

↓

Execute main.py

↓

Run Complete Pipeline

↓

Wait For Next Execution
```

Scheduler execution:

```bash
python -m src.ingestion.scheduler
```

---

# 9. Module Interaction

The interaction between modules is shown below.

```
                config.py
                     │
                     ▼
               helper.py
                     │
                     ▼
               logger.py
                     │
      ┌──────────────┴──────────────┐
      ▼                             ▼
csv_ingestion.py             api_ingestion.py
      │                             │
      └──────────────┬──────────────┘
                     ▼
         metadata_generator.py
                     │
                     ▼
                 main.py
                     │
                     ▼
              scheduler.py
```

Each module performs an independent responsibility while sharing configuration and utility functions.

---

# 10. Error Handling Workflow

The pipeline incorporates exception handling to ensure robustness.

```
Start Operation

↓

Try

↓

Success ?

Yes ─────► Continue

No

↓

Log Error

↓

Retry (API only)

↓

Continue Pipeline
```

The CSV module reports missing files without crashing the entire application.

The API module retries failed requests before reporting an error.

---

# 11. Raw Data Storage Workflow

After successful ingestion, datasets are stored using timestamp-based partitioning.

CSV Example

```
ratings.csv

↓

data/raw/csv/

↓

ratings/

↓

2026/

↓

07/

↓

16/

↓

225641/

↓

ratings.csv
```

API Example

```
REST API

↓

products.json

↓

data/raw/api/

↓

products/

↓

2026/

↓

07/

↓

16/

↓

225642/

↓

products.json
```

---

# 12. Complete End-to-End Workflow

```
                 MovieLens Dataset
                        │
                        ▼
                 CSV Ingestion
                        │
                        │
DummyJSON API ──────────┤
                        ▼
                REST API Ingestion
                        │
                        ▼
                 Raw Data Lake
                        │
                        ▼
              Metadata Generation
                        │
                        ▼
                    Log Files
                        │
                        ▼
                  Pipeline Finished
```

---

# 13. Advantages of the Workflow

The implemented workflow provides several advantages:

- Automated ingestion from multiple data sources
- Modular implementation
- Timestamp-based storage
- Centralized logging
- Metadata generation
- Retry mechanism for API failures
- Scalable architecture
- Easy maintenance
- Simplified debugging
- Foundation for future machine learning pipelines

---

# 14. Conclusion

The RecoMart Recommendation Pipeline successfully automates the ingestion of structured CSV datasets and REST API data into a centralized raw data lake.

The modular workflow integrates configuration management, logging, metadata generation, and scheduling into a single reusable pipeline. This architecture provides a scalable foundation for downstream preprocessing, feature engineering, recommendation model development, and future production deployment.
