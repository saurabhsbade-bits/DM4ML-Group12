"""
API Data Preparation Module

Cleans and preprocesses API-ingested JSON data.
Handles schema normalization, type conversion, and feature extraction.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple
import json

from src.utils.logger import logger


class APIDataCleaner:
    """
    Cleans API-ingested JSON data.
    
    Operations:
    - Flatten nested JSON structures
    - Handle missing values
    - Type conversion
    - Remove duplicates
    - Text normalization
    """

    def __init__(self):
        """Initialize API data cleaner."""
        self.cleaned_datasets = {}

    def clean_api_data(
        self,
        records: List[Dict],
        dataset_name: str,
        flatten_nested: bool = True,
        missing_strategy: str = "drop",
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean API records and convert to DataFrame.

        Args:
            records: List of API records (dicts)
            dataset_name: Name of dataset
            flatten_nested: Whether to flatten nested structures
            missing_strategy: How to handle missing values (drop, fill_na)

        Returns:
            Tuple of (cleaned_df, report)
        """
        logger.info(f"Cleaning API data: {dataset_name}")

        if not records:
            logger.warning(f"No records to clean for {dataset_name}")
            return pd.DataFrame(), {"error": "No records"}

        # Convert to DataFrame
        df = pd.DataFrame(records)
        initial_rows = len(df)

        report = {
            "dataset_name": dataset_name,
            "initial_rows": initial_rows,
            "rows_dropped": 0,
            "operations": [],
        }

        # Flatten nested structures if needed
        if flatten_nested:
            df = self._flatten_nested(df)
            report["operations"].append("Nested structures flattened")

        # Handle missing values
        if missing_strategy == "drop":
            before_drop = len(df)
            df = df.dropna()
            dropped = before_drop - len(df)
            report["rows_dropped"] += dropped
            report["operations"].append(f"Dropped {dropped} rows with missing values")

        elif missing_strategy == "fill_zero":
            numeric_columns = df.select_dtypes(include=['number']).columns
            df[numeric_columns] = df[numeric_columns].fillna(0)
            report["operations"].append("Filled numeric nulls with 0")

        elif missing_strategy == "fill_forward":
            df = df.fillna(method='ffill')
            report["operations"].append("Forward-filled missing values")

        # Remove duplicates
        before_dedup = len(df)
        df = df.drop_duplicates()
        dedup_dropped = before_dedup - len(df)
        if dedup_dropped > 0:
            report["rows_dropped"] += dedup_dropped
            report["operations"].append(f"Removed {dedup_dropped} duplicate rows")

        # Text normalization
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
            report["operations"].append(f"Normalized text in {col}")

        # Fix data types
        df = self._fix_data_types(df)
        report["operations"].append("Data types optimized")

        report["final_rows"] = len(df)
        report["columns"] = list(df.columns)

        self.cleaned_datasets[dataset_name] = df
        logger.info(
            f"Cleaning completed: {initial_rows} → {len(df)} rows "
            f"({report['rows_dropped']} removed)"
        )

        return df, report

    def _flatten_nested(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flatten nested JSON structures."""
        flattened_data = []

        for idx, row in df.iterrows():
            flat_record = {}
            self._flatten_record(row.to_dict(), flat_record, prefix="")
            flattened_data.append(flat_record)

        return pd.DataFrame(flattened_data)

    def _flatten_record(
        self,
        record: Dict,
        flat_record: Dict,
        prefix: str,
    ) -> None:
        """Recursively flatten nested record."""
        for key, value in record.items():
            new_key = f"{prefix}_{key}" if prefix else key

            if isinstance(value, dict):
                self._flatten_record(value, flat_record, new_key)
            elif isinstance(value, list):
                # Convert list to string representation
                flat_record[new_key] = str(value) if value else None
            else:
                flat_record[new_key] = value

    def _fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types."""
        for col in df.columns:
            # Try to convert to numeric
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    # Keep as object if conversion fails
                    pass

            # Convert integer columns with no nulls
            if df[col].dtype == 'float64':
                if df[col].notna().all() and (df[col] % 1 == 0).all():
                    df[col] = df[col].astype('int64')

        return df

    def save_cleaned_data(self, output_dir: Path = None) -> Dict[str, Path]:
        """Save cleaned datasets to CSV."""
        if output_dir is None:
            output_dir = Path.cwd() / "data" / "processed"

        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}
        for dataset_name, df in self.cleaned_datasets.items():
            output_file = output_dir / f"api_{dataset_name}_cleaned.csv"
            df.to_csv(output_file, index=False)
            saved_files[dataset_name] = output_file
            logger.info(f"Saved cleaned API data: {output_file}")

        return saved_files


class APIDataPreprocessor:
    """
    Preprocesses API data for modeling.
    
    Operations:
    - Feature extraction from JSON
    - Categorical encoding
    - Numerical normalization
    - Feature scaling
    """

    def __init__(self):
        """Initialize API data preprocessor."""
        self.processed_datasets = {}
        self.encoders = {}
        self.scalers = {}

    def preprocess_api_data(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        numeric_columns: List[str] = None,
        categorical_columns: List[str] = None,
        normalize_method: str = "minmax",
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Preprocess API data.

        Args:
            df: Input DataFrame
            dataset_name: Dataset name
            numeric_columns: Columns to normalize
            categorical_columns: Columns to encode
            normalize_method: minmax or standard

        Returns:
            Tuple of (processed_df, report)
        """
        logger.info(f"Preprocessing API data: {dataset_name}")

        df_processed = df.copy()
        report = {
            "dataset_name": dataset_name,
            "initial_columns": len(df),
            "operations": [],
        }

        # Auto-detect numeric columns if not provided
        if numeric_columns is None:
            numeric_columns = df_processed.select_dtypes(
                include=['int64', 'float64']
            ).columns.tolist()

        # Auto-detect categorical columns if not provided
        if categorical_columns is None:
            categorical_columns = df_processed.select_dtypes(
                include=['object']
            ).columns.tolist()

        # Normalize numeric columns
        for col in numeric_columns:
            if col in df_processed.columns:
                df_processed[col] = self._normalize_column(
                    df_processed,
                    col,
                    normalize_method,
                    dataset_name
                )
                report["operations"].append(f"Normalized {col} ({normalize_method})")

        # Encode categorical columns
        for col in categorical_columns:
            if col in df_processed.columns:
                df_processed[col] = self._encode_column(
                    df_processed,
                    col,
                    dataset_name
                )
                report["operations"].append(f"Encoded {col} (label)")

        report["final_columns"] = len(df_processed)
        self.processed_datasets[dataset_name] = df_processed

        logger.info(f"Preprocessing completed for {dataset_name}")
        return df_processed, report

    def _normalize_column(
        self,
        df: pd.DataFrame,
        column: str,
        method: str,
        dataset_name: str,
    ) -> pd.Series:
        """Normalize numerical column."""
        if method == "minmax":
            min_val = df[column].min()
            max_val = df[column].max()
            if max_val > min_val:
                return (df[column] - min_val) / (max_val - min_val)
            else:
                return df[column]

        elif method == "standard":
            mean = df[column].mean()
            std = df[column].std()
            if std > 0:
                return (df[column] - mean) / std
            else:
                return df[column]

        return df[column]

    def _encode_column(
        self,
        df: pd.DataFrame,
        column: str,
        dataset_name: str,
    ) -> pd.Series:
        """Encode categorical column."""
        encoder_key = f"{dataset_name}_{column}"

        # Create mapping from unique values
        unique_values = df[column].unique()
        mapping = {val: idx for idx, val in enumerate(unique_values)}
        self.encoders[encoder_key] = mapping

        return df[column].map(mapping)

    def extract_features(
        self,
        df: pd.DataFrame,
        dataset_name: str,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Extract useful features from API data.

        Args:
            df: Input DataFrame
            dataset_name: Dataset name

        Returns:
            Tuple of (df_with_features, report)
        """
        logger.info(f"Extracting features from {dataset_name}")

        df_features = df.copy()
        report = {
            "dataset_name": dataset_name,
            "new_features": [],
        }

        # Example features for product data
        if "price" in df_features.columns and "discountPercentage" in df_features.columns:
            df_features["final_price"] = (
                df_features["price"] * (1 - df_features["discountPercentage"] / 100)
            )
            report["new_features"].append("final_price")

        if "rating" in df_features.columns and "stock" in df_features.columns:
            # Rating quality score weighted by stock
            df_features["rating_quality"] = (
                df_features["rating"] * (df_features["stock"].clip(upper=100) / 100)
            )
            report["new_features"].append("rating_quality")

        if "title" in df_features.columns:
            # Only calculate length if title is string
            if df_features["title"].dtype == "object":
                df_features["title_length"] = df_features["title"].str.len()
                report["new_features"].append("title_length")

        logger.info(f"Extracted {len(report['new_features'])} features")
        return df_features, report

    def save_processed_data(self, output_dir: Path = None) -> Dict[str, Path]:
        """Save processed datasets to CSV."""
        if output_dir is None:
            output_dir = Path.cwd() / "data" / "processed"

        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}
        for dataset_name, df in self.processed_datasets.items():
            output_file = output_dir / f"api_{dataset_name}_processed.csv"
            df.to_csv(output_file, index=False)
            saved_files[dataset_name] = output_file
            logger.info(f"Saved processed API data: {output_file}")

        return saved_files


def normalize_product_for_recommendation(
    product_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize product data to work with recommendation system.
    
    Converts product data to item features for hybrid recommendations.
    """
    df_normalized = product_df.copy()

    # Ensure key columns exist
    if "id" in df_normalized.columns:
        df_normalized = df_normalized.rename(columns={"id": "itemId"})

    if "title" in df_normalized.columns:
        df_normalized = df_normalized.rename(columns={"title": "itemName"})

    if "price" in df_normalized.columns:
        df_normalized = df_normalized.rename(columns={"price": "itemPrice"})

    if "category" in df_normalized.columns:
        df_normalized = df_normalized.rename(columns={"category": "itemCategory"})

    return df_normalized
