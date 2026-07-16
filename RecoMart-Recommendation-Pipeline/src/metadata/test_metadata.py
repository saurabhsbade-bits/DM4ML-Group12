from pathlib import Path

from src.metadata.metadata_generator import MetadataGenerator

metadata = MetadataGenerator()

metadata.add_csv_metadata(
    dataset_name="ratings",
    source_file=Path("dataset/ratings.csv"),
    destination_file=Path("dataset/ratings.csv"),
)

metadata.save()