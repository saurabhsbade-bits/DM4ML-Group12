"""
Data Profiler Module

Generates comprehensive statistical profiles of datasets including
distributions, cardinality, patterns, and quality metrics.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from src.utils.logger import logger


class DataProfiler:
    """
    Generates detailed statistical profiles of datasets.
    """

    def __init__(self):
        """Initialize profiler with empty profiles."""
        self.profiles = {}

    def profile_dataset(
        self,
        file_path: Path,
        dataset_name: str,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive profile for a dataset.

        Args:
            file_path: Path to CSV file
            dataset_name: Name of dataset for reporting

        Returns:
            Dictionary with statistical profile
        """

        logger.info(f"Profiling dataset: {dataset_name}")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to profile {dataset_name}: {e}")
            return {"dataset": dataset_name, "status": "FAILED", "error": str(e)}

        profile = {
            "dataset": dataset_name,
            "file_path": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "basic_info": self._basic_info(df),
            "column_profiles": self._profile_columns(df),
            "data_quality_metrics": self._quality_metrics(df),
        }

        self.profiles[dataset_name] = profile
        logger.info(f"Profile generated for {dataset_name}")

        return profile

    def _basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract basic dataset information."""
        return {
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": round(
                (df.duplicated().sum() / len(df)) * 100, 2
            ),
        }

    def _profile_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Profile individual columns."""
        profiles = {}

        for column in df.columns:
            col_profile = {
                "name": column,
                "data_type": str(df[column].dtype),
                "non_null_count": int(df[column].count()),
                "null_count": int(df[column].isna().sum()),
                "null_percentage": round(
                    (df[column].isna().sum() / len(df)) * 100, 2
                ),
                "unique_values": int(df[column].nunique()),
                "cardinality": round(
                    (df[column].nunique() / len(df)) * 100, 2
                ),  # %
            }

            # Numeric columns
            if pd.api.types.is_numeric_dtype(df[column]):
                col_profile.update(
                    {
                        "min": float(df[column].min()),
                        "max": float(df[column].max()),
                        "mean": float(df[column].mean()),
                        "median": float(df[column].median()),
                        "std_dev": float(df[column].std()),
                        "q25": float(df[column].quantile(0.25)),
                        "q75": float(df[column].quantile(0.75)),
                    }
                )

            # String columns
            elif pd.api.types.is_string_dtype(df[column]):
                col_profile.update(
                    {
                        "min_length": int(df[column].astype(str).str.len().min()),
                        "max_length": int(df[column].astype(str).str.len().max()),
                        "avg_length": round(
                            df[column].astype(str).str.len().mean(), 2
                        ),
                        "top_values": df[column]
                        .value_counts()
                        .head(5)
                        .to_dict(),
                    }
                )

            profiles[column] = col_profile

        return profiles

    def _quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isna().sum().sum()

        completeness = round(((total_cells - missing_cells) / total_cells) * 100, 2)
        validity = 100  # Adjust based on constraints validation

        return {
            "completeness_percentage": completeness,
            "validity_percentage": validity,
            "total_cells": int(total_cells),
            "missing_cells": int(missing_cells),
            "duplicate_rows_count": int(df.duplicated().sum()),
            "overall_quality_score": round((completeness + validity) / 2, 2),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all profiles."""
        if not self.profiles:
            return {"total_datasets": 0, "average_quality_score": 0}

        quality_scores = [
            profile["data_quality_metrics"]["overall_quality_score"]
            for profile in self.profiles.values()
        ]

        return {
            "total_datasets": len(self.profiles),
            "average_quality_score": round(sum(quality_scores) / len(quality_scores), 2),
            "profiles": self.profiles,
        }
