"""
Test suite for the feature engineering & feature store module (Member 3).
Runs the real MovieLens dataset through engineer_features() once (module
scope) since it takes several seconds, then exercises design_sql_schema,
setup_feature_store and retrieve_features against isolated temp dirs.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.features import engineer_features, design_sql_schema, setup_feature_store
import src.features.feature_store as feature_store_module
from src.utils.logger import logger


class TestEngineerFeatures(unittest.TestCase):
    """Tests for engineer_features()."""

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = tempfile.mkdtemp(prefix="recomart_features_test_")
        cls.output_dir = Path(cls.tmp_dir) / "features"
        cls.combined = engineer_features(
            input_path=str(project_root / "data" / "processed"),
            output_path=str(cls.output_dir),
        )
        cls.user_features = pd.read_csv(cls.output_dir / "user_features.csv")
        cls.item_features = pd.read_csv(cls.output_dir / "item_features.csv")
        cls.interaction_features = pd.read_csv(cls.output_dir / "interaction_features.csv")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def test_output_files_created(self):
        for name in ("user_features.csv", "item_features.csv", "interaction_features.csv", "features.csv"):
            self.assertTrue((self.output_dir / name).exists(), f"Missing output file: {name}")
        logger.info("PASS: engineer_features output files test passed")

    def test_returns_interaction_level_dataframe(self):
        self.assertEqual(len(self.combined), len(self.interaction_features))
        self.assertIn("rating", self.combined.columns)
        logger.info("PASS: engineer_features return value test passed")

    def test_user_features_row_count_and_activity(self):
        ratings = pd.read_csv(project_root / "dataset" / "ratings.csv")
        self.assertEqual(len(self.user_features), ratings["userId"].nunique())
        # num_ratings per user must sum to the total number of ratings.
        self.assertEqual(int(self.user_features["num_ratings"].sum()), len(ratings))
        self.assertTrue((self.user_features["avg_rating"].between(0.5, 5.0)).all())
        logger.info("PASS: user features aggregate test passed")

    def test_user_genre_preference_vector_present(self):
        pref_cols = [c for c in self.user_features.columns if c.startswith("pref_")]
        self.assertGreaterEqual(len(pref_cols), 15, "Expected a ~15+ dim genre preference vector")
        self.assertFalse(self.user_features[pref_cols].isna().any().any())
        logger.info("PASS: user preference vector test passed")

    def test_item_features_row_count_and_popularity(self):
        movies = pd.read_csv(project_root / "dataset" / "movies.csv")
        self.assertEqual(len(self.item_features), len(movies))
        self.assertTrue((self.item_features["popularity_percentile"].between(0.0, 1.0)).all())
        genre_cols = [c for c in self.item_features.columns if c.startswith("genre_")]
        self.assertGreaterEqual(len(genre_cols), 15)
        logger.info("PASS: item features aggregate test passed")

    def test_interaction_features_recency_and_deviation(self):
        self.assertTrue((self.interaction_features["recency_days"] >= 0).all())
        # First rating per user should have a null "days since previous rating".
        null_gap_count = self.interaction_features["days_since_user_prev_rating"].isna().sum()
        self.assertEqual(null_gap_count, len(self.user_features))
        recon = (
            self.interaction_features["rating"] - self.interaction_features["user_avg_rating"]
        )
        pd.testing.assert_series_equal(
            recon, self.interaction_features["rating_dev_from_user_avg"], check_names=False
        )
        logger.info("PASS: interaction features recency/deviation test passed")

    def test_similarity_features_bounded(self):
        sims = self.interaction_features["top_similar_user_similarity"].dropna()
        self.assertTrue(((sims >= -1.0001) & (sims <= 1.0001)).all())
        logger.info("PASS: similarity feature bounds test passed")


class TestSqlSchema(unittest.TestCase):
    """Tests for design_sql_schema()."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="recomart_schema_test_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_schema_contains_required_tables(self):
        schema_path = design_sql_schema(self.tmp_dir)
        self.assertTrue(Path(schema_path).exists())
        sql_text = Path(schema_path).read_text(encoding="utf-8")
        for table in ("user_features", "item_features", "interaction_features", "feature_metadata"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", sql_text)
        self.assertIn("PRIMARY KEY", sql_text)
        self.assertIn("REFERENCES", sql_text)
        logger.info("PASS: SQL schema content test passed")


class TestFeatureStore(unittest.TestCase):
    """Tests for setup_feature_store() and retrieve_features()."""

    @classmethod
    def setUpClass(cls):
        cls.tmp_root = tempfile.mkdtemp(prefix="recomart_store_test_")
        cls.features_dir = Path(cls.tmp_root) / "features"
        cls.store_dir = Path(cls.tmp_root) / "feature_store"

        engineer_features(input_path=str(project_root / "data" / "processed"), output_path=str(cls.features_dir))
        setup_feature_store(str(cls.features_dir), config={"store_dir": str(cls.store_dir)})

        # retrieve_features() always reads from the module-level default
        # store directory (fixed signature per assignment spec), so point
        # it at our isolated temp store for the duration of these tests.
        cls._original_store_dir = feature_store_module.FEATURE_STORE_DIR
        feature_store_module.FEATURE_STORE_DIR = cls.store_dir

    @classmethod
    def tearDownClass(cls):
        feature_store_module.FEATURE_STORE_DIR = cls._original_store_dir
        shutil.rmtree(cls.tmp_root, ignore_errors=True)

    def test_registry_and_metadata_created(self):
        self.assertTrue((self.store_dir / "registry.json").exists())
        self.assertTrue((self.store_dir / "features_metadata_v1.json").exists())
        self.assertTrue((self.store_dir / "schema.sql").exists())
        self.assertTrue((self.store_dir / "offline" / "v1" / "user_features.csv").exists())
        logger.info("PASS: feature store artifacts test passed")

    def test_retrieve_user_features(self):
        expected = pd.read_csv(self.features_dir / "user_features.csv").set_index("userId")
        result = feature_store_module.retrieve_features(
            entity_ids=[1, 2, 3], feature_names=["num_ratings", "avg_rating"]
        )
        self.assertEqual(len(result), 3)
        for user_id in (1, 2, 3):
            row = result[result["entity_id"] == user_id].iloc[0]
            self.assertAlmostEqual(row["avg_rating"], expected.loc[user_id, "avg_rating"], places=6)
        logger.info("PASS: retrieve_features (user) test passed")

    def test_retrieve_handles_missing_entity_and_feature(self):
        result = feature_store_module.retrieve_features(
            entity_ids=[1, 999999], feature_names=["avg_rating", "does_not_exist"]
        )
        self.assertEqual(len(result), 2)
        self.assertTrue(pd.isna(result.loc[result["entity_id"] == 999999, "avg_rating"]).all())
        self.assertTrue(result["does_not_exist"].isna().all())
        logger.info("PASS: retrieve_features missing-entity/feature test passed")


if __name__ == "__main__":
    unittest.main()
