"""
Data Validation and Profiling Pipeline

Main orchestrator that runs validation and profiling on all datasets
and generates comprehensive quality reports.
"""

from pathlib import Path
from typing import Dict, Any

from src.config.config import CSV_FILES, METADATA_FILE
from src.validation.data_validator import DataValidator
from src.validation.data_profiler import DataProfiler
from src.validation.report_generator import DataQualityReportGenerator
from src.utils.logger import logger
from src.utils.helper import save_json


class DataValidationPipeline:
    """
    Orchestrates data validation, profiling, and report generation.
    """

    def __init__(self):
        """Initialize pipeline components."""
        self.validator = DataValidator()
        self.profiler = DataProfiler()
        self.report_generator = DataQualityReportGenerator()

    def run_validation(
        self,
        datasets: Dict[str, Path] = None,
        custom_constraints: Dict[str, Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run complete validation and profiling pipeline.

        Args:
            datasets: Dict of dataset names and file paths
            custom_constraints: Custom validation constraints per dataset

        Returns:
            Dictionary with validation results and profiling
        """

        logger.info("=" * 80)
        logger.info("DATA VALIDATION PIPELINE STARTED")
        logger.info("=" * 80)

        if datasets is None:
            datasets = CSV_FILES

        # Define schemas for each dataset
        schemas = {
            "movies": {"movieId": "int", "title": "str", "genres": "str"},
            "ratings": {
                "userId": "int",
                "movieId": "int",
                "rating": "float",
                "timestamp": "int",
            },
            "tags": {
                "userId": "int",
                "movieId": "int",
                "tag": "str",
                "timestamp": "int",
            },
            "links": {"movieId": "int", "imdbId": "int", "tmdbId": "int"},
        }

        # Define constraints for each dataset
        if custom_constraints is None:
            custom_constraints = {
                "ratings": {
                    "rating": {
                        "type": "range",
                        "min": 0.5,
                        "max": 5.0,
                    },
                    "userId": {
                        "type": "range",
                        "min": 1,
                    },
                    "movieId": {
                        "type": "range",
                        "min": 1,
                    },
                },
            }

        # Run validation for each dataset
        validation_results = {}
        for dataset_name, file_path in datasets.items():
            schema = schemas.get(dataset_name, {})
            constraints = custom_constraints.get(dataset_name)

            result = self.validator.validate_csv(
                file_path,
                dataset_name,
                schema,
                constraints,
            )
            validation_results[dataset_name] = result

        logger.info("=" * 80)
        logger.info("VALIDATION PHASE COMPLETED")
        logger.info("=" * 80)

        # Run profiling for each dataset
        logger.info("=" * 80)
        logger.info("DATA PROFILING PHASE STARTED")
        logger.info("=" * 80)

        for dataset_name, file_path in datasets.items():
            self.profiler.profile_dataset(file_path, dataset_name)

        profiling_summary = self.profiler.get_summary()

        logger.info("=" * 80)
        logger.info("DATA PROFILING PHASE COMPLETED")
        logger.info("=" * 80)

        # Generate report
        logger.info("=" * 80)
        logger.info("REPORT GENERATION STARTED")
        logger.info("=" * 80)

        report_path = self.report_generator.generate_report(
            validation_results,
            profiling_summary,
        )

        logger.info("=" * 80)
        logger.info("REPORT GENERATION COMPLETED")
        logger.info("=" * 80)

        # Prepare results summary
        results = {
            "status": "COMPLETED",
            "timestamp": profiling_summary.get("profiles", {}).get(
                list(profiling_summary.get("profiles", {}).keys())[0] if profiling_summary.get("profiles") else None,
                {}
            ).get("timestamp", ""),
            "validation": validation_results,
            "profiling": profiling_summary,
            "report_path": str(report_path),
        }

        # Save results to JSON
        results_file = Path(__file__).resolve().parents[2] / "data" / "reports" / "validation_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        save_json(results, results_file)

        logger.info(f"Validation results saved to: {results_file}")
        logger.info(f"Report generated at: {report_path}")

        return results

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print summary of validation and profiling results."""

        print("\n" + "=" * 80)
        print("DATA QUALITY VALIDATION SUMMARY")
        print("=" * 80)

        # Validation summary
        validation_results = results.get("validation", {})
        passed = sum(1 for r in validation_results.values() if r["status"] == "PASS")
        failed = len(validation_results) - passed

        print(f"\n✓ Datasets Validated: {len(validation_results)}")
        print(f"  - Passed: {passed}")
        print(f"  - Failed: {failed}")

        # Issues summary
        all_issues = []
        for result in validation_results.values():
            all_issues.extend(result.get("issues", []))

        if all_issues:
            print(f"\n⚠ Total Issues Found: {len(all_issues)}")
            issue_types = {}
            for issue in all_issues:
                issue_type = issue.get("type", "Unknown")
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            for issue_type, count in issue_types.items():
                print(f"  - {issue_type}: {count}")

        # Quality metrics
        profiling = results.get("profiling", {})
        profiles = profiling.get("profiles", {})

        print(f"\n📊 Quality Metrics:")
        for dataset_name, profile in profiles.items():
            metrics = profile.get("data_quality_metrics", {})
            quality_score = metrics.get("overall_quality_score", 0)
            completeness = metrics.get("completeness_percentage", 0)
            print(f"  {dataset_name}:")
            print(f"    - Quality Score: {quality_score:.2f}%")
            print(f"    - Completeness: {completeness:.2f}%")

        print(f"\n📄 Report: {results.get('report_path')}")
        print("=" * 80 + "\n")
