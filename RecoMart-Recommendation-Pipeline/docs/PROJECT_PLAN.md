# Project Plan & Next Steps

Summary
-------
This document aligns the repository with the project plan and next actionable work items so the team can continue development and handoffs.

Current state
-------------
- Ingestion (Member 1): implemented and validated (CSV + API).
- Validation & Preparation (Member 2): implemented and validated; reports and processed data exist in `data/processed`.
- Feature Engineering (Member 3): minimal, working placeholder at `src/features` producing `data/features/features.csv`.
- Model Training (Member 4): minimal, working placeholder at `src/models` producing `models/baseline_model.joblib`.
- DAGs updated for Airflow 3.x and load successfully (`airflow/dags/recom_pipeline.py`, `recom_pipeline_enhanced.py`).
- CI smoke workflow added: `.github/workflows/e2e.yml` (uses `ci-requirements.txt`).

Remaining work (priority order)
------------------------------
1. Member 3: Expand feature engineering
   - Implement additional features (time-based, co-occurrence, embeddings)
   - Add unit tests for feature correctness
   - Owner: Member 3

2. Member 4: Improve modeling
   - Add training configuration, hyperparameter search, MLflow tracking
   - Add model evaluation report generation
   - Owner: Member 4

3. Data quality fixes
   - Investigate validation failures for `movies`, `links`, `tags` (type mismatches)
   - Add data-cleaning rules or adapt schemas
   - Owner: Member 2

4. Productionization & infra
   - Pin and review `airflow/requirements.txt` for deployment
   - Add Dockerfile or WSL instructions for reproducible Airflow runs on Windows
   - Owner: DevOps / Team

5. Documentation & handoff
   - Update `README.md` (done) and add `CONTRIBUTING.md` with development workflows
   - Owner: Project lead

How to run E2E locally (developer)
---------------------------------
1. Create and activate a venv

Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r ci-requirements.txt
python scripts/run_e2e.py
```

macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ci-requirements.txt
python scripts/run_e2e.py
```

Where to find artifacts
-----------------------
- Ingested raw data: `data/raw`
- Processed data + preparation summary: `data/processed`
- Features: `data/features/features.csv`
- Trained model: `models/baseline_model.joblib`
- Validation reports: `data/reports`

Next immediate actions (this week)
----------------------------------
- Member 2: Fix the `movies` type mismatches and re-run validation.
- Member 3: Add one new engineered feature (e.g., user frequency) and a unit test.
- Member 4: Add MLflow tracking scaffold and a simple `train_config.yaml`.

If you'd like, I can open PR branches for each action and add CI checks per-PR.
