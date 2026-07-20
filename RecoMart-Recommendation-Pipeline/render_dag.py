import importlib.util
import os
import pathlib
import sys

repo = pathlib.Path(r"c:\Users\saura\DM4ML-Group12\RecoMart-Recommendation-Pipeline").resolve()
airflow_home = repo / "airflow"
os.environ["AIRFLOW_HOME"] = str(airflow_home)
os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
os.environ["PYTHONPATH"] = str(repo)
os.environ["AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"] = "sqlite:///" + str((airflow_home / "airflow.db").resolve()).replace("\\", "/")

spec = importlib.util.spec_from_file_location("recom_pipeline", repo / "airflow" / "dags" / "recom_pipeline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print("dag", getattr(module, "dag", None) is not None)
out = airflow_home / "graphs" / "recom_pipeline.png"
out.parent.mkdir(parents=True, exist_ok=True)
module.dag.draw(out_path=str(out))
print("written", out.exists(), out.stat().st_size if out.exists() else None)
