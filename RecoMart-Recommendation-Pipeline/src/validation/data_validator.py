"""
Data Validator Module

Performs comprehensive data quality validation checks on ingested datasets.
Validates schema, missing values, duplicates, data types, and business logic constraints.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from src.utils.logger import logger


class DataValidator:
    """
    Comprehensive data validation framework for structured datasets.
    """

    def __init__(self):
        """Initialize validator with empty validation results."""
        self.validation_results = {}
        self.issues = []

    def validate_csv(
        self,
        file_path: Path,
        dataset_name: str,
        schema: Dict[str, str],
        constraints: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Validate a CSV dataset against schema and constraints.

        Args:
            file_path: Path to CSV file
            dataset_name: Name of dataset for reporting
            schema: Expected schema {column_name: data_type}
            constraints: Optional validation constraints (ranges, allowed values, etc.)

        Returns:
            Dictionary with validation results
        """

        logger.info(f"Starting validation for {dataset_name}")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return {
                "dataset": dataset_name,
                "status": "FAILED",
                "error": str(e),
                "passed": 0,
                "failed": 1,
                "issues": [{"check": "File Read", "message": str(e)}],
            }

        results = {
            "dataset": dataset_name,
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "checks": {},
            "issues": [],
        }

        # 1. Schema Validation
        results["checks"]["schema"] = self._validate_schema(df, schema, results)

        # 2. Missing Values Check
        results["checks"]["missing_values"] = self._validate_missing_values(
            df, results
        )

        # 3. Duplicate Rows Check
        results["checks"]["duplicates"] = self._validate_duplicates(df, results)

        # 4. Data Types Check
        results["checks"]["data_types"] = self._validate_data_types(df, schema, results)

        # 5. Business Logic Constraints
        if constraints:
            results["checks"]["constraints"] = self._validate_constraints(
                df, constraints, results
            )

        # Summary
        passed = sum(
            1 for check in results["checks"].values() if check.get("status") == "PASS"
        )
        total = len(results["checks"])

        results["status"] = "PASS" if len(results["issues"]) == 0 else "FAIL"
        results["passed"] = passed
        results["failed"] = total - passed

        logger.info(
            f"Validation completed for {dataset_name}: {results['status']} "
            f"({passed}/{total} checks passed)"
        )

        self.validation_results[dataset_name] = results
        return results

    def _validate_schema(
        self, df: pd.DataFrame, schema: Dict[str, str], results: Dict
    ) -> Dict:
        """Validate that all expected columns exist."""
        check = {"check": "Schema Validation", "details": {}}

        missing_columns = set(schema.keys()) - set(df.columns)
        extra_columns = set(df.columns) - set(schema.keys())

        if missing_columns or extra_columns:
            check["status"] = "FAIL"
            check["message"] = f"Schema mismatch detected"
            if missing_columns:
                check["details"]["missing_columns"] = list(missing_columns)
            if extra_columns:
                check["details"]["extra_columns"] = list(extra_columns)
            results["issues"].append(
                {
                    "type": "Schema Mismatch",
                    "severity": "HIGH",
                    "message": f"Missing: {missing_columns}, Extra: {extra_columns}",
                }
            )
        else:
            check["status"] = "PASS"
            check["message"] = "All required columns present"

        check["columns_found"] = list(df.columns)
        check["columns_expected"] = list(schema.keys())

        return check

    def _validate_missing_values(self, df: pd.DataFrame, results: Dict) -> Dict:
        """Check for missing/null values in each column."""
        check = {"check": "Missing Values", "details": {}}

        missing_info = {}
        total_missing = 0

        for column in df.columns:
            null_count = df[column].isna().sum()
            null_pct = (null_count / len(df)) * 100

            if null_count > 0:
                missing_info[column] = {
                    "null_count": int(null_count),
                    "null_percentage": round(null_pct, 2),
                }
                total_missing += null_count

        if total_missing > 0:
            check["status"] = "FAIL"
            check["message"] = f"Found {total_missing} null values across columns"
            check["details"] = missing_info
            results["issues"].append(
                {
                    "type": "Missing Values",
                    "severity": "MEDIUM",
                    "message": f"Total missing values: {total_missing}",
                    "details": missing_info,
                }
            )
        else:
            check["status"] = "PASS"
            check["message"] = "No missing values detected"
            check["details"] = {"null_count": 0, "affected_columns": []}

        return check

    def _validate_duplicates(self, df: pd.DataFrame, results: Dict) -> Dict:
        """Check for duplicate rows."""
        check = {"check": "Duplicate Detection", "details": {}}

        duplicate_count = df.duplicated().sum()
        duplicate_pct = (duplicate_count / len(df)) * 100

        if duplicate_count > 0:
            check["status"] = "FAIL"
            check["message"] = f"Found {duplicate_count} duplicate rows"
            check["details"] = {
                "duplicate_count": int(duplicate_count),
                "duplicate_percentage": round(duplicate_pct, 2),
            }
            results["issues"].append(
                {
                    "type": "Duplicate Records",
                    "severity": "MEDIUM",
                    "message": f"Found {duplicate_count} duplicate rows ({duplicate_pct:.2f}%)",
                }
            )
        else:
            check["status"] = "PASS"
            check["message"] = "No duplicate rows detected"
            check["details"] = {"duplicate_count": 0}

        return check

    def _validate_data_types(
        self, df: pd.DataFrame, schema: Dict[str, str], results: Dict
    ) -> Dict:
        """Validate data types match expected schema."""
        check = {"check": "Data Type Validation", "details": {}}

        type_issues = {}
        type_mapping = {
            "int": ("int64", "int32", "int"),
            "float": ("float64", "float32", "float"),
            "str": ("object", "string"),
            "datetime": ("datetime64",),
        }

        for column, expected_type in schema.items():
            if column not in df.columns:
                continue

            actual_type = str(df[column].dtype)
            expected_types = type_mapping.get(expected_type, (expected_type,))

            if not any(exp in actual_type for exp in expected_types):
                type_issues[column] = {
                    "expected": expected_type,
                    "actual": actual_type,
                }

        if type_issues:
            check["status"] = "FAIL"
            check["message"] = f"Data type mismatches found in {len(type_issues)} columns"
            check["details"] = type_issues
            results["issues"].append(
                {
                    "type": "Data Type Mismatch",
                    "severity": "MEDIUM",
                    "message": f"Type mismatches in: {list(type_issues.keys())}",
                }
            )
        else:
            check["status"] = "PASS"
            check["message"] = "All data types match schema"
            check["details"] = {}

        return check

    def _validate_constraints(
        self, df: pd.DataFrame, constraints: Dict[str, Any], results: Dict
    ) -> Dict:
        """
        Validate business logic constraints.

        Args:
            df: DataFrame
            constraints: Dict with constraint definitions
                {
                    "column_name": {
                        "type": "range|enum|format|referential",
                        "min": value,
                        "max": value,
                        "allowed_values": [...],
                        "pattern": regex_pattern,
                        "unique": bool
                    }
                }
        """
        check = {"check": "Business Logic Constraints", "details": {}}

        constraint_issues = {}

        for column, constraint in constraints.items():
            if column not in df.columns:
                continue

            column_issues = {}

            # Range checks
            if "min" in constraint or "max" in constraint:
                min_val = constraint.get("min")
                max_val = constraint.get("max")

                out_of_range = df[
                    (df[column] < min_val) | (df[column] > max_val)
                ].shape[0]

                if out_of_range > 0:
                    column_issues["range_check"] = {
                        "violations": int(out_of_range),
                        "range": f"[{min_val}, {max_val}]",
                    }

            # Allowed values/enum check
            if "allowed_values" in constraint:
                allowed = set(constraint["allowed_values"])
                invalid_values = df[~df[column].isin(allowed)].shape[0]

                if invalid_values > 0:
                    column_issues["enum_check"] = {
                        "violations": int(invalid_values),
                        "allowed": allowed,
                    }

            # Uniqueness check
            if constraint.get("unique", False):
                duplicates = df[column].duplicated().sum()
                if duplicates > 0:
                    column_issues["unique_check"] = {"duplicates": int(duplicates)}

            if column_issues:
                constraint_issues[column] = column_issues

        if constraint_issues:
            check["status"] = "FAIL"
            check["message"] = f"Constraint violations found"
            check["details"] = constraint_issues
            results["issues"].append(
                {
                    "type": "Constraint Violation",
                    "severity": "HIGH",
                    "message": f"Business logic violations in: {list(constraint_issues.keys())}",
                }
            )
        else:
            check["status"] = "PASS"
            check["message"] = "All constraints satisfied"
            check["details"] = {}

        return check

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all validation results."""
        if not self.validation_results:
            return {
                "total_datasets": 0,
                "passed": 0,
                "failed": 0,
                "total_issues": 0,
            }

        total_datasets = len(self.validation_results)
        passed_datasets = sum(
            1
            for result in self.validation_results.values()
            if result["status"] == "PASS"
        )
        failed_datasets = total_datasets - passed_datasets

        all_issues = []
        for result in self.validation_results.values():
            all_issues.extend(result.get("issues", []))

        return {
            "total_datasets": total_datasets,
            "passed_datasets": passed_datasets,
            "failed_datasets": failed_datasets,
            "total_issues": len(all_issues),
            "issue_summary": self._categorize_issues(all_issues),
            "validation_results": self.validation_results,
        }

    def _categorize_issues(self, issues: List[Dict]) -> Dict[str, int]:
        """Categorize issues by type."""
        categories = {}
        for issue in issues:
            issue_type = issue.get("type", "Unknown")
            categories[issue_type] = categories.get(issue_type, 0) + 1
        return categories
