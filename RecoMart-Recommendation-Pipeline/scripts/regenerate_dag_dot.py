"""Regenerate the DOT export of the recom_pipeline DAG after a dependency fix."""
from pathlib import Path
from airflow.models.dagbag import DagBag
from airflow.utils.dot_renderer import render_dag

REPO_ROOT = Path(__file__).resolve().parent.parent
DAG_FOLDER = REPO_ROOT / "airflow" / "dags"
OUT_DOT = REPO_ROOT / "airflow" / "graphs" / "recom_pipeline.dot"

db = DagBag(dag_folder=str(DAG_FOLDER), include_examples=False)
print("IMPORT_ERRORS:", db.import_errors)

dag = db.dags.get("recom_pipeline")
print("DAG_FOUND:", dag is not None)
if dag is None:
    raise SystemExit("DAG not found")

for t in dag.tasks:
    print("DEP", t.task_id, "| upstream=", sorted(t.upstream_task_ids), "| downstream=", sorted(t.downstream_task_ids))

dot = render_dag(dag)
OUT_DOT.parent.mkdir(parents=True, exist_ok=True)
OUT_DOT.write_text(dot.source, encoding="utf-8")
print("WROTE", OUT_DOT, OUT_DOT.exists())
