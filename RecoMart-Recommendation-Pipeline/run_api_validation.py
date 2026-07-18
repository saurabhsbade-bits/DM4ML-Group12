from src.ingestion.api_ingestion import run_api_ingestion
from src.metadata.metadata_generator import MetadataGenerator
from src.validation.api_validator import APIValidator, APIDataProfiler, get_default_product_schema, get_default_product_constraints
from src.utils.helper import save_json
from pathlib import Path

if __name__ == '__main__':
    metadata = MetadataGenerator()
    run_api_ingestion(metadata)
    metadata.save()

    # Find latest products.json in API raw dir (search recursively)
    from src.config.config import API_RAW_DIR
    import os

    files = list(Path(API_RAW_DIR).rglob('products.json'))
    if not files:
        print('No API products.json found')
        raise SystemExit(1)

    latest = max(files, key=lambda p: p.stat().st_mtime)
    print('Found API file:', latest)

    validator = APIValidator()
    schema = get_default_product_schema()
    constraints = get_default_product_constraints()

    valid_records, report = validator.validate_json_file(Path(latest), schema, constraints)

    profiler = APIDataProfiler()
    profile = profiler.profile_api_data(valid_records, 'products')

    out_dir = Path(__file__).resolve().parents[1] / 'data' / 'reports'
    out_dir.mkdir(parents=True, exist_ok=True)
    save_json(report, out_dir / 'api_validation_report.json')
    save_json(profile, out_dir / 'api_profile.json')

    print('API validation complete. Valid records:', len(valid_records) if valid_records else 0)
    print('Reports saved to:', out_dir)
