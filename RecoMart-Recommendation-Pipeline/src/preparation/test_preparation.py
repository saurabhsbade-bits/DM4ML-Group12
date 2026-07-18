"""
Test suite for data preparation modules
Tests DataCleaner, DataPreprocessor, and ExploratoryAnalyzer
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import unittest
from datetime import datetime

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.preparation.data_cleaner import DataCleaner
from src.preparation.data_preprocessor import DataPreprocessor
from src.preparation.exploratory_analysis import ExploratoryAnalyzer
from src.utils.logger import logger


class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner class"""
    
    def setUp(self):
        """Initialize test fixtures"""
        self.cleaner = DataCleaner()
        self.test_data_dir = project_root / "dataset"
        
    def test_cleaner_initialization(self):
        """Test that DataCleaner initializes correctly"""
        self.assertIsNotNone(self.cleaner)
        logger.info("✓ DataCleaner initialization test passed")
        
    def test_clean_ratings_csv(self):
        """Test cleaning ratings.csv"""
        ratings_file = self.test_data_dir / "ratings.csv"
        
        self.assertTrue(ratings_file.exists(), f"Ratings file not found: {ratings_file}")
        
        missing_strategy = {
            "rating": "drop",
            "timestamp": "drop"
        }
        
        df_clean, report = self.cleaner.clean_csv(
            file_path=ratings_file,
            dataset_name="ratings",
            missing_strategy=missing_strategy
        )
        
        # Assertions
        self.assertIsNotNone(df_clean)
        self.assertGreater(len(df_clean), 0)
        self.assertFalse(df_clean.isnull().any().any(), "Cleaned data contains null values")
        
        logger.info(f"✓ Ratings cleaning test passed: {len(df_clean)} rows")
        
    def test_clean_movies_csv(self):
        """Test cleaning movies.csv"""
        movies_file = self.test_data_dir / "movies.csv"
        
        self.assertTrue(movies_file.exists(), f"Movies file not found: {movies_file}")
        
        df_clean, report = self.cleaner.clean_csv(
            file_path=movies_file,
            dataset_name="movies",
            missing_strategy={}
        )
        
        self.assertIsNotNone(df_clean)
        self.assertGreater(len(df_clean), 0)
        
        logger.info(f"✓ Movies cleaning test passed: {len(df_clean)} rows")
        
    def test_clean_tags_csv(self):
        """Test cleaning tags.csv"""
        tags_file = self.test_data_dir / "tags.csv"
        
        self.assertTrue(tags_file.exists(), f"Tags file not found: {tags_file}")
        
        df_clean, report = self.cleaner.clean_csv(
            file_path=tags_file,
            dataset_name="tags",
            missing_strategy={}
        )
        
        self.assertIsNotNone(df_clean)
        self.assertGreater(len(df_clean), 0)
        
        logger.info(f"✓ Tags cleaning test passed: {len(df_clean)} rows")
        
    def test_clean_links_csv(self):
        """Test cleaning links.csv"""
        links_file = self.test_data_dir / "links.csv"
        
        self.assertTrue(links_file.exists(), f"Links file not found: {links_file}")
        
        df_clean, report = self.cleaner.clean_csv(
            file_path=links_file,
            dataset_name="links",
            missing_strategy={"imdbId": "drop", "tmdbId": "drop"}
        )
        
        self.assertIsNotNone(df_clean)
        self.assertGreater(len(df_clean), 0)
        
        logger.info(f"✓ Links cleaning test passed: {len(df_clean)} rows")


class TestDataPreprocessor(unittest.TestCase):
    """Test cases for DataPreprocessor class"""
    
    def setUp(self):
        """Initialize test fixtures"""
        self.preprocessor = DataPreprocessor()
        self.test_data_dir = project_root / "dataset"
        
        # Load and clean test data
        self.cleaner = DataCleaner()
        
    def test_preprocessor_initialization(self):
        """Test that DataPreprocessor initializes correctly"""
        self.assertIsNotNone(self.preprocessor)
        logger.info("✓ DataPreprocessor initialization test passed")
        
    def test_minmax_normalization(self):
        """Test MinMax normalization"""
        ratings_file = self.test_data_dir / "ratings.csv"
        df = pd.read_csv(ratings_file).head(100)
        
        # Normalize rating column
        df_normalized = df.copy()
        scaler = self.preprocessor._normalize_column(df_normalized, "rating", "minmax")
        
        # Check normalization results
        self.assertGreaterEqual(df_normalized["rating"].min(), 0)
        self.assertLessEqual(df_normalized["rating"].max(), 1)
        
        logger.info("✓ MinMax normalization test passed")
        
    def test_standard_normalization(self):
        """Test Standard normalization"""
        ratings_file = self.test_data_dir / "ratings.csv"
        df = pd.read_csv(ratings_file).head(100)
        
        # Normalize rating column
        df_normalized = df.copy()
        scaler = self.preprocessor._normalize_column(df_normalized, "rating", "standard")
        
        # Check normalization results (mean ≈ 0, std ≈ 1)
        self.assertAlmostEqual(df_normalized["rating"].mean(), 0, places=0)
        self.assertAlmostEqual(df_normalized["rating"].std(), 1, places=0)
        
        logger.info("✓ Standard normalization test passed")
        
    def test_label_encoding(self):
        """Test label encoding for categorical variables"""
        movies_file = self.test_data_dir / "movies.csv"
        df = pd.read_csv(movies_file).head(100)
        
        # Extract first genre (categorical)
        df['first_genre'] = df['genres'].str.split('|').str[0]
        
        # Encode
        df_encoded = df.copy()
        self.preprocessor._encode_column(df_encoded, "first_genre")
        
        # Check encoding
        self.assertFalse(df_encoded['first_genre'].dtype == 'object')
        self.assertTrue(pd.api.types.is_numeric_dtype(df_encoded['first_genre']))
        
        logger.info("✓ Label encoding test passed")
        
    def test_interaction_matrix_creation(self):
        """Test interaction matrix creation"""
        ratings_file = self.test_data_dir / "ratings.csv"
        df_ratings = pd.read_csv(ratings_file)
        
        # Create interaction matrix
        interaction_matrix = self.preprocessor.create_interaction_matrix(
            df_ratings=df_ratings,
            user_col='userId',
            item_col='movieId',
            rating_col='rating'
        )
        
        # Assertions
        self.assertIsNotNone(interaction_matrix)
        self.assertEqual(len(interaction_matrix.shape), 2)
        self.assertGreater(interaction_matrix.shape[0], 0)  # users
        self.assertGreater(interaction_matrix.shape[1], 0)  # items
        
        # Check sparsity
        total_cells = interaction_matrix.shape[0] * interaction_matrix.shape[1]
        filled_cells = (interaction_matrix != 0).sum().sum()
        sparsity = ((total_cells - filled_cells) / total_cells) * 100
        
        self.assertGreater(sparsity, 90)  # Should be highly sparse
        logger.info(f"✓ Interaction matrix test passed: {interaction_matrix.shape}, sparsity: {sparsity:.2f}%")


class TestExploratoryAnalyzer(unittest.TestCase):
    """Test cases for ExploratoryAnalyzer class"""
    
    def setUp(self):
        """Initialize test fixtures"""
        self.output_dir = project_root / "data" / "test_plots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = ExploratoryAnalyzer(output_dir=self.output_dir)
        self.test_data_dir = project_root / "dataset"
        
    def test_analyzer_initialization(self):
        """Test that ExploratoryAnalyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertTrue(self.output_dir.exists())
        logger.info("✓ ExploratoryAnalyzer initialization test passed")
        
    def test_dataset_analysis(self):
        """Test dataset analysis"""
        ratings_file = self.test_data_dir / "ratings.csv"
        df = pd.read_csv(ratings_file)
        
        analysis = self.analyzer.analyze_dataset(df, "ratings_test")
        
        self.assertIsNotNone(analysis)
        self.assertIn('basic_stats', analysis)
        self.assertIn('missing_values', analysis)
        
        logger.info("✓ Dataset analysis test passed")
        
    def test_distribution_plots(self):
        """Test distribution plot generation"""
        ratings_file = self.test_data_dir / "ratings.csv"
        df = pd.read_csv(ratings_file)
        
        plot_path = self.analyzer.plot_distributions(df, "ratings_test", save=True)
        
        self.assertIsNotNone(plot_path)
        self.assertTrue(Path(plot_path).exists())
        
        logger.info(f"✓ Distribution plots test passed: {plot_path}")
        
    def test_heatmap_generation(self):
        """Test heatmap generation"""
        ratings_file = self.test_data_dir / "ratings.csv"
        df = pd.read_csv(ratings_file).head(1000)
        
        plot_path = self.analyzer.plot_heatmap(df, "ratings_test", save=True)
        
        self.assertIsNotNone(plot_path)
        self.assertTrue(Path(plot_path).exists())
        
        logger.info(f"✓ Heatmap generation test passed: {plot_path}")
        
    def test_sparsity_plot(self):
        """Test sparsity plot generation"""
        ratings_file = self.test_data_dir / "ratings.csv"
        df_ratings = pd.read_csv(ratings_file)
        
        # Create small interaction matrix for testing
        preprocessor = DataPreprocessor()
        interaction_matrix = preprocessor.create_interaction_matrix(
            df_ratings=df_ratings.head(1000),
            user_col='userId',
            item_col='movieId',
            rating_col='rating'
        )
        
        plot_path = self.analyzer.plot_sparsity(interaction_matrix, "test_sparsity", save=True)
        
        self.assertIsNotNone(plot_path)
        self.assertTrue(Path(plot_path).exists())
        
        logger.info(f"✓ Sparsity plot test passed: {plot_path}")
        
    def test_categorical_distributions(self):
        """Test categorical distribution plots"""
        movies_file = self.test_data_dir / "movies.csv"
        df = pd.read_csv(movies_file)
        
        plot_path = self.analyzer.plot_categorical_distributions(df, "movies_test", save=True)
        
        self.assertIsNotNone(plot_path)
        self.assertTrue(Path(plot_path).exists())
        
        logger.info(f"✓ Categorical distributions test passed: {plot_path}")


class TestEndToEndPipeline(unittest.TestCase):
    """Integration tests for complete pipeline"""
    
    def setUp(self):
        """Initialize test fixtures"""
        self.cleaner = DataCleaner()
        self.preprocessor = DataPreprocessor()
        self.analyzer = ExploratoryAnalyzer(output_dir=project_root / "data" / "test_output")
        self.test_data_dir = project_root / "dataset"
        
    def test_full_preparation_pipeline(self):
        """Test complete preparation pipeline: clean -> preprocess -> analyze"""
        ratings_file = self.test_data_dir / "ratings.csv"
        
        print("\n" + "=" * 80)
        print("FULL PREPARATION PIPELINE TEST")
        print("=" * 80)
        
        # Step 1: Clean
        print("\n[1/4] Cleaning data...")
        df_clean, clean_report = self.cleaner.clean_csv(
            file_path=ratings_file,
            dataset_name="ratings_test",
            missing_strategy={"rating": "drop", "timestamp": "drop"}
        )
        self.assertIsNotNone(df_clean)
        print(f"  ✓ Cleaned: {len(df_clean)} rows")
        
        # Step 2: Preprocess
        print("\n[2/4] Preprocessing data...")
        df_processed, preprocess_report = self.preprocessor.preprocess_dataset(
            df=df_clean,
            dataset_name="ratings_test",
            categorical_columns=[],
            numerical_columns=["userId", "movieId", "rating", "timestamp"],
            normalize_method="minmax"
        )
        self.assertIsNotNone(df_processed)
        print(f"  ✓ Preprocessed: {len(df_processed)} rows")
        
        # Step 3: Create interaction matrix
        print("\n[3/4] Creating interaction matrix...")
        interaction_matrix = self.preprocessor.create_interaction_matrix(
            df_ratings=df_clean,
            user_col='userId',
            item_col='movieId',
            rating_col='rating'
        )
        self.assertIsNotNone(interaction_matrix)
        
        total_cells = interaction_matrix.shape[0] * interaction_matrix.shape[1]
        filled_cells = (interaction_matrix != 0).sum().sum()
        sparsity = ((total_cells - filled_cells) / total_cells) * 100
        print(f"  ✓ Matrix: {interaction_matrix.shape[0]} users × {interaction_matrix.shape[1]} items")
        print(f"  ✓ Sparsity: {sparsity:.2f}%")
        
        # Step 4: Analyze
        print("\n[4/4] Analyzing data...")
        analysis = self.analyzer.analyze_dataset(df_processed, "ratings_test")
        self.assertIsNotNone(analysis)
        print(f"  ✓ Analysis complete")
        
        print("\n" + "=" * 80)
        print("✅ FULL PIPELINE TEST PASSED")
        print("=" * 80 + "\n")
        
        return True


def run_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("DATA PREPARATION MODULE TEST SUITE")
    print("=" * 80 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataCleaner))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPreprocessor))
    suite.addTests(loader.loadTestsFromTestCase(TestExploratoryAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndPipeline))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("=" * 80 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
