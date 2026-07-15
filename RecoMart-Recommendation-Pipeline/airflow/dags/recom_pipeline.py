"""
RecoMart Recommendation Pipeline - Orchestration DAG

Orchestrates the end-to-end data management pipeline:
- Data Ingestion (Member 1)
- Data Validation (Member 2)
- Data Preparation (Member 2)
- Feature Engineering (Member 3)
- Feature Store (Member 3)
- Model Training (Member 4)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import logging
import sys
from pathlib import Path

# Import monitoring utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from monitoring import task_failure_callback, task_success_callback, task_retry_callback

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# DAG Configuration
DAG_ID = "recom_pipeline"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_PATH = PROJECT_ROOT / "src"
DATA_PATH = PROJECT_ROOT / "data"
LOGS_PATH = PROJECT_ROOT / "airflow" / "logs"

# Ensure log directory exists
LOGS_PATH.mkdir(exist_ok=True, parents=True)

# Default args
default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 7, 15),
    "email_on_failure": False,
    "email_on_retry": False,
    "provide_context": True,
    "depends_on_past": False,
}

# ============================================================================
# Task Functions
# ============================================================================

def log_pipeline_start(**context):
    """Log pipeline execution start."""
    execution_date = context['execution_date']
    logger.info(f"RecoMart Pipeline started at {execution_date}")
    logger.info(f"Task: {context['task'].task_id}")


def task_data_ingestion(**context):
    """
    Task: Data Ingestion (Member 1)
    - Ingest CSV files and REST API data
    - Store in data/raw with timestamp partitioning
    """
    try:
        logger.info("Starting data ingestion task...")
        # TODO: Call Member 1's ingestion script
        # import sys; sys.path.insert(0, str(SRC_PATH))
        # from ingestion.main import ingest_data
        # ingest_data(output_path=DATA_PATH / "raw")
        
        logger.info("Placeholder: Data ingestion completed")
        logger.info(f"Raw data stored in: {DATA_PATH / 'raw'}")
        
        return {"status": "success", "ingestion_path": str(DATA_PATH / "raw")}
    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}", exc_info=True)
        raise


def task_data_validation(**context):
    """
    Task: Data Validation (Member 2)
    - Run schema, missing value, duplicate checks
    - Generate data quality report
    """
    try:
        logger.info("Starting data validation task...")
        # TODO: Call Member 2's validation script
        # import sys; sys.path.insert(0, str(SRC_PATH))
        # from validation.main import validate_data
        # report = validate_data(input_path=DATA_PATH / "raw", output_path=DATA_PATH / "processed")
        
        logger.info("Placeholder: Data validation completed")
        logger.info(f"Quality report saved to: {DATA_PATH / 'processed'}")
        
        return {"status": "success", "validation_report": "data_quality_report.pdf"}
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}", exc_info=True)
        raise


def task_data_preparation(**context):
    """
    Task: Data Preparation (Member 2)
    - Clean, preprocess, and normalize data
    - Perform EDA and generate plots
    """
    try:
        logger.info("Starting data preparation task...")
        # TODO: Call Member 2's preparation script
        # import sys; sys.path.insert(0, str(SRC_PATH))
        # from preparation.main import prepare_data
        # prepared_df = prepare_data(input_path=DATA_PATH / "processed", output_path=DATA_PATH / "processed")
        
        logger.info("Placeholder: Data preparation completed")
        logger.info(f"Prepared data saved to: {DATA_PATH / 'processed'}")
        
        return {"status": "success", "prepared_dataset": "prepared_dataset.csv"}
    except Exception as e:
        logger.error(f"Data preparation failed: {str(e)}", exc_info=True)
        raise


def task_feature_engineering(**context):
    """
    Task: Feature Engineering (Member 3)
    - Create user, item, and interaction features
    - Design and execute SQL transformation
    """
    try:
        logger.info("Starting feature engineering task...")
        # TODO: Call Member 3's feature engineering script
        # import sys; sys.path.insert(0, str(SRC_PATH))
        # from features.main import engineer_features
        # feature_df = engineer_features(input_path=DATA_PATH / "processed", output_path=DATA_PATH / "features")
        
        logger.info("Placeholder: Feature engineering completed")
        logger.info(f"Engineered features saved to: {DATA_PATH / 'features'}")
        
        return {"status": "success", "features_path": str(DATA_PATH / "features")}
    except Exception as e:
        logger.error(f"Feature engineering failed: {str(e)}", exc_info=True)
        raise


def task_feature_store_setup(**context):
    """
    Task: Feature Store Setup (Member 3)
    - Initialize Feast feature store (or custom registry)
    - Publish versioned features
    """
    try:
        logger.info("Starting feature store setup task...")
        # TODO: Call Member 3's feature store script
        # import sys; sys.path.insert(0, str(SRC_PATH / "features"))
        # from feature_store import setup_feature_store
        # setup_feature_store(features_path=DATA_PATH / "features")
        
        logger.info("Placeholder: Feature store initialized")
        logger.info("Feature metadata registered and versioned")
        
        return {"status": "success", "feature_store": "feast_registry_v1"}
    except Exception as e:
        logger.error(f"Feature store setup failed: {str(e)}", exc_info=True)
        raise


def task_model_training(**context):
    """
    Task: Model Training & Evaluation (Member 4)
    - Train recommendation model (Collaborative Filtering or Content-Based)
    - Evaluate using Precision@K, Recall@K, NDCG
    - Track experiments with MLflow
    """
    try:
        logger.info("Starting model training task...")
        # TODO: Call Member 4's training script
        # import sys; sys.path.insert(0, str(SRC_PATH))
        # from models.main import train_model
        # metrics = train_model(
        #     features_path=DATA_PATH / "features",
        #     output_path=PROJECT_ROOT / "mlruns"
        # )
        
        logger.info("Placeholder: Model training completed")
        logger.info("Model metrics: Precision@10=0.XX, Recall@10=0.XX, NDCG=0.XX")
        logger.info(f"Model saved and tracked in: {PROJECT_ROOT / 'mlruns'}")
        
        return {"status": "success", "model": "recom_model_v1"}
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}", exc_info=True)
        raise


def log_pipeline_end(**context):
    """Log pipeline execution completion."""
    logger.info("RecoMart Pipeline execution completed successfully")
    logger.info(f"Logs saved to: {LOGS_PATH}")


# ============================================================================
# DAG Definition
# ============================================================================

dag = DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="RecoMart End-to-End Recommendation Pipeline",
    schedule_interval="0 2 * * 0",  # Weekly at 2 AM on Sunday
    catchup=False,
    tags=["recom", "pipeline", "ml"],
    doc_md=__doc__,
)

# Tasks
with dag:
    start = PythonOperator(
        task_id="pipeline_start",
        python_callable=log_pipeline_start,
        provide_context=True,
    )

    with TaskGroup("ingestion_layer", tooltip="Data Ingestion") as ingestion_layer:
        ingest = PythonOperator(
            task_id="ingest_data",
            python_callable=task_data_ingestion,
            provide_context=True,
            retries=2,
            retry_delay=timedelta(minutes=5),
            on_failure_callback=task_failure_callback,
            on_success_callback=task_success_callback,
            on_retry_callback=task_retry_callback,
        )

    with TaskGroup("validation_layer", tooltip="Data Validation") as validation_layer:
        validate = PythonOperator(
            task_id="validate_data",
            python_callable=task_data_validation,
            provide_context=True,
            retries=1,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=task_failure_callback,
            on_success_callback=task_success_callback,
            on_retry_callback=task_retry_callback,
        )

    with TaskGroup("preparation_layer", tooltip="Data Preparation") as preparation_layer:
        prepare = PythonOperator(
            task_id="prepare_data",
            python_callable=task_data_preparation,
            provide_context=True,
            retries=1,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=task_failure_callback,
            on_success_callback=task_success_callback,
            on_retry_callback=task_retry_callback,
        )

    with TaskGroup("feature_layer", tooltip="Feature Engineering & Store") as feature_layer:
        engineer = PythonOperator(
            task_id="engineer_features",
            python_callable=task_feature_engineering,
            provide_context=True,
            retries=1,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=task_failure_callback,
            on_success_callback=task_success_callback,
            on_retry_callback=task_retry_callback,
        )

        feature_store = PythonOperator(
            task_id="setup_feature_store",
            python_callable=task_feature_store_setup,
            provide_context=True,
            retries=1,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=task_failure_callback,
            on_success_callback=task_success_callback,
            on_retry_callback=task_retry_callback,
        )

    with TaskGroup("model_layer", tooltip="Model Training & Evaluation") as model_layer:
        train = PythonOperator(
            task_id="train_model",
            python_callable=task_model_training,
            provide_context=True,
            retries=2,
            retry_delay=timedelta(minutes=5),
            on_failure_callback=task_failure_callback,
            on_success_callback=task_success_callback,
            on_retry_callback=task_retry_callback,
        )

    end = PythonOperator(
        task_id="pipeline_end",
        python_callable=log_pipeline_end,
        provide_context=True,
        trigger_rule="all_done",
    )

    # Task dependencies
    start >> ingestion_layer
    ingestion_layer >> validation_layer
    validation_layer >> preparation_layer
    preparation_layer >> feature_layer
    engineer >> feature_store
    feature_store >> model_layer
    model_layer >> end
