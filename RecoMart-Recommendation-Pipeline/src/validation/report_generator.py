"""
Data Quality Report Generator

Generates comprehensive PDF reports with validation results,
data profiles, and quality metrics.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Union

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        PageBreak,
        Image,
        KeepTogether,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    Table = None
    TableStyle = None

from src.utils.logger import logger


class DataQualityReportGenerator:
    """
    Generates comprehensive PDF reports for data quality validation.
    """

    def __init__(self, output_dir: Path = None):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports (default: data/reports)
        """
        if output_dir is None:
            output_dir = Path(__file__).resolve().parents[2] / "data" / "reports"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        validation_results: Dict[str, Any],
        profiling_results: Dict[str, Any],
        report_name: str = None,
    ) -> Path:
        """
        Generate comprehensive PDF report.

        Args:
            validation_results: Results from DataValidator
            profiling_results: Results from DataProfiler
            report_name: Optional custom report name

        Returns:
            Path to generated PDF report
        """

        if not REPORTLAB_AVAILABLE:
            logger.error(
                "reportlab not installed. Install with: pip install reportlab"
            )
            return self._generate_html_fallback(
                validation_results, profiling_results, report_name
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = report_name or f"DataQualityReport_{timestamp}.pdf"
        report_path = self.output_dir / report_name

        logger.info(f"Generating PDF report: {report_path}")

        try:
            doc = SimpleDocTemplate(
                str(report_path),
                pagesize=letter,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )

            story = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f4788"),
                spaceAfter=30,
                alignment=TA_CENTER,
            )

            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#2c5aa0"),
                spaceAfter=12,
                spaceBefore=12,
            )

            # Title Page
            story.append(Spacer(1, 0.5 * inch))
            story.append(
                Paragraph("Data Quality Report", title_style)
            )
            story.append(
                Paragraph(
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.5 * inch))

            # Executive Summary
            story.append(Paragraph("Executive Summary", heading_style))
            summary_data = self._create_summary_table(
                validation_results, profiling_results
            )
            story.append(summary_data)
            story.append(Spacer(1, 0.3 * inch))

            # Validation Results
            story.append(PageBreak())
            story.append(Paragraph("Data Validation Results", heading_style))
            story.extend(
                self._create_validation_section(validation_results, styles)
            )

            # Data Profiles
            story.append(PageBreak())
            story.append(Paragraph("Data Profiling & Statistics", heading_style))
            story.extend(self._create_profiling_section(profiling_results, styles))

            # Quality Metrics
            story.append(PageBreak())
            story.append(Paragraph("Data Quality Metrics", heading_style))
            story.extend(self._create_metrics_section(profiling_results, styles))

            # Issues & Recommendations
            if any(
                result.get("issues") for result in validation_results.values()
            ):
                story.append(PageBreak())
                story.append(Paragraph("Issues & Recommendations", heading_style))
                story.extend(self._create_issues_section(validation_results, styles))

            # Build PDF
            doc.build(story)
            logger.info(f"Report successfully generated: {report_path}")

            return report_path

        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return self._generate_html_fallback(
                validation_results, profiling_results, report_name
            )

    def _create_summary_table(
        self,
        validation_results: Dict[str, Any],
        profiling_results: Dict[str, Any],
    ) -> Union[Any, None]:
        """Create executive summary table."""
        if not REPORTLAB_AVAILABLE:
            return None

        val_summary = self._get_validation_summary(validation_results)
        prof_summary = self._get_profiling_summary(profiling_results)

        data = [
            ["Metric", "Value"],
            ["Total Datasets", str(len(validation_results))],
            ["Datasets Passed Validation", str(val_summary["passed"])],
            ["Datasets with Issues", str(val_summary["failed"])],
            ["Total Validation Issues", str(val_summary["total_issues"])],
            ["Average Quality Score", f"{prof_summary['avg_quality']:.2f}%"],
        ]

        table = Table(data, colWidths=[3 * inch, 2.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        return table

    def _create_validation_section(
        self, validation_results: Dict[str, Any], styles
    ) -> List:
        """Create validation results section."""
        story = []

        for dataset_name, result in validation_results.items():
            # Dataset header
            status_color = (
                colors.green if result["status"] == "PASS" else colors.red
            )
            story.append(
                Paragraph(
                    f"<b>{dataset_name}</b> - Status: <font color='{status_color}'>{result['status']}</font>",
                    styles["Heading3"],
                )
            )

            # Dataset info table
            info_data = [
                ["Total Rows", str(result["total_rows"])],
                ["Total Columns", str(result["total_columns"])],
                ["Validation Checks Passed", f"{result['passed']}/{result['passed'] + result['failed']}"],
            ]

            info_table = Table(info_data, colWidths=[2.5 * inch, 2.5 * inch])
            info_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(info_table)
            story.append(Spacer(1, 0.2 * inch))

            # Validation checks
            checks_data = [["Check", "Status", "Details"]]
            for check_name, check_result in result.get("checks", {}).items():
                status = check_result.get("status", "N/A")
                message = check_result.get("message", "")
                status_color = colors.green if status == "PASS" else colors.red
                checks_data.append(
                    [
                        check_name.replace("_", " ").title(),
                        Paragraph(
                            f"<font color='{status_color}'><b>{status}</b></font>",
                            styles["Normal"],
                        ),
                        message[:50] + ("..." if len(message) > 50 else ""),
                    ]
                )

            checks_table = Table(checks_data, colWidths=[1.8 * inch, 1.2 * inch, 2.5 * inch])
            checks_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(checks_table)
            story.append(Spacer(1, 0.3 * inch))

        return story

    def _create_profiling_section(
        self, profiling_results: Dict[str, Any], styles
    ) -> List:
        """Create data profiling section."""
        story = []

        for dataset_name, profile in profiling_results.get("profiles", {}).items():
            story.append(Paragraph(f"<b>{dataset_name}</b>", styles["Heading3"]))

            # Column profiles
            col_profiles = profile.get("column_profiles", {})
            for col_name, col_profile in col_profiles.items():
                col_data = [
                    ["Column", col_name],
                    ["Data Type", col_profile.get("data_type", "N/A")],
                    ["Non-Null Count", str(col_profile.get("non_null_count", 0))],
                    ["Null %", f"{col_profile.get('null_percentage', 0):.2f}%"],
                    ["Unique Values", str(col_profile.get("unique_values", 0))],
                ]

                if "min" in col_profile:
                    col_data.extend(
                        [
                            ["Min", f"{col_profile['min']:.2f}"],
                            ["Max", f"{col_profile['max']:.2f}"],
                            ["Mean", f"{col_profile['mean']:.2f}"],
                            ["Std Dev", f"{col_profile['std_dev']:.2f}"],
                        ]
                    )

                col_table = Table(col_data, colWidths=[2 * inch, 3.5 * inch])
                col_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ]
                    )
                )
                story.append(col_table)
                story.append(Spacer(1, 0.1 * inch))

            story.append(Spacer(1, 0.2 * inch))

        return story

    def _create_metrics_section(
        self, profiling_results: Dict[str, Any], styles
    ) -> List:
        """Create quality metrics section."""
        story = []

        for dataset_name, profile in profiling_results.get("profiles", {}).items():
            story.append(Paragraph(f"<b>{dataset_name}</b>", styles["Heading3"]))

            metrics = profile.get("data_quality_metrics", {})
            metrics_data = [
                ["Metric", "Value"],
                ["Completeness", f"{metrics.get('completeness_percentage', 0):.2f}%"],
                ["Validity", f"{metrics.get('validity_percentage', 0):.2f}%"],
                ["Quality Score", f"{metrics.get('overall_quality_score', 0):.2f}%"],
                ["Total Cells", str(metrics.get("total_cells", 0))],
                ["Missing Cells", str(metrics.get("missing_cells", 0))],
            ]

            metrics_table = Table(metrics_data, colWidths=[2.5 * inch, 2.5 * inch])
            metrics_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(metrics_table)
            story.append(Spacer(1, 0.3 * inch))

        return story

    def _create_issues_section(
        self, validation_results: Dict[str, Any], styles
    ) -> List:
        """Create issues and recommendations section."""
        story = []

        all_issues = []
        for result in validation_results.values():
            all_issues.extend(result.get("issues", []))

        if not all_issues:
            story.append(Paragraph("No data quality issues detected.", styles["Normal"]))
            return story

        issues_data = [["Dataset", "Issue Type", "Severity", "Message"]]
        for result in validation_results.values():
            for issue in result.get("issues", []):
                dataset_name = result.get("dataset", "Unknown")
                issue_type = issue.get("type", "Unknown")
                severity = issue.get("severity", "LOW")
                message = issue.get("message", "")[:40]

                severity_color = {
                    "HIGH": "red",
                    "MEDIUM": "orange",
                    "LOW": "green",
                }.get(severity, "black")

                issues_data.append(
                    [
                        dataset_name,
                        issue_type,
                        Paragraph(
                            f"<font color='{severity_color}'><b>{severity}</b></font>",
                            styles["Normal"],
                        ),
                        message,
                    ]
                )

        issues_table = Table(issues_data, colWidths=[1.5 * inch, 1.8 * inch, 1.2 * inch, 1.8 * inch])
        issues_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        story.append(issues_table)

        return story

    def _generate_html_fallback(
        self,
        validation_results: Dict[str, Any],
        profiling_results: Dict[str, Any],
        report_name: str = None,
    ) -> Path:
        """Generate HTML report as fallback when reportlab is unavailable."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = report_name or f"DataQualityReport_{timestamp}.html"
        report_path = self.output_dir / report_name

        html_content = """
        <html>
        <head>
            <title>Data Quality Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #1f4788; }
                h2 { color: #2c5aa0; margin-top: 30px; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
                th { background-color: #2c5aa0; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .pass { color: green; font-weight: bold; }
                .fail { color: red; font-weight: bold; }
                .high { color: red; }
                .medium { color: orange; }
                .low { color: green; }
            </style>
        </head>
        <body>
        """

        html_content += f"<h1>Data Quality Report</h1>"
        html_content += f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"

        # Summary
        val_summary = self._get_validation_summary(validation_results)
        prof_summary = self._get_profiling_summary(profiling_results)

        html_content += "<h2>Executive Summary</h2>"
        html_content += f"<table>"
        html_content += f"<tr><th>Metric</th><th>Value</th></tr>"
        html_content += f"<tr><td>Total Datasets</td><td>{len(validation_results)}</td></tr>"
        html_content += f"<tr><td>Datasets Passed</td><td class='pass'>{val_summary['passed']}</td></tr>"
        html_content += f"<tr><td>Datasets with Issues</td><td class='fail'>{val_summary['failed']}</td></tr>"
        html_content += f"<tr><td>Total Issues</td><td>{val_summary['total_issues']}</td></tr>"
        html_content += f"<tr><td>Average Quality Score</td><td>{prof_summary['avg_quality']:.2f}%</td></tr>"
        html_content += "</table>"

        # Validation results
        html_content += "<h2>Validation Results</h2>"
        for dataset_name, result in validation_results.items():
            status_class = "pass" if result["status"] == "PASS" else "fail"
            html_content += f"<h3>{dataset_name} - <span class='{status_class}'>{result['status']}</span></h3>"
            html_content += f"<table>"
            html_content += f"<tr><th>Check</th><th>Status</th><th>Details</th></tr>"
            for check_name, check_result in result.get("checks", {}).items():
                status = check_result.get("status", "N/A")
                status_class = "pass" if status == "PASS" else "fail"
                message = check_result.get("message", "")
                html_content += (
                    f"<tr><td>{check_name}</td><td class='{status_class}'>{status}</td><td>{message}</td></tr>"
                )
            html_content += "</table>"

        html_content += "</body></html>"

        with open(report_path, "w") as f:
            f.write(html_content)

        logger.info(f"HTML report generated: {report_path}")
        return report_path

    def _get_validation_summary(self, validation_results: Dict) -> Dict:
        """Extract validation summary."""
        passed = sum(1 for r in validation_results.values() if r["status"] == "PASS")
        failed = len(validation_results) - passed
        total_issues = sum(len(r.get("issues", [])) for r in validation_results.values())

        return {
            "passed": passed,
            "failed": failed,
            "total_issues": total_issues,
        }

    def _get_profiling_summary(self, profiling_results: Dict) -> Dict:
        """Extract profiling summary."""
        quality_scores = [
            profile["data_quality_metrics"]["overall_quality_score"]
            for profile in profiling_results.get("profiles", {}).values()
        ]

        avg_quality = (
            sum(quality_scores) / len(quality_scores)
            if quality_scores
            else 0
        )

        return {"avg_quality": avg_quality}
