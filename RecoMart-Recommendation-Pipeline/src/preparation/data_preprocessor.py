"""
Data Preprocessing Module

Handles categorical encoding, numerical normalization, and feature engineering
for recommendation pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List, Any
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
from src.utils.logger import logger


class DataPreprocessor:
    """
    Performs data preprocessing including encoding and normalization.
    """

    def __init__(self):
        """Initialize preprocessor with encoders and scalers."""
        self.label_encoders = {}
        self.scalers = {}
        self.encoding_mappings = {}
        self.processed_datasets = {}

    def preprocess_dataset(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        categorical_columns: List[str] = None,
        numerical_columns: List[str] = None,
        normalize_method: str = "minmax",
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Preprocess dataset with encoding and normalization.

        Args:
            df: Input DataFrame
            dataset_name: Name of dataset
            categorical_columns: Columns to encode
            numerical_columns: Columns to normalize
            normalize_method: "minmax" or "standard"

        Returns:
            Tuple of (preprocessed DataFrame, preprocessing report)
        """

        logger.info(f"Preprocessing dataset: {dataset_name}")

        df_processed = df.copy()
        report = {
            "dataset": dataset_name,
            "original_columns": len(df.columns),
            "encoding_operations": {},
            "normalization_operations": {},
        }

        # Auto-detect categorical columns if not specified
        if categorical_columns is None:
            categorical_columns = df_processed.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()

        # Auto-detect numerical columns if not specified
        if numerical_columns is None:
            numerical_columns = df_processed.select_dtypes(
                include=["int64", "float64"]
            ).columns.tolist()

        # Encode categorical variables
        for col in categorical_columns:
            if col in df_processed.columns:
                df_processed, encoding_report = self._encode_column(
                    df_processed, col, dataset_name
                )
                report["encoding_operations"][col] = encoding_report

        # Normalize numerical variables
        for col in numerical_columns:
            if col in df_processed.columns:
                df_processed, normalization_report = self._normalize_column(
                    df_processed, col, normalize_method, dataset_name
                )
                report["normalization_operations"][col] = normalization_report

        report["processed_columns"] = len(df_processed.columns)
        self.processed_datasets[dataset_name] = df_processed

        logger.info(f"Preprocessing completed for {dataset_name}")

        return df_processed, report

    def _encode_column(
        self,
        df: pd.DataFrame,
        column: str,
        dataset_name: str,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Encode categorical column using label encoding."""
        report = {
            "method": "label_encoding",
            "original_type": str(df[column].dtype),
            "unique_values": int(df[column].nunique()),
        }

        # Create or use existing encoder
        encoder_key = f"{dataset_name}_{column}"

        if encoder_key not in self.label_encoders:
            encoder = LabelEncoder()
            df[column] = encoder.fit_transform(df[column].astype(str))
            self.label_encoders[encoder_key] = encoder

            # Store mapping
            self.encoding_mappings[encoder_key] = dict(
                zip(encoder.classes_, encoder.transform(encoder.classes_))
            )
        else:
            encoder = self.label_encoders[encoder_key]
            df[column] = encoder.transform(df[column].astype(str))

        report["mapping"] = self.encoding_mappings[encoder_key]
        report["new_type"] = str(df[column].dtype)

        return df, report

    def _normalize_column(
        self,
        df: pd.DataFrame,
        column: str,
        method: str,
        dataset_name: str,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Normalize numerical column."""
        report = {
            "method": method,
            "original_min": float(df[column].min()),
            "original_max": float(df[column].max()),
            "original_mean": float(df[column].mean()),
            "original_std": float(df[column].std()),
        }

        scaler_key = f"{dataset_name}_{column}"

        if scaler_key not in self.scalers:
            if method == "minmax":
                scaler = MinMaxScaler()
            else:  # standard
                scaler = StandardScaler()

            df[[column]] = scaler.fit_transform(df[[column]])
            self.scalers[scaler_key] = scaler
        else:
            scaler = self.scalers[scaler_key]
            df[[column]] = scaler.transform(df[[column]])

        report["normalized_min"] = float(df[column].min())
        report["normalized_max"] = float(df[column].max())
        report["normalized_mean"] = float(df[column].mean())
        report["normalized_std"] = float(df[column].std())

        return df, report

    def encode_one_hot(
        self,
        df: pd.DataFrame,
        column: str,
        dataset_name: str,
        drop_first: bool = True,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Apply one-hot encoding to categorical column.

        Args:
            df: Input DataFrame
            column: Column to encode
            dataset_name: Name of dataset
            drop_first: Whether to drop first category (avoid multicollinearity)

        Returns:
            Tuple of (encoded DataFrame, encoding report)
        """
        report = {
            "method": "one_hot_encoding",
            "original_column": column,
            "unique_values": int(df[column].nunique()),
        }

        # Apply one-hot encoding
        encoded = pd.get_dummies(df[column], prefix=column, drop_first=drop_first)

        # Replace original column with encoded columns
        df = df.drop(column, axis=1)
        df = pd.concat([df, encoded], axis=1)

        report["new_columns_created"] = list(encoded.columns)
        report["columns_added"] = len(encoded.columns)

        return df, report

    def create_interaction_matrix(
        self,
        df_ratings: pd.DataFrame,
        user_col: str = "userId",
        item_col: str = "movieId",
        rating_col: str = "rating",
    ) -> pd.DataFrame:
        """
        Create user-item interaction matrix from ratings data.

        Args:
            df_ratings: Ratings DataFrame
            user_col: User ID column
            item_col: Item ID column
            rating_col: Rating/interaction column

        Returns:
            User-item interaction matrix (pivot table)
        """
        logger.info("Creating user-item interaction matrix")

        interaction_matrix = df_ratings.pivot_table(
            index=user_col,
            columns=item_col,
            values=rating_col,
            fill_value=0,
        )

        logger.info(
            f"Interaction matrix shape: {interaction_matrix.shape} "
            f"(users x items)"
        )
        
        # Calculate sparsity
        total_cells = interaction_matrix.shape[0] * interaction_matrix.shape[1]
        filled_cells = (interaction_matrix != 0).sum().sum()
        sparsity_pct = (1 - filled_cells / total_cells) * 100
        logger.info(f"Matrix sparsity: {sparsity_pct:.2f}%")

        return interaction_matrix

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of preprocessing operations."""
        return {
            "total_datasets_processed": len(self.processed_datasets),
            "label_encoders": len(self.label_encoders),
            "scalers": len(self.scalers),
            "encoding_mappings": list(self.encoding_mappings.keys()),
        }

    def save_processed_data(
        self,
        output_dir: Path = None,
    ) -> Dict[str, Path]:
        """Save processed datasets to CSV."""
        if output_dir is None:
            output_dir = Path(__file__).resolve().parents[2] / "data" / "processed"

        output_dir.mkdir(parents=True, exist_ok=True)
        saved_files = {}

        for dataset_name, df in self.processed_datasets.items():
            output_file = output_dir / f"{dataset_name}_processed.csv"
            df.to_csv(output_file, index=False)
            saved_files[dataset_name] = output_file
            logger.info(f"Saved processed data: {output_file}")

        return saved_files
