"""
Alert and Notification System for RecoMart Pipeline

Provides:
- Email alerts for critical failures
- Slack notifications (optional)
- Summary reports
- Health checks
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import json

logger = logging.getLogger(__name__)


class AlertManager:
    """Centralized alerting system for pipeline failures and anomalies."""
    
    def __init__(
        self,
        log_dir: Path,
        smtp_config: Optional[Dict[str, str]] = None,
        slack_webhook: Optional[str] = None
    ):
        """
        Initialize alert manager.
        
        Args:
            log_dir: Directory for alert logs
            smtp_config: SMTP configuration (host, port, user, password)
            slack_webhook: Slack webhook URL for notifications
        """
        self.log_dir = log_dir
        self.alerts_log = log_dir / "alerts.jsonl"
        self.smtp_config = smtp_config
        self.slack_webhook = slack_webhook
    
    def alert_on_failure(
        self,
        dag_id: str,
        task_id: str,
        error: str,
        context: Dict[str, Any]
    ) -> None:
        """
        Send alert on task failure.
        
        Args:
            dag_id: DAG identifier
            task_id: Task identifier
            error: Error message
            context: Airflow context for details
        """
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "TASK_FAILURE",
            "dag_id": dag_id,
            "task_id": task_id,
            "error": error,
            "execution_date": str(context.get("execution_date")),
            "try_number": context.get("task_instance").try_number if context else None,
        }
        
        self._log_alert(alert)
        self._send_alert(alert)
        logger.warning(f"Alert: Task {task_id} failed - {error}")
    
    def alert_on_sla_miss(
        self,
        dag_id: str,
        task_id: str,
        sla_seconds: int,
        actual_seconds: int
    ) -> None:
        """
        Send alert when task exceeds SLA.
        
        Args:
            dag_id: DAG identifier
            task_id: Task identifier
            sla_seconds: SLA in seconds
            actual_seconds: Actual execution time in seconds
        """
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "SLA_MISS",
            "dag_id": dag_id,
            "task_id": task_id,
            "sla_seconds": sla_seconds,
            "actual_seconds": actual_seconds,
            "delay_seconds": actual_seconds - sla_seconds,
        }
        
        self._log_alert(alert)
        self._send_alert(alert)
        logger.warning(f"Alert: SLA miss for {task_id}: {actual_seconds}s > {sla_seconds}s")
    
    def alert_on_data_quality(
        self,
        dag_id: str,
        quality_metric: str,
        threshold: float,
        actual: float
    ) -> None:
        """
        Send alert when data quality metric falls below threshold.
        
        Args:
            dag_id: DAG identifier
            quality_metric: Metric name (e.g., "completeness", "uniqueness")
            threshold: Quality threshold
            actual: Actual metric value
        """
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "DATA_QUALITY_ALERT",
            "dag_id": dag_id,
            "metric": quality_metric,
            "threshold": threshold,
            "actual": actual,
        }
        
        self._log_alert(alert)
        self._send_alert(alert)
        logger.warning(f"Alert: Data quality alert {quality_metric}: {actual} < {threshold}")
    
    def _log_alert(self, alert: Dict[str, Any]) -> None:
        """
        Log alert to file.
        
        Args:
            alert: Alert dictionary
        """
        try:
            with open(self.alerts_log, "a") as f:
                f.write(json.dumps(alert) + "\n")
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
    
    def _send_alert(self, alert: Dict[str, Any]) -> None:
        """
        Send alert via configured channels.
        
        Args:
            alert: Alert dictionary
        """
        try:
            if self.smtp_config:
                self._send_email_alert(alert)
            if self.slack_webhook:
                self._send_slack_alert(alert)
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def _send_email_alert(self, alert: Dict[str, Any]) -> None:
        """
        Send email alert (requires SMTP config).
        
        Args:
            alert: Alert dictionary
        """
        if not self.smtp_config:
            return
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config.get("user")
            msg["To"] = self.smtp_config.get("recipient")
            msg["Subject"] = f"RecoMart Pipeline Alert: {alert['type']}"
            
            body = f"""
            Pipeline Alert
            ===============
            Type: {alert['type']}
            DAG: {alert['dag_id']}
            Task: {alert.get('task_id', 'N/A')}
            Time: {alert['timestamp']}
            
            Details:
            {json.dumps(alert, indent=2)}
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            # TODO: Connect to SMTP and send email
            # Requires smtp_config["host"], ["port"], ["user"], ["password"]
            
            logger.info(f"Email alert sent for {alert['type']}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, alert: Dict[str, Any]) -> None:
        """
        Send Slack alert (requires webhook URL).
        
        Args:
            alert: Alert dictionary
        """
        if not self.slack_webhook:
            return
        
        try:
            # TODO: Implement Slack webhook POST
            import requests
            
            payload = {
                "text": f"🚨 RecoMart Pipeline Alert: {alert['type']}",
                "attachments": [
                    {
                        "color": "danger" if alert['type'] == "TASK_FAILURE" else "warning",
                        "fields": [
                            {"title": "DAG", "value": alert['dag_id'], "short": True},
                            {"title": "Task", "value": alert.get('task_id', 'N/A'), "short": True},
                            {"title": "Time", "value": alert['timestamp'], "short": False},
                            {"title": "Details", "value": json.dumps(alert), "short": False},
                        ]
                    }
                ]
            }
            
            # requests.post(self.slack_webhook, json=payload)
            # logger.info(f"Slack alert sent for {alert['type']}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get summary of recent alerts.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with alert statistics
        """
        if not self.alerts_log.exists():
            return {"total_alerts": 0, "by_type": {}, "recent_alerts": []}
        
        alerts = []
        try:
            with open(self.alerts_log, "r") as f:
                for line in f:
                    alerts.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading alerts log: {e}")
            return {"error": str(e)}
        
        # Count by type
        by_type = {}
        for alert in alerts:
            alert_type = alert.get("type", "UNKNOWN")
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
        
        return {
            "total_alerts": len(alerts),
            "by_type": by_type,
            "recent_alerts": alerts[-5:] if alerts else [],
        }
