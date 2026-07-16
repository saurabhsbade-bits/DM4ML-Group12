# Dataset Documentation

## Project Title

**RecoMart Recommendation Pipeline – Dataset Documentation**

---

# 1. Introduction

The RecoMart Recommendation Pipeline integrates data from multiple heterogeneous sources to support recommendation system development. The project uses both static CSV datasets and dynamic REST API data to demonstrate the ingestion of structured data from different origins.

The selected datasets provide information about movies, user ratings, product catalogs, and user-generated tags, forming a comprehensive foundation for recommendation system development.

---

# 2. Dataset Overview

The project uses two primary data sources:

| Source | Type | Format | Purpose |
|----------|--------|---------|---------|
| MovieLens Dataset | Local Dataset | CSV | Movie recommendation data |
| DummyJSON Products API | External API | JSON | Product catalog information |

---

# 3. MovieLens Dataset

## Dataset Description

The MovieLens dataset is one of the most widely used benchmark datasets for recommendation system research. It contains historical movie ratings collected from real users.

The dataset is publicly available from the GroupLens Research Lab.

Dataset Link:

https://grouplens.org/datasets/movielens/

---

# 4. CSV Files Used

The project utilizes the following CSV files.

---

## 4.1 movies.csv

This file contains movie information.

### Purpose

Provides movie metadata for recommendation algorithms.

### Attributes

| Column | Description |
|----------|----------------|
| movieId | Unique movie identifier |
| title | Movie title |
| genres | Movie genres |

Example

| movieId | title | genres |
|-----------|------------------------------|----------------------|
| 1 | Toy Story (1995) | Adventure\|Animation\|Children |

---

## 4.2 ratings.csv

Contains user ratings assigned to movies.

### Purpose

Used for collaborative filtering and recommendation model training.

### Attributes

| Column | Description |
|----------|----------------|
| userId | Unique user ID |
| movieId | Movie ID |
| rating | Rating value |
| timestamp | Rating timestamp |

Example

| userId | movieId | rating |
|----------|-----------|---------|
| 1 | 1 | 4.0 |

---

## 4.3 links.csv

Maps MovieLens movie IDs to external movie databases.

### Purpose

Allows integration with external movie information.

### Attributes

| Column | Description |
|----------|----------------|
| movieId | MovieLens movie ID |
| imdbId | IMDb identifier |
| tmdbId | TMDB identifier |

---

## 4.4 tags.csv

Contains user-generated tags for movies.

### Purpose

Supports content-based recommendation systems.

### Attributes

| Column | Description |
|----------|----------------|
| userId | User ID |
| movieId | Movie ID |
| tag | User tag |
| timestamp | Tag timestamp |

---

# 5. Dataset Statistics

The ingested dataset contains the following records.

| Dataset | Records |
|-----------|------------:|
| movies.csv | 9,742 |
| ratings.csv | 100,836 |
| links.csv | 9,742 |
| tags.csv | 3,683 |

These statistics are automatically captured during metadata generation.

---

# 6. DummyJSON REST API

## API Description

The project retrieves product information from the DummyJSON REST API.

Endpoint:

```
https://dummyjson.com/products
```

The API returns product information in JSON format.

---

## Purpose

The API demonstrates real-time ingestion of external data sources alongside local datasets.

---

## Sample Attributes

| Attribute | Description |
|-------------|----------------|
| id | Product ID |
| title | Product Name |
| description | Product Description |
| category | Product Category |
| price | Product Price |
| rating | Product Rating |
| stock | Available Stock |
| brand | Product Brand |

---

## Sample JSON Response

```json
{
  "id": 1,
  "title": "Essence Mascara Lash Princess",
  "category": "beauty",
  "price": 9.99,
  "rating": 2.56,
  "stock": 99
}
```

---

# 7. Data Ingestion Summary

The pipeline automatically ingests data from both sources.

### CSV Workflow

```
movies.csv
ratings.csv
links.csv
tags.csv

↓

CSV Ingestion Module

↓

Raw Data Lake
```

---

### REST API Workflow

```
DummyJSON API

↓

API Ingestion Module

↓

products.json

↓

Raw Data Lake
```

---

# 8. Data Storage

CSV files are stored using the following hierarchy.

```
data/
└── raw/
    └── csv/
        └── dataset_name/
            └── YYYY/
                └── MM/
                    └── DD/
                        └── HHMMSS/
```

Example

```
data/raw/csv/ratings/2026/07/16/225641/ratings.csv
```

REST API responses are stored as:

```
data/raw/api/products/2026/07/16/225642/products.json
```

---

# 9. Metadata Generated

For every ingested dataset, the pipeline records:

- Dataset name
- Source type
- Source file
- Destination path
- Number of records
- File size
- Status
- Ingestion timestamp

This metadata enables auditing, monitoring, and data lineage tracking.

---

# 10. Why These Datasets Were Selected

The MovieLens dataset was selected because it is an industry-standard benchmark for recommendation systems and contains rich user–movie interaction data.

The DummyJSON API was selected because it provides publicly accessible product information in JSON format, allowing demonstration of REST API ingestion techniques.

Using both sources demonstrates the pipeline's capability to integrate heterogeneous data formats within a single ingestion framework.

---

# 11. Conclusion

The combination of structured CSV datasets and REST API data provides a realistic scenario for building modern data engineering pipelines.

The implemented ingestion framework successfully collects, stores, logs, and documents these datasets, establishing a robust foundation for future preprocessing, feature engineering, and recommendation model development.
