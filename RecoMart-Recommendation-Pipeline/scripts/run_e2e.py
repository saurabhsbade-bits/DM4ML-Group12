"""Run end-to-end pipeline locally.

This script executes: ingest -> validate -> prepare -> feature engineering -> train
It is intended for quick local verification and CI smoke tests.
"""
from pathlib import Path

from src.ingestion import ingest_data
from src.validation import validate_data, prepare_data
from src.features import engineer_features
from src.models import train_model


def main():
    base = Path(__file__).resolve().parent.parent
    raw_dir = base / 'data' / 'raw'
    processed_dir = base / 'data' / 'processed'
    features_dir = base / 'data' / 'features'
    models_dir = base / 'models'

    print('Running ingest_data...')
    ingest_data(output_path=str(raw_dir))
    print('Running validate_data...')
    validate_data(input_path=str(raw_dir), output_path=str(processed_dir))
    print('Running prepare_data...')
    prepare_data(input_path=str(raw_dir), output_path=str(processed_dir))
    print('Running engineer_features...')
    feats = engineer_features(input_path=str(processed_dir), output_path=str(features_dir))
    print('Features generated:', feats.shape)
    print('Running train_model...')
    res = train_model(features_path=str(features_dir), output_path=str(models_dir))
    print('Train result:', res)


if __name__ == '__main__':
    main()
