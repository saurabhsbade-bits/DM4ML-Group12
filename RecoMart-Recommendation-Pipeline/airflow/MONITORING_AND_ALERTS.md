# Pipeline Monitoring and Alerting Guide

## Overview

The RecoMart pipeline includes comprehensive logging, monitoring, and alerting capabilities to ensure reliable operation and quick failure detection.

## Logging Architecture

### Structured Logging

All logs are output in JSON format for easy parsing and analysis:

```json
{
  "timestamp": "2026-07-15T14:30:00.123456",
  "level": "INFO",
  "logger": "recom_pipeline",
  "message": "Task started",
  "module": "recom_pipeline",
  "function": "task_data_ingestion",
  "line": 45
}
```

### Log Locations

- **Main logs:** `airflow/logs/recom_pipeline.log`
- **Execution events:** `airflow/logs/pipeline_execution.jsonl`
- **Failures:** `airflow/logs/pipeline_failures.jsonl`
- **Alerts:** `airflow/logs/alerts.jsonl`

### Log Rotation

Logs automatically rotate when they reach 10 MB, with up to 5 backup files retained.

## Task Callbacks

Each task in the pipeline has three callbacks configured:

### 1. Success Callback (`task_success_callback`)

Triggered when a task completes successfully.

**Action:** Logs task completion info

```python
Task {task_id} succeeded
```

### 2. Failure Callback (`task_failure_callback`)

Triggered when a task fails after all retries are exhausted.

**Actions:**
- Logs failure with error message
- Records failure in `pipeline_failures.jsonl`
- Calls AlertManager to send notifications

```python
Task {task_id} failed: {error_message}
```

### 3. Retry Callback (`task_retry_callback`)

Triggered when a task is retried.

**Action:** Logs retry attempt number

```python
Task {task_id} retrying (attempt {try_number})
```

## Retry Configuration

Each task has configurable retry settings:

| Task | Retries | Delay |
|------|---------|-------|
| Data Ingestion | 2 | 5 min |
| Data Validation | 1 | 3 min |
| Data Preparation | 1 | 3 min |
| Feature Engineering | 1 | 3 min |
| Feature Store | 1 | 3 min |
| Model Training | 2 | 5 min |

## Monitoring

### Pipeline Execution Monitoring

The `PipelineMonitor` class tracks all pipeline executions:

```python
from airflow.monitoring import PipelineMonitor

monitor = PipelineMonitor(Path("airflow/logs"))

# Log execution event
monitor.log_execution(
    dag_id="recom_pipeline",
    run_id="2026-07-15T14:30:00",
    status="SUCCESS",
    metrics={"duration": 3600, "tasks_completed": 6}
)
```

### Monitoring Metrics

Each execution event includes:
- Timestamp
- DAG ID
- Run ID
- Execution status
- Pipeline metrics (duration, task count, etc.)

### Accessing Execution History

```python
# Get execution log
with open("airflow/logs/pipeline_execution.jsonl", "r") as f:
    for line in f:
        event = json.loads(line)
        print(event)
```

### Failure Summary

Get recent failure information:

```python
failure_summary = monitor.get_failure_summary()
# Returns:
# {
#   "total_failures": 2,
#   "recent_failures": [
#     {
#       "timestamp": "2026-07-15T14:30:00",
#       "dag_id": "recom_pipeline",
#       "task_id": "ingest_data",
#       "error": "Connection timeout"
#     }
#   ]
# }
```

## Alerting

### Alert Types

The system supports multiple alert types:

1. **TASK_FAILURE** - Task failed after all retries
2. **SLA_MISS** - Task exceeded time SLA
3. **DATA_QUALITY_ALERT** - Data quality metric below threshold

### Alert Manager

```python
from airflow.alerts import AlertManager

alert_manager = AlertManager(
    log_dir=Path("airflow/logs"),
    smtp_config={
        "host": "smtp.gmail.com",
        "port": 587,
        "user": "your-email@gmail.com",
        "password": "your-app-password",
        "recipient": "alerts@recomart.com"
    },
    slack_webhook="https://hooks.slack.com/services/YOUR/WEBHOOK"
)

# Alert on task failure
alert_manager.alert_on_failure(
    dag_id="recom_pipeline",
    task_id="ingest_data",
    error="Connection timeout",
    context=airflow_context
)

# Alert on SLA miss
alert_manager.alert_on_sla_miss(
    dag_id="recom_pipeline",
    task_id="train_model",
    sla_seconds=7200,  # 2 hours
    actual_seconds=9000  # 2.5 hours
)

# Alert on data quality
alert_manager.alert_on_data_quality(
    dag_id="recom_pipeline",
    quality_metric="completeness",
    threshold=0.95,
    actual=0.92
)
```

### Integration with Airflow

Alerts are automatically sent when task callbacks are triggered:

```python
PythonOperator(
    task_id="ingest_data",
    python_callable=my_task,
    on_failure_callback=task_failure_callback,  # Sends alert on failure
    on_success_callback=task_success_callback,  # Logs success
)
```

### Alert Notification Channels

#### Email Alerts

Requires SMTP configuration. Set up environment variables:

```bash
export AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
export AIRFLOW__SMTP__SMTP_PORT=587
export AIRFLOW__SMTP__SMTP_USER=your-email@gmail.com
export AIRFLOW__SMTP__SMTP_PASSWORD=your-app-password
```

#### Slack Alerts

Set Slack webhook URL:

```python
alert_manager = AlertManager(
    log_dir=Path("airflow/logs"),
    slack_webhook="https://hooks.slack.com/services/YOUR/WEBHOOK"
)
```

### Alert Summary

Get recent alerts:

```python
summary = alert_manager.get_alert_summary(hours=24)
# Returns:
# {
#   "total_alerts": 3,
#   "by_type": {
#     "TASK_FAILURE": 2,
#     "SLA_MISS": 1
#   },
#   "recent_alerts": [...]
# }
```

## Monitoring Dashboard

### Airflow UI

Access at http://localhost:8080

**Available views:**
- **DAG view:** Pipeline structure and dependencies
- **Tree view:** Historical execution and status
- **Graph view:** Task-level execution timeline
- **Logs:** Detailed task logs

### Log Files

Analyze logs directly:

```bash
# View main log
tail -f airflow/logs/recom_pipeline.log

# View failures
cat airflow/logs/pipeline_failures.jsonl | jq .

# View alerts
cat airflow/logs/alerts.jsonl | jq .
```

### Log Analysis Scripts

Example Python script to analyze execution logs:

```python
import json
from pathlib import Path

log_file = Path("airflow/logs/pipeline_execution.jsonl")

total_duration = 0
success_count = 0

with open(log_file, "r") as f:
    for line in f:
        event = json.loads(line)
        if event["status"] == "SUCCESS":
            success_count += 1
            total_duration += event["metrics"].get("duration", 0)

avg_duration = total_duration / success_count if success_count > 0 else 0
print(f"Successful runs: {success_count}")
print(f"Average duration: {avg_duration}s")
```

## Best Practices

1. **Regular Log Review:** Check failure logs daily
2. **Alert Threshold Tuning:** Adjust SLA thresholds based on expected performance
3. **Log Retention:** Archive old logs monthly
4. **Monitoring:** Set up dashboards for key metrics
5. **Testing:** Test alert channels before going to production

## Troubleshooting

### Logs Not Being Created

1. Check `AIRFLOW_HOME` is set correctly
2. Verify write permissions on `airflow/logs/` directory
3. Ensure `configure_logging()` is called before any tasks run

### Alerts Not Sending

1. Verify SMTP/Slack configuration
2. Check network connectivity
3. Review alert handler logs for errors

### Missing Execution Events

1. Ensure `PipelineMonitor.log_execution()` is called
2. Check `pipeline_execution.jsonl` file exists
3. Verify write permissions on log directory

## See Also

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Main DAG](dags/recom_pipeline.py)
- [Monitoring Module](monitoring.py)
- [Alerts Module](alerts.py)
- [README](README.md)
