Data Validation & Preparation — Quick Guide

Purpose
- Describe how to run the repository's data validation, profiling, cleaning, preprocessing and exploratory analysis (CSV datasets + API products).

Requirements
- Python 3.9+ (tested on 3.12)
- Recommended packages (install with `pip install -r airflow/requirements.txt` or individually):
  - pandas, numpy, scikit-learn, matplotlib, seaborn, reportlab, requests, nbconvert

Key scripts / notebooks
- `run_validation.py` — runs the CSV validation + profiling pipeline and generates a PDF or HTML data quality report. Uses `src/validation/validation_pipeline.py`.
- `run_api_validation.py` — ingests API product data, validates JSON with `src/validation/api_validator.py`, profiles API records and saves reports.

- `notebooks/02_Data_Preparation_CSV_and_API.ipynb` — interactive notebook demonstrating CSV + API cleaning, preprocessing and EDA (and containing the automated preprocessing routine).

Where outputs are stored
- Processed datasets: `data/processed/` (e.g. `movies_processed.csv`, `ratings_processed.csv`, `products_processed.csv`)
- Plots: `data/plots/` (distribution plots, heatmaps, sparsity, categorical plots)
- Validation & profiling reports: `data/reports/` (PDF report, JSON summaries)
- Ingestion metadata: `data/metadata/ingestion_metadata.json`

Run commands
- Run CSV validation & profiling (console):

```powershell
python RecoMart-Recommendation-Pipeline\run_validation.py
```

- Run API ingestion + validation:

```powershell
python RecoMart-Recommendation-Pipeline\run_api_validation.py
```

-- Run preprocessing + EDA (CSV) and save processed datasets/plots:

Option A — Run the preprocessing routine from the notebook (recommended, interactive):

```powershell
python -m nbconvert --to notebook --execute RecoMart-Recommendation-Pipeline\notebooks\02_Data_Preparation_CSV_and_API.ipynb --output RecoMart-Recommendation-Pipeline\notebooks\02_Data_Preparation_CSV_and_API.executed.ipynb --ExecutePreprocessor.timeout=600
```

Option B — Open the notebook and run the cell that calls `run_preprocessing_notebook()` to execute preprocessing interactively.

-- Note on dependencies: install the environment used for Airflow and the data tools with:

```powershell
pip install -r airflow/requirements.txt
```

-- Execute the notebook end-to-end (optional):

```powershell
python -m nbconvert --to notebook --execute RecoMart-Recommendation-Pipeline\notebooks\02_Data_Preparation_CSV_and_API.ipynb --output RecoMart-Recommendation-Pipeline\notebooks\02_Data_Preparation_CSV_and_API.executed.ipynb --ExecutePreprocessor.timeout=600
```

Notes & customization
- Schemas and constraints: adjust dataset schemas and `custom_constraints` in `src/validation/validation_pipeline.py` and API constraints in `src/validation/api_validator.py`.
- Missing-value strategies: configure per-column strategies in `DataCleaner.clean_csv(...)` by passing `missing_strategy` dict.
- Encoding & normalization: tweak methods in `src/preparation/data_preprocessor.py` (label vs one-hot, `minmax` vs `standard`).
- Reportlab is used for the PDF report; if not available an HTML fallback is generated.

Troubleshooting
- If imports fail inside notebooks, make sure to run the notebook from the repository root or add the repository root to `sys.path` as shown in the notebook's first cell.
- If the API run cannot find `products.json`, confirm `src/ingestion/api_ingestion.py` completed and check `data/raw/api/...` for timestamped folders.

Next steps
- Use the processed CSVs in downstream feature engineering or model training pipelines.
- Optionally produce a zip of `data/processed` + `data/plots` for handoff.

Contact
- For changes to the validation rules or preprocessing choices, modify the respective modules under `src/validation` and `src/preparation`.
