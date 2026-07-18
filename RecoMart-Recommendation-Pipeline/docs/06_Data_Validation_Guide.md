# Data Profiling & Validation Guide

## Overview

A comprehensive data validation and profiling framework has been implemented to ensure data quality, completeness, and consistency before processing in the recommendation pipeline.

## Components

### 1. **DataValidator** (`src/validation/data_validator.py`)

Performs comprehensive validation checks on datasets:

#### Validation Checks

- **Schema Validation**: Verifies all expected columns exist with correct names
- **Missing Values Detection**: Identifies null/NA values by column
- **Duplicate Detection**: Finds duplicate rows within datasets
- **Data Type Validation**: Ensures columns match expected data types
- **Business Logic Constraints**: Validates domain-specific rules (ranges, formats)

#### Supported Constraint Types

```python
constraints = {
    "rating": {
        "type": "range",
        "min": 0.5,
        "max": 5.0,
    },
    "userId": {
        "type": "range",
        "min": 1,
    },
    "genre": {
        "type": "enum",
        "allowed_values": ["Action", "Comedy", "Drama"],
    },
    "movie_id": {
        "type": "unique",
        "unique": True,
    }
}
```

#### Usage Example

```python
from src.validation.data_validator import DataValidator
from pathlib import Path

validator = DataValidator()

schema = {
    "movieId": "int",
    "title": "str",
    "genres": "str",
}

result = validator.validate_csv(
    file_path=Path("dataset/movies.csv"),
    dataset_name="movies",
    schema=schema,
    constraints=None
)

print(result["status"])  # "PASS" or "FAIL"
print(result["issues"])  # List of detected issues
```

### 2. **DataProfiler** (`src/validation/data_profiler.py`)

Generates detailed statistical profiles of datasets:

#### Profile Metrics

**Basic Information**
- Total rows, columns, memory usage
- Duplicate row count and percentage

**Column Statistics**
- Data type, non-null count, null percentage
- Cardinality (% unique values)
- For numeric columns: min, max, mean, median, std dev, quartiles
- For string columns: length statistics, top values

**Data Quality Metrics**
- Completeness: % of non-null cells
- Validity: % of valid records
- Overall Quality Score: Combined metric (0-100)

#### Usage Example

```python
from src.validation.data_profiler import DataProfiler
from pathlib import Path

profiler = DataProfiler()

profile = profiler.profile_dataset(
    file_path=Path("dataset/ratings.csv"),
    dataset_name="ratings"
)

print(f"Quality Score: {profile['data_quality_metrics']['overall_quality_score']}")
print(f"Completeness: {profile['data_quality_metrics']['completeness_percentage']}%")
```

### 3. **DataQualityReportGenerator** (`src/validation/report_generator.py`)

Generates comprehensive PDF reports with:

- Executive summary with key metrics
- Validation results for each dataset
- Data profiling statistics
- Quality metrics by dataset
- Issues and recommendations

#### Usage Example

```python
from src.validation.report_generator import DataQualityReportGenerator

generator = DataQualityReportGenerator(output_dir=Path("data/reports"))

report_path = generator.generate_report(
    validation_results=validation_summary,
    profiling_results=profiling_summary,
    report_name="DataQualityReport.pdf"
)
```

### 4. **DataValidationPipeline** (`src/validation/validation_pipeline.py`)

Orchestrates the complete validation workflow:

1. Loads datasets
2. Runs validation checks
3. Generates statistical profiles
4. Creates comprehensive PDF report
5. Saves results to JSON

#### Usage Example

```python
from src.validation.validation_pipeline import DataValidationPipeline

pipeline = DataValidationPipeline()

results = pipeline.run_validation(
    datasets={"movies": Path("dataset/movies.csv"), ...},
    custom_constraints={...}
)

pipeline.print_summary(results)
```

## Validation Results Summary

### Current Validation Status

| Dataset | Status | Quality Score | Issues |
|---------|--------|---------------|--------|
| movies | ✅ PASS | 100.00% | 0 |
| ratings | ✅ PASS | 100.00% | 0 |
| links | ⚠️ FAIL | 99.98% | 2 |
| tags | ✅ PASS | 100.00% | 0 |

### Issues Detected

#### Dataset: links
1. **Missing Values** (MEDIUM severity)
   - Column: `tmdbId`
   - Count: 8 null values
   - Percentage: 0.08% of 9,742 rows

2. **Data Type Mismatch** (MEDIUM severity)
   - Column: `tmdbId`
   - Expected: `int`
   - Actual: `float64`
   - Reason: Null values forced column to float type

### Quality Metrics

**Overall Average Quality Score**: 100.00%
- Completeness: > 99.97% across all datasets
- No duplicate rows detected
- Schema matches expected structure

## Data Characteristics

### Movies Dataset (9,742 rows)
- Columns: movieId (int), title (str), genres (str)
- No missing values, no duplicates
- Quality: 100%

### Ratings Dataset (100,836 rows)
- Columns: userId (int), movieId (int), rating (float), timestamp (int)
- Rating range: 0.5 - 5.0 (validated)
- No missing values, no duplicates
- Quality: 100%

### Links Dataset (9,742 rows)
- Columns: movieId (int), imdbId (int), tmdbId (int)
- 8 missing tmdbId values (0.08%)
- tmdbId stored as float due to nulls
- Quality: 99.98%

### Tags Dataset (3,683 rows)
- Columns: userId (int), movieId (int), tag (str), timestamp (int)
- No missing values, no duplicates
- Quality: 100%

## Generated Reports

### PDF Report
- **Location**: `data/reports/DataQualityReport_[timestamp].pdf`
- **Contents**: 
  - Executive summary
  - Detailed validation results per dataset
  - Statistical profiles and distributions
  - Data quality metrics
  - Issues and severity levels

### JSON Results
- **Location**: `data/reports/validation_results.json`
- **Contents**:
  - Raw validation results
  - Profiling statistics
  - Issue details
  - Timestamps for audit trail

## Running Validation

### Quick Start

```bash
cd RecoMart-Recommendation-Pipeline

# Run full validation pipeline
python -m src.validation.test_validation

# Or import and use directly
python -c "
from src.validation.validation_pipeline import DataValidationPipeline
pipeline = DataValidationPipeline()
results = pipeline.run_validation()
pipeline.print_summary(results)
"
```

### Custom Validation

```python
from src.validation.validation_pipeline import DataValidationPipeline
from pathlib import Path

pipeline = DataValidationPipeline()

custom_constraints = {
    "ratings": {
        "rating": {"type": "range", "min": 0.5, "max": 5.0},
        "userId": {"type": "range", "min": 1},
    }
}

results = pipeline.run_validation(
    custom_constraints=custom_constraints
)
```

## Recommendations

### For links.csv
1. **Handle Missing tmdbId Values**
   - Option 1: Drop rows with missing tmdbId
   - Option 2: Fill with default value (-1)
   - Option 3: Leave as-is if external API can provide replacements

2. **Fix Data Type**
   - Convert tmdbId to int after handling nulls
   - Use nullable int type or default value strategy

### For Production Deployment
1. Schedule validation runs post-ingestion
2. Set quality score thresholds for alerts
3. Archive reports for compliance
4. Monitor quality trends over time

## Dependencies

- `pandas`: Data analysis and validation
- `numpy`: Numerical operations
- `reportlab`: PDF report generation

Install with:
```bash
pip install pandas numpy reportlab
```

## Integration with Pipeline

The validation framework integrates with the main ingestion pipeline:

```python
# In main.py
from src.validation.validation_pipeline import DataValidationPipeline

# After ingestion
pipeline = DataValidationPipeline()
validation_results = pipeline.run_validation()

# Log validation status
if validation_results["validation"]["status"] == "PASS":
    logger.info("All datasets passed validation")
else:
    logger.warning("Some datasets failed validation - review report")
```

## File Structure

```
src/validation/
├── __init__.py                    # Module initialization
├── data_validator.py              # Core validation logic
├── data_profiler.py               # Statistical profiling
├── report_generator.py            # PDF/HTML report generation
├── validation_pipeline.py         # Orchestration pipeline
└── test_validation.py             # Test/demo script

data/reports/
├── DataQualityReport_[timestamp].pdf   # PDF report
├── validation_results.json              # Detailed JSON results
└── README.md                            # This file
```

## Next Steps

1. ✅ Implement validation framework
2. ✅ Generate baseline quality report
3. **Review issues** and decide on remediation
4. Integrate validation into ingestion pipeline
5. Set up automated quality monitoring
6. Configure alerting for quality degradation
