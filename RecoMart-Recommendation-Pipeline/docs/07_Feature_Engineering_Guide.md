# Feature Engineering & Feature Store Guide (Member 3)

## Overview

This module turns the validated MovieLens interaction data into a set of
versioned, documented features for the recommendation model (Member 4):
user features, item (movie) features, interaction features, and a set
of similarity/cross features. It also defines a relational SQL schema
for the transformed data and a lightweight custom feature store that
registers, versions and serves the engineered features.

Code: `src/features/`. Artifacts: `data/features/`, `feature_store/`.

## Why raw MovieLens tables, not `data/processed/*_processed.csv`

Member 2's preprocessing step (`src/preparation/data_preprocessor.py`)
auto-detects every numeric/categorical column and applies
`MinMaxScaler` / `LabelEncoder` to it — including primary keys
(`userId`, `movieId`), the rating `timestamp`, and the pipe-separated
`genres` string (collapsed into a single opaque label-encoded integer).
None of the fitted scalers/encoders are persisted, so this cannot be
inverted. That makes `data/processed` unsuitable as the base for
features that need to be interpretable, joinable, and versioned
(genre preference vectors, real recency in days, human-readable ids in
the feature store/SQL schema).

`engineer_features()` therefore reads the canonical raw tables
(`dataset/movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`, via
`src.config.config.CSV_FILES`) — which Member 2's own validation report
already confirms are clean (no missing values or duplicates) — while
still checking `input_path` (Member 2's `data/processed`) for
`preparation_summary.json` as a lineage/gating signal before running.

## Public API (`src/features/__init__.py`)

```python
engineer_features(input_path: str, output_path: str) -> pd.DataFrame
design_sql_schema(output_path: str) -> str
setup_feature_store(features_path: str, config: Optional[Dict] = None) -> str
retrieve_features(entity_ids: list, feature_names: list, timestamp: Optional[str] = None) -> pd.DataFrame
```

These signatures match `SUBMISSION_CHECKLIST.md`'s Member 3 spec exactly
so no other module (DAG, `scripts/run_e2e.py`) needs to change.

### `engineer_features`

Builds three tables and writes them to `output_path` (default
`data/features/`):

| File | Rows | Description |
|---|---|---|
| `user_features.csv` | 1 per user | activity, rating stats, temporal patterns, genre preference vector |
| `item_features.csv` | 1 per movie | popularity, rating stats, release metadata, genre content vector |
| `interaction_features.csv` | 1 per rating event | recency/frequency, deviations, similarity & cross features |
| `engineered_features_<version>.csv` (+ `.parquet` if pyarrow/fastparquet available) | 1 per rating event | timestamped copy of `interaction_features.csv` |
| `features.csv` | 1 per rating event | **legacy** flat file (`userId, movieId, rating, user_avg, item_avg, item_count, ...`) kept for backward compatibility with Member 4's `train_model()` |

Returns the interaction-level DataFrame (one row per rating event).

### `design_sql_schema`

Generates `schema.sql` (four tables: `user_features`, `item_features`,
`interaction_features`, `feature_metadata`, with primary keys, foreign
keys and indexes) from the *live* genre vocabulary in
`dataset/movies.csv`, so the DDL can never drift from the columns the
builders actually produce. See `feature_store/schema.sql`.

### `setup_feature_store`

Reads the three feature tables from `features_path`, materializes a new
version under `feature_store/offline/<version>/`, and (re)writes:

- `feature_store/registry.json` — feature views (entity, column list,
  source file) + a list of materialized versions with timestamps.
- `feature_store/features_metadata_v<N>.json` — one entry per feature
  (name, entity, source table, dtype, human description, version).
- `feature_store/schema.sql` — via `design_sql_schema`.

### `retrieve_features`

Looks up `feature_names` for `entity_ids` from the registry's versioned
offline snapshots. If `timestamp` is given, it uses the latest version
materialized at or before that timestamp (simple point-in-time
retrieval); otherwise the latest version. Missing entities or unknown
feature names come back as `NaN` rather than raising, and a warning is
logged for unknown features — features spanning different entity types
(e.g. a user feature and an item feature) can be requested together;
each is looked up from its own table against the same `entity_ids`.

## Why a custom feature store instead of Feast

Feast needs a metastore/online-store backend and, at the time this was
built, has no published wheel for this project's Python runtime — `pip
install feast` is not reliably reproducible for a grader on a fresh
machine. The assignment explicitly allows "Feast **or custom**", so
this module implements the same responsibilities (registry, versioning,
point-in-time retrieval, documented metadata) with plain JSON +
versioned CSV snapshots (see `src/features/feature_store.py`).

## Feature catalog

### User features (`user_features.csv`, indexed by `userId`)

| Feature | Description |
|---|---|
| `num_ratings` | Activity frequency — number of ratings given |
| `avg_rating`, `median_rating`, `rating_std`, `min_rating`, `max_rating` | Rating behaviour stats |
| `most_active_hour` (0-23), `most_active_dow` (0=Mon..6=Sun) | Most common hour/day the user rates |
| `activity_span_days` | Days between the user's first and last rating |
| `avg_days_between_ratings` | Average gap between consecutive ratings |
| `num_distinct_genres_rated`, `top_genre`, `top_genre_share` | Breadth/focus of taste |
| `genre_entropy` | Shannon entropy of the user's genre distribution (taste diversity) |
| `num_tags_given` | Number of free-text tags authored |
| `activity_percentile` | Percentile rank of `num_ratings` vs all users |
| `pref_<genre>` (20 columns) | **User preference vector** — average rating given to movies tagged with that genre; genres the user never rated fall back to their overall `avg_rating` (cold-start prior) |

### Item features (`item_features.csv`, indexed by `movieId`)

| Feature | Description |
|---|---|
| `title`, `release_year`, `item_age_years` | Identity / release metadata |
| `is_new_release` | Released within the last 3 years of the catalog's release span |
| `num_genres`, `primary_genre` | Genre summary |
| `genre_<genre>` (20 columns) | **Item content vector** — one-hot genre flags |
| `num_ratings`, `popularity_percentile` | Popularity |
| `avg_rating`, `median_rating`, `rating_std` | Rating behaviour |
| `recent_avg_rating`, `rating_trend` | Seasonal/trend signal: average rating over the most recent ~25% of the item's rating events, and its delta from the all-time average |
| `num_tags`, `top_tag` | Free-text tag summary |
| `imdb_id`, `tmdb_id` | External identifiers (from `links.csv`) |

### Interaction features (`interaction_features.csv`, one row per rating event)

| Feature | Description |
|---|---|
| `interaction_id`, `userId`, `movieId`, `rating`, `timestamp`/`event_datetime` | Keys |
| `recency_days` | Days between this event and the most recent event in the dataset |
| `user_interaction_seq_num` | 1-indexed chronological position of this event for the user (frequency) |
| `days_since_user_prev_rating` | Gap since the user's previous rating (null for their first) |
| `rating_dev_from_user_avg`, `rating_dev_from_item_avg` | Rating "maturity"/normalization signals |
| `user_item_cross_rating` | Cross feature: `user_avg_rating * item_avg_rating` |
| `user_activity_x_item_popularity` | Cross feature: user activity percentile x item popularity percentile |
| `item_trending_score` | Item popularity percentile decayed by how long ago this event happened |
| `user_genre_affinity_for_item` | User's average genre preference across the genres tagged on this item |
| `top_similar_user_id`, `top_similar_user_similarity` | Nearest other user by cosine similarity of rating vectors, and the score |
| `top_similar_item_id`, `top_similar_item_similarity` | Nearest other movie by cosine similarity of genre vectors, and the score |
| `cf_predicted_rating` | Collaborative-filtering estimate: similarity-weighted rating from the user's nearest neighbours for this item (falls back to the item's average when no neighbour has rated it) |

Total: **~96 named features** across the three tables (well above the
assignment's "45+ engineered features" bar), computed with plain
numpy/pandas (no scikit-learn/scipy dependency) — user-user similarity
uses a dense cosine similarity over the (610 users x ~9.7K movies)
rating matrix, and item-item content similarity is computed in chunks
over the genre matrix to avoid materializing a full 9.7K x 9.7K matrix.

## Running it

```python
from src.features import engineer_features, design_sql_schema, setup_feature_store, retrieve_features

features_df = engineer_features(input_path="data/processed", output_path="data/features")
design_sql_schema("feature_store")
setup_feature_store("data/features")

sample = retrieve_features(entity_ids=[1, 2, 3], feature_names=["num_ratings", "avg_rating", "top_genre"])
```

Or via the existing end-to-end smoke script, which already wires this
in between preparation and model training:

```powershell
python scripts/run_e2e.py
```

Tests: `python -m unittest src.features.test_features -v` (11 tests
covering shapes, aggregate sanity checks, SQL schema content, and the
feature store registry/retrieval round trip).
