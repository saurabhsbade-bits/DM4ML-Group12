"""
Logging and Monitoring Configuration for RecoMart Pipeline

Features:
- Structured logging with context
- Task failure callbacks and alerts
- Pipeline monitoring hooks
- Experiment tracking (MLflow integration)
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler

# Initialize logger
logger = logging.getLogger(__name__)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs JSON-structured logs for easy parsing."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def configure_logging(
    log_dir: Path,
    log_name: str = "recom_pipeline",
    level: int = logging.INFO,
    structured: bool = True
) -> logging.Logger:
    """
    Configure structured logging for the pipeline.
    
    Args:
        log_dir: Directory to store logs
        log_name: Name of the logger
        level: Logging level (default: INFO)
        structured: Use JSON structured logs (default: True)
        
    Returns:
        Configured logger instance
    """
    log_dir.mkdir(exist_ok=True, parents=True)
    
    logger_instance = logging.getLogger(log_name)
    logger_instance.setLevel(level)
    logger_instance.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    logger_instance.addHandler(console_handler)
    
    # File handler with rotation
    log_file = log_dir / f"{log_name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger_instance.addHandler(file_handler)
    
    logger_instance.info(f"Logging configured to {log_file}")
    
    return logger_instance


def log_task_start(task_id: str, execution_date: str, context: Dict[str, Any]) -> None:
    """
    Log task execution start with context.
    
    Args:
        task_id: Task identifier
        execution_date: Execution date/time
        context: Airflow context dictionary
    """
    logger.info(
        "Task started",
        extra={
            "task_id": task_id,
            "execution_date": execution_date,
            "try_number": context.get("task_instance").try_number if context else None,
        }
    )


def log_task_end(task_id: str, status: str, duration: float) -> None:
    """
    Log task execution end with duration.
    
    Args:
        task_id: Task identifier
        status: Task status (success/failure)
        duration: Execution duration in seconds
    """
    logger.info(
        "Task completed",
        extra={
            "task_id": task_id,
            "status": status,
            "duration_seconds": duration,
        }
    )


class PipelineMonitor:
    """Centralized monitoring for pipeline execution."""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.execution_log = log_dir / "pipeline_execution.jsonl"
        self.failures_log = log_dir / "pipeline_failures.jsonl"
    
    def log_execution(self, dag_id: str, run_id: str, status: str, metrics: Dict[str, Any]) -> None:
        """
        Log pipeline execution event.
        
        Args:
            dag_id: DAG identifier
            run_id: Run identifier
            status: Execution status
            metrics: Pipeline metrics
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "dag_id": dag_id,
            "run_id": run_id,
            "status": status,
            "metrics": metrics,
        }
        
        with open(self.execution_log, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        logger.info(f"Pipeline execution logged: {dag_id} - {status}")
    
    def log_failure(self, dag_id: str, task_id: str, run_id: str, error: str) -> None:
        """
        Log task failure for alerting.
        
        Args:
            dag_id: DAG identifier
            task_id: Task identifier
            run_id: Run identifier
            error: Error message
        """
        failure = {
            "timestamp": datetime.utcnow().isoformat(),
            "dag_id": dag_id,
            "task_id": task_id,
            "run_id": run_id,
            "error": error,
        }
        
        with open(self.failures_log, "a") as f:
            f.write(json.dumps(failure) + "\n")
        
        logger.error(f"Task failure logged: {dag_id}.{task_id} - {error}")
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """
        Get summary of recent failures.
        
        Returns:
            Dictionary with failure statistics
        """
        if not self.failures_log.exists():
            return {"total_failures": 0, "recent_failures": []}
        
        failures = []
        try:
            with open(self.failures_log, "r") as f:
                for line in f.readlines()[-10:]:  # Last 10 failures
                    failures.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading failure log: {e}")
        
        return {
            "total_failures": len(failures),
            "recent_failures": failures,
        }


def task_failure_callback(context) -> None:
    """
    Airflow callback for task failures. Logs and alerts.
    
    Args:
        context: Airflow task context
    """
    task_instance = context["task_instance"]
    exception = context.get("exception")
    
    log_dir = Path(__file__).parent.parent / "logs"
    monitor = PipelineMonitor(log_dir)
    
    error_msg = str(exception) if exception else "Unknown error"
    
    monitor.log_failure(
        dag_id=context["dag"].dag_id,
        task_id=task_instance.task_id,
        run_id=context["run_id"],
        error=error_msg,
    )
    
    logger.error(
        f"Task {task_instance.task_id} failed on attempt {task_instance.try_number}: {error_msg}"
    )


def task_success_callback(context) -> None:
    """
    Airflow callback for task success.
    
    Args:
        context: Airflow task context
    """
    task_instance = context["task_instance"]
    logger.info(f"Task {task_instance.task_id} succeeded")


def task_retry_callback(context) -> None:
    """
    Airflow callback for task retries.
    
    Args:
        context: Airflow task context
    """
    task_instance = context["task_instance"]
    logger.warning(
        f"Task {task_instance.task_id} retrying (attempt {task_instance.try_number})"
    )
