from src.utils.helper import *

print(current_timestamp())

print(
    csv_record_count(
        Path("dataset/ratings.csv")
    )
)

print(
    file_size(
        Path("dataset/ratings.csv")
    )
)