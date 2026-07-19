"""
Data Ingestion Module (Member 1)

Responsibilities:
- Ingest CSV files from local filesystem
- Fetch data from REST APIs
- Implement error handling and retry logic
- Log all ingestion events
- Store raw data with timestamp partitioning
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

from src.metadata.metadata_generator import MetadataGenerator
from src.utils.helper import ensure_directory
from .csv_ingestion import run_csv_ingestion
from .api_ingestion import run_api_ingestion

logger = logging.getLogger(__name__)


def ingest_csv_data(source_path: str, output_path: str) -> Dict[str, Any]:
    """
    Ingest CSV files from source and store in raw data lake.
    
    Args:
        source_path: Source directory containing CSV files
        output_path: Output directory for raw data
        
    Returns:
        Dict with ingestion metadata and status
    """
    logger.info(f"Starting CSV ingestion from source_path={source_path}")
    output_dir = Path(output_path)
    ensure_directory(output_dir)

    metadata = MetadataGenerator()
    run_csv_ingestion(metadata)
    metadata.save()

    return {
        "status": "success",
        "source_path": source_path,
        "output_path": str(output_dir),
        "metadata_file": str(Path(__file__).resolve().parents[2] / "data" / "metadata" / "ingestion_metadata.json"),
    }


def ingest_rest_api_data(api_endpoints: List[str], output_path: str) -> Dict[str, Any]:
    """
    Ingest data from REST APIs.
    
    Args:
        api_endpoints: List of API endpoints to fetch from
        output_path: Output directory for raw data
        
    Returns:
        Dict with ingestion metadata and status
    """
    logger.info(f"Starting REST API ingestion from api_endpoints={api_endpoints}")
    output_dir = Path(output_path)
    ensure_directory(output_dir)

    metadata = MetadataGenerator()
    run_api_ingestion(metadata)
    metadata.save()

    return {
        "status": "success",
        "api_endpoints": api_endpoints,
        "output_path": str(output_dir),
        "metadata_file": str(Path(__file__).resolve().parents[2] / "data" / "metadata" / "ingestion_metadata.json"),
    }


def ingest_data(output_path: str) -> Dict[str, Any]:
    """
    Main ingestion orchestrator.
    
    Args:
        output_path: Output directory for raw data
        
    Returns:
        Dict with combined ingestion results
    """
    logger.info(f"Starting data ingestion pipeline with output_path={output_path}")
    output_dir = Path(output_path)
    ensure_directory(output_dir)

    metadata = MetadataGenerator()
    run_csv_ingestion(metadata)
    run_api_ingestion(metadata)
    metadata.save()

    return {
        "status": "success",
        "output_path": str(output_dir),
        "metadata_file": str(Path(__file__).resolve().parents[2] / "data" / "metadata" / "ingestion_metadata.json"),
        "ingested_sources": ["csv", "api"],
    }
