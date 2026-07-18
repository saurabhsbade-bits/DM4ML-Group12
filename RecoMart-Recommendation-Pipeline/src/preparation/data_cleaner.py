"""
Data Cleaning Module

Handles missing values, data type conversions, and outlier detection
for recommendation pipeline datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List, Any
from src.utils.logger import logger


class DataCleaner:
    """
    Performs data cleaning operations including missing value handling
    and outlier detection.
    """

    def __init__(self):
        """Initialize data cleaner."""
        self.missing_value_report = {}
        self.cleaned_datasets = {}

    def clean_csv(
        self,
        file_path: Path,
        dataset_name: str,
        missing_strategy: Dict[str, str] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean a CSV dataset by handling missing values and data issues.

        Args:
            file_path: Path to CSV file
            dataset_name: Name of dataset
            missing_strategy: Strategy for each column
                {"column": "drop|mean|median|forward_fill|zero"}

        Returns:
            Tuple of (cleaned DataFrame, cleaning report)
        """

        logger.info(f"Cleaning dataset: {dataset_name}")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None, {"error": str(e)}

        original_shape = df.shape
        report = {
            "dataset": dataset_name,
            "original_rows": original_shape[0],
            "original_columns": original_shape[1],
            "operations": [],
        }

        # Default strategy
        if missing_strategy is None:
            missing_strategy = {}

        # Handle missing values
        df, missing_report = self._handle_missing_values(
            df, dataset_name, missing_strategy
        )
        report["operations"].append(missing_report)

        # Handle duplicates
        df, duplicate_report = self._handle_duplicates(df, dataset_name)
        report["operations"].append(duplicate_report)

        # Handle data types
        df, dtype_report = self._fix_data_types(df, dataset_name)
        report["operations"].append(dtype_report)

        report["final_rows"] = df.shape[0]
        report["final_columns"] = df.shape[1]
        report["rows_dropped"] = original_shape[0] - df.shape[0]

        logger.info(
            f"Cleaning completed for {dataset_name}: "
            f"{report['rows_dropped']} rows dropped"
        )

        self.cleaned_datasets[dataset_name] = df
        self.missing_value_report[dataset_name] = report

        return df, report

    def _handle_missing_values(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        strategy: Dict[str, str],
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Handle missing values according to strategy."""
        report = {
            "operation": "Missing Value Handling",
            "missing_columns": {},
            "rows_dropped": 0,
        }

        for column in df.columns:
            null_count = df[column].isna().sum()

            if null_count == 0:
                continue

            col_strategy = strategy.get(column, "drop")

            if col_strategy == "drop":
                initial_rows = len(df)
                df = df.dropna(subset=[column])
                dropped = initial_rows - len(df)
                report["rows_dropped"] += dropped
                report["missing_columns"][column] = {
                    "strategy": "drop",
                    "rows_dropped": dropped,
                }

            elif col_strategy == "mean" and pd.api.types.is_numeric_dtype(df[column]):
                fill_value = df[column].mean()
                df[column].fillna(fill_value, inplace=True)
                report["missing_columns"][column] = {
                    "strategy": "mean",
                    "fill_value": float(fill_value),
                }

            elif col_strategy == "median" and pd.api.types.is_numeric_dtype(df[column]):
                fill_value = df[column].median()
                df[column].fillna(fill_value, inplace=True)
                report["missing_columns"][column] = {
                    "strategy": "median",
                    "fill_value": float(fill_value),
                }

            elif col_strategy == "zero":
                df[column].fillna(0, inplace=True)
                report["missing_columns"][column] = {
                    "strategy": "zero",
                }

            elif col_strategy == "forward_fill":
                df[column].fillna(method="ffill", inplace=True)
                report["missing_columns"][column] = {
                    "strategy": "forward_fill",
                }

            elif col_strategy == "mode" and not pd.api.types.is_numeric_dtype(df[column]):
                fill_value = df[column].mode()[0] if len(df[column].mode()) > 0 else "Unknown"
                df[column].fillna(fill_value, inplace=True)
                report["missing_columns"][column] = {
                    "strategy": "mode",
                    "fill_value": str(fill_value),
                }

        return df, report

    def _handle_duplicates(
        self,
        df: pd.DataFrame,
        dataset_name: str,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Remove duplicate rows."""
        report = {
            "operation": "Duplicate Handling",
            "duplicates_found": int(df.duplicated().sum()),
            "duplicates_removed": 0,
        }

        initial_rows = len(df)
        df = df.drop_duplicates()
        report["duplicates_removed"] = initial_rows - len(df)

        return df, report

    def _fix_data_types(
        self,
        df: pd.DataFrame,
        dataset_name: str,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Infer and fix data types."""
        report = {
            "operation": "Data Type Fixing",
            "type_conversions": {},
        }

        # Try to infer better types
        for column in df.columns:
            original_type = str(df[column].dtype)

            # Try converting float columns with integer values to int
            if df[column].dtype == "float64":
                if df[column].isna().sum() == 0:
                    # No nulls, safe to convert
                    if all(df[column] == df[column].astype(int)):
                        df[column] = df[column].astype("int64")
                        report["type_conversions"][column] = {
                            "from": original_type,
                            "to": "int64",
                        }

            # Try converting to category for low-cardinality strings
            elif df[column].dtype == "object":
                unique_count = df[column].nunique()
                total_count = len(df)
                cardinality = (unique_count / total_count) * 100

                if cardinality < 5:  # Less than 5% unique values
                    df[column] = df[column].astype("category")
                    report["type_conversions"][column] = {
                        "from": original_type,
                        "to": "category",
                        "cardinality_pct": round(cardinality, 2),
                    }

        return df, report

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of cleaning operations."""
        return {
            "total_datasets_cleaned": len(self.cleaned_datasets),
            "cleaning_reports": self.missing_value_report,
        }

    def save_cleaned_data(
        self,
        output_dir: Path = None,
    ) -> Dict[str, Path]:
        """Save cleaned datasets to CSV."""
        if output_dir is None:
            output_dir = Path(__file__).resolve().parents[2] / "data" / "processed"

        output_dir.mkdir(parents=True, exist_ok=True)
        saved_files = {}

        for dataset_name, df in self.cleaned_datasets.items():
            output_file = output_dir / f"{dataset_name}_cleaned.csv"
            df.to_csv(output_file, index=False)
            saved_files[dataset_name] = output_file
            logger.info(f"Saved cleaned data: {output_file}")

        return saved_files
