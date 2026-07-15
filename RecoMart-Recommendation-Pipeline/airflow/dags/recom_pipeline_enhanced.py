"""
Enhanced Airflow DAG with Logging, Monitoring, and Alerting

This is an extended version of the main DAG with additional:
- Structured logging output
- Task callbacks for success/failure/retry
- Centralized monitoring
- Alert thresholds
"""

from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
import logging

from monitoring import (
    configure_logging,
    PipelineMonitor,
    task_failure_callback,
    task_success_callback,
    task_retry_callback,
    log_task_start,
    log_task_end,
)

# Setup logging
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "airflow" / "logs"
logger = configure_logging(LOG_DIR, "recom_pipeline_enhanced")

# Initialize monitoring
monitor = PipelineMonitor(LOG_DIR)

# DAG Configuration
DAG_ID = "recom_pipeline_enhanced"
default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 7, 15),
    "email_on_failure": False,
    "provide_context": True,
}


def task_wrapper_with_monitoring(func, task_id: str):
    """
    Wrapper to add monitoring to task functions.
    
    Args:
        func: Original task function
        task_id: Task identifier
        
    Returns:
        Wrapped function with monitoring
    """
    def wrapped(**context):
        start_time = datetime.utcnow()
        try:
            log_task_start(task_id, context["execution_date"], context)
            result = func(**context)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_task_end(task_id, "SUCCESS", duration)
            
            return result
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            log_task_end(task_id, "FAILURE", duration)
            logger.error(f"Task {task_id} failed after {duration}s: {str(e)}")
            raise
    
    return wrapped


# Task definitions (placeholder - see recom_pipeline.py for actual implementation)
def monitored_ingestion(**context):
    logger.info("Monitored ingestion task")
    # TODO: Implement actual ingestion with monitoring
    pass


dag = DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="RecoMart Pipeline Enhanced with Monitoring",
    schedule_interval="0 2 * * 0",
    catchup=False,
    tags=["recom", "monitoring"],
)

with dag:
    # Example task with callbacks
    ingest = PythonOperator(
        task_id="ingest_data",
        python_callable=task_wrapper_with_monitoring(monitored_ingestion, "ingest_data"),
        on_failure_callback=task_failure_callback,
        on_success_callback=task_success_callback,
        on_retry_callback=task_retry_callback,
        provide_context=True,
    )
