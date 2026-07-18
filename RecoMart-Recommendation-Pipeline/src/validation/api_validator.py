"""
API Data Validation Module

Validates JSON data from REST APIs (e.g., product APIs)
with schema validation, data quality checks, and business logic constraints.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd

from src.utils.logger import logger


class APIValidator:
    """
    Validates API-ingested JSON data.
    
    Checks:
    - JSON structure and schema
    - Required fields presence
    - Data type validation
    - Value ranges and constraints
    - Data completeness
    """

    def __init__(self):
        """Initialize API validator."""
        self.validation_results = []
        self.issues = []

    def validate_json_file(
        self,
        file_path: Path,
        schema: Dict[str, Any],
        constraints: Dict[str, Any] = None,
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Validate a JSON file against schema and constraints.

        Args:
            file_path: Path to JSON file
            schema: Expected schema definition
            constraints: Business logic constraints

        Returns:
            Tuple of (data, validation_report)
        """
        logger.info(f"Validating API data: {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            return None, {"error": f"Invalid JSON: {e}"}
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None, {"error": f"File not found: {file_path}"}

        # If data is wrapped in 'products' key, extract it
        if isinstance(data, dict) and "products" in data:
            records = data["products"]
        else:
            records = data if isinstance(data, list) else [data]

        # Run validations
        report = {
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": 0,
            "schema_validation": {},
            "field_validation": {},
            "constraint_validation": {},
            "issues": [],
        }

        valid_records = []

        for idx, record in enumerate(records):
            record_valid = True

            # Schema validation
            schema_check = self._validate_schema(record, schema, idx)
            if not schema_check["valid"]:
                report["schema_validation"][idx] = schema_check
                record_valid = False

            # Field validation
            field_check = self._validate_fields(record, schema, idx)
            if not field_check["valid"]:
                report["field_validation"][idx] = field_check
                record_valid = False

            # Constraint validation
            if constraints:
                constraint_check = self._validate_constraints(record, constraints, idx)
                if not constraint_check["valid"]:
                    report["constraint_validation"][idx] = constraint_check
                    record_valid = False

            if record_valid:
                report["valid_records"] += 1
                valid_records.append(record)
            else:
                report["invalid_records"] += 1
                self.issues.append({
                    "record_index": idx,
                    "issues": [
                        schema_check.get("issues", []),
                        field_check.get("issues", []),
                    ]
                })

        logger.info(
            f"Validation completed: {report['valid_records']} valid, "
            f"{report['invalid_records']} invalid out of {report['total_records']}"
        )

        return valid_records, report

    def _validate_schema(
        self,
        record: Dict,
        schema: Dict,
        idx: int,
    ) -> Dict[str, Any]:
        """Validate record has expected schema structure."""
        issues = []
        valid = True

        # Check required fields
        required_fields = schema.get("required_fields", [])
        for field in required_fields:
            if field not in record:
                issues.append(f"Missing required field: {field}")
                valid = False

        return {
            "valid": valid,
            "record_index": idx,
            "issues": issues,
        }

    def _validate_fields(
        self,
        record: Dict,
        schema: Dict,
        idx: int,
    ) -> Dict[str, Any]:
        """Validate field data types and values."""
        issues = []
        valid = True

        field_types = schema.get("field_types", {})

        for field, expected_type in field_types.items():
            if field not in record:
                continue

            value = record[field]

            # Type checking
            if expected_type == "string" and not isinstance(value, str):
                issues.append(f"Field '{field}': expected string, got {type(value).__name__}")
                valid = False

            elif expected_type == "number" and not isinstance(value, (int, float)):
                issues.append(f"Field '{field}': expected number, got {type(value).__name__}")
                valid = False

            elif expected_type == "integer" and not isinstance(value, int):
                issues.append(f"Field '{field}': expected integer, got {type(value).__name__}")
                valid = False

            elif expected_type == "list" and not isinstance(value, list):
                issues.append(f"Field '{field}': expected list, got {type(value).__name__}")
                valid = False

            elif expected_type == "dict" and not isinstance(value, dict):
                issues.append(f"Field '{field}': expected dict, got {type(value).__name__}")
                valid = False

            # Check for null/empty critical fields
            if isinstance(value, str) and len(value.strip()) == 0:
                issues.append(f"Field '{field}': empty string value")
                valid = False

        return {
            "valid": valid,
            "record_index": idx,
            "issues": issues,
        }

    def _validate_constraints(
        self,
        record: Dict,
        constraints: Dict,
        idx: int,
    ) -> Dict[str, Any]:
        """Validate business logic constraints."""
        issues = []
        valid = True

        # Range constraints
        range_constraints = constraints.get("ranges", {})
        for field, (min_val, max_val) in range_constraints.items():
            if field in record:
                value = record[field]
                if isinstance(value, (int, float)):
                    if value < min_val or value > max_val:
                        issues.append(
                            f"Field '{field}': value {value} outside range [{min_val}, {max_val}]"
                        )
                        valid = False

        # Enum constraints
        enum_constraints = constraints.get("enums", {})
        for field, allowed_values in enum_constraints.items():
            if field in record:
                value = record[field]
                if value not in allowed_values:
                    issues.append(
                        f"Field '{field}': value '{value}' not in allowed values {allowed_values}"
                    )
                    valid = False

        # String length constraints
        length_constraints = constraints.get("string_length", {})
        for field, (min_len, max_len) in length_constraints.items():
            if field in record:
                value = record[field]
                if isinstance(value, str):
                    if len(value) < min_len or len(value) > max_len:
                        issues.append(
                            f"Field '{field}': length {len(value)} outside range [{min_len}, {max_len}]"
                        )
                        valid = False

        return {
            "valid": valid,
            "record_index": idx,
            "issues": issues,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "total_validations": len(self.validation_results),
            "total_issues": len(self.issues),
            "issues": self.issues,
        }


class APIDataProfiler:
    """
    Generates statistical profiles of API data.
    
    Analyzes:
    - Field distributions
    - Cardinality and uniqueness
    - Data quality metrics
    - Correlation patterns
    """

    def __init__(self):
        """Initialize API data profiler."""
        self.profiles = {}

    def profile_api_data(
        self,
        records: List[Dict],
        dataset_name: str,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive profile of API data.

        Args:
            records: List of API records (dicts)
            dataset_name: Name of dataset

        Returns:
            Profile dictionary with statistics
        """
        logger.info(f"Profiling API dataset: {dataset_name}")

        if not records:
            logger.warning(f"No records to profile for {dataset_name}")
            return {}

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(records)

        profile = {
            "dataset_name": dataset_name,
            "basic_stats": self._get_basic_stats(df),
            "field_profiles": self._profile_fields(df),
            "data_quality": self._assess_quality(df),
        }

        self.profiles[dataset_name] = profile
        return profile

    def _get_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic dataset statistics."""
        return {
            "total_records": len(df),
            "total_fields": len(df.columns),
            "fields": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 ** 2),
        }

    def _profile_fields(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Profile individual fields."""
        profiles = {}

        for column in df.columns:
            col_data = df[column]
            
            # Skip complex types (list, dict)
            if col_data.dtype == 'object':
                # Check if contains complex objects
                sample = col_data.dropna().iloc[0] if len(col_data.dropna()) > 0 else None
                if isinstance(sample, (list, dict)):
                    profiles[column] = {
                        "data_type": "complex_object",
                        "non_null_count": col_data.notna().sum(),
                        "null_count": col_data.isna().sum(),
                        "null_percentage": (col_data.isna().sum() / len(df)) * 100,
                    }
                    continue
            
            profiles[column] = {
                "data_type": str(col_data.dtype),
                "non_null_count": col_data.notna().sum(),
                "null_count": col_data.isna().sum(),
                "null_percentage": (col_data.isna().sum() / len(df)) * 100,
                "unique_values": col_data.nunique(),
                "unique_percentage": (col_data.nunique() / len(df)) * 100,
            }

            # Numeric field stats
            if col_data.dtype in ['int64', 'float64']:
                profiles[column].update({
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                })

            # Categorical field stats
            if col_data.dtype == 'object':
                top_values = col_data.value_counts().head(5).to_dict()
                profiles[column].update({
                    "top_values": top_values,
                })

        return profiles

    def _assess_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality."""
        total_cells = len(df) * len(df.columns)
        null_cells = df.isna().sum().sum()
        
        quality_score = ((total_cells - null_cells) / total_cells) * 100

        return {
            "total_cells": total_cells,
            "null_cells": null_cells,
            "filled_cells": total_cells - null_cells,
            "completeness_percentage": quality_score,
            "quality_score": min(100, max(0, quality_score)),
        }


def get_default_product_schema() -> Dict[str, Any]:
    """Get default schema for dummyjson products API."""
    return {
        "required_fields": [
            "id", "title", "price", "rating"
        ],
        "field_types": {
            "id": "integer",
            "title": "string",
            "description": "string",
            "price": "number",
            "discountPercentage": "number",
            "rating": "number",
            "stock": "integer",
            "brand": "string",
            "category": "string",
            "thumbnail": "string",
            "images": "list",
        },
    }


def get_default_product_constraints() -> Dict[str, Any]:
    """Get default constraints for product validation."""
    return {
        "ranges": {
            "price": (0.01, 10000),
            "rating": (0, 5),
            "discountPercentage": (0, 100),
            "stock": (0, 100000),
        },
        "string_length": {
            "title": (3, 500),
            "brand": (1, 100),
            "category": (1, 50),
        },
    }
