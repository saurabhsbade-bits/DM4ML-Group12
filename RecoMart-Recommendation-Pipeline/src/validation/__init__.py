"""
Data Validation & Preparation Module (Member 2)

Responsibilities:
- Validate data schema and correctness
- Check for missing values, duplicates, anomalies
- Generate data quality reports
- Clean and preprocess data
- Perform EDA and visualization
"""

import logging
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from .data_validator import DataValidator
from .data_profiler import DataProfiler
from .report_generator import DataQualityReportGenerator
from .validation_pipeline import DataValidationPipeline
from src.config.config import CSV_FILES
from src.preparation.data_cleaner import DataCleaner
from src.preparation.data_preprocessor import DataPreprocessor
from src.preparation.exploratory_analysis import ExploratoryAnalyzer
from src.utils.helper import ensure_directory, save_json

__all__ = [
    "DataValidator",
    "DataProfiler",
    "DataQualityReportGenerator",
    "DataValidationPipeline",
]

logger = logging.getLogger(__name__)


def _get_latest_raw_csv_paths(raw_input_path: Path) -> Dict[str, Path]:
    """Resolve the latest raw CSV files from the ingestion output directory."""
    dataset_paths: Dict[str, Path] = {}
    raw_csv_root = raw_input_path / "csv"

    for dataset_name in CSV_FILES:
        dataset_dir = raw_csv_root / dataset_name
        latest_file = None

        if dataset_dir.exists():
            candidate_files = list(dataset_dir.rglob("*.csv"))
            if candidate_files:
                latest_file = max(candidate_files, key=lambda path: path.stat().st_mtime)

        if latest_file is None:
            latest_file = CSV_FILES[dataset_name]
            logger.warning(
                f"Could not locate raw file for {dataset_name} under {dataset_dir}. "
                f"Falling back to configured dataset: {latest_file}"
            )

        dataset_paths[dataset_name] = latest_file

    return dataset_paths


def validate_data(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Run comprehensive data validation checks.
    
    Args:
        input_path: Path to raw data
        output_path: Path for validation reports
        
    Returns:
        Dict with validation results and quality metrics
    """
    logger.info(f"Starting data validation from {input_path}")
    ensure_directory(Path(output_path))
    dataset_paths = _get_latest_raw_csv_paths(Path(input_path))
    pipeline = DataValidationPipeline()
    results = pipeline.run_validation(datasets=dataset_paths)
    return results


def prepare_data(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Clean, preprocess, and prepare data for analysis.
    
    Args:
        input_path: Path to validated/raw data
        output_path: Path for prepared data
        
    Returns:
        Prepared DataFrame
    """
    logger.info(f"Starting data preparation from {input_path}")
    output_dir = Path(output_path)
    ensure_directory(output_dir)

    dataset_paths = _get_latest_raw_csv_paths(Path(input_path))
    cleaner = DataCleaner()
    preprocessor = DataPreprocessor()

    processed_frames = []
    summary: Dict[str, Any] = {}

    for dataset_name, file_path in dataset_paths.items():
        if not file_path.exists():
            logger.warning(f"Skipping missing file for {dataset_name}: {file_path}")
            continue

        cleaned_df, clean_report = cleaner.clean_csv(
            file_path=file_path,
            dataset_name=dataset_name,
            missing_strategy={},
        )

        if cleaned_df is None:
            logger.warning(f"Cleaning returned no dataframe for {dataset_name}")
            continue

        processed_df, preprocess_report = preprocessor.preprocess_dataset(
            df=cleaned_df,
            dataset_name=dataset_name,
        )

        output_file = output_dir / f"{dataset_name}_processed.csv"
        processed_df.to_csv(output_file, index=False)

        summary[dataset_name] = {
            "clean_report": clean_report,
            "preprocess_report": preprocess_report,
            "output_file": str(output_file),
        }

        processed_frames.append(processed_df)

    report_file = output_dir / "preparation_summary.json"
    save_json(summary, report_file)
    logger.info(f"Preparation summary saved to {report_file}")

    if processed_frames:
        combined_df = pd.concat(processed_frames, ignore_index=True, sort=False)
    else:
        combined_df = pd.DataFrame()

    return combined_df


def generate_eda_report(data: pd.DataFrame, output_path: str) -> None:
    """
    Generate EDA visualizations and statistics.
    
    Args:
        data: Prepared DataFrame
        output_path: Path to save EDA plots and summary
    """
    logger.info(f"Generating EDA report and saving to {output_path}")
    output_dir = Path(output_path)
    ensure_directory(output_dir)

    analyzer = ExploratoryAnalyzer(output_dir=output_dir)
    analyzer.analyze_dataset(data, "prepared_data")
    analyzer.plot_distributions(data, "prepared_data", save=True)
    analyzer.plot_heatmap(data, "prepared_data", save=True)

    if {"userId", "movieId", "rating"}.issubset(set(data.columns)):
        interaction_matrix = DataPreprocessor().create_interaction_matrix(
            df_ratings=data,
            user_col="userId",
            item_col="movieId",
            rating_col="rating",
        )
        analyzer.plot_sparsity(interaction_matrix, "prepared_data_sparsity", save=True)
