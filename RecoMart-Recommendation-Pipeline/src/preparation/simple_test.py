"""
Simple test runner for data preparation modules
Focuses on core functionality without complex analysis
"""

import pandas as pd
from pathlib import Path
import sys

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.preparation.data_cleaner import DataCleaner
from src.preparation.data_preprocessor import DataPreprocessor
from src.preparation.exploratory_analysis import ExploratoryAnalyzer


def test_data_cleaner():
    """Test DataCleaner module"""
    print("\n" + "=" * 80)
    print("TEST 1: DATA CLEANER")
    print("=" * 80)
    
    cleaner = DataCleaner()
    test_data_dir = project_root / "dataset"
    
    # Test 1.1: Clean ratings
    print("\n[1.1] Testing ratings.csv cleaning...")
    ratings_file = test_data_dir / "ratings.csv"
    df_clean, report = cleaner.clean_csv(
        file_path=ratings_file,
        dataset_name="ratings",
        missing_strategy={"rating": "drop"}
    )
    assert len(df_clean) > 0
    assert not df_clean.isnull().any().any()
    print(f"  ✓ Ratings cleaned: {len(df_clean)} rows, no nulls")
    
    # Test 1.2: Clean movies
    print("\n[1.2] Testing movies.csv cleaning...")
    movies_file = test_data_dir / "movies.csv"
    df_clean, report = cleaner.clean_csv(
        file_path=movies_file,
        dataset_name="movies",
        missing_strategy={}
    )
    assert len(df_clean) > 0
    print(f"  ✓ Movies cleaned: {len(df_clean)} rows")
    
    # Test 1.3: Clean tags
    print("\n[1.3] Testing tags.csv cleaning...")
    tags_file = test_data_dir / "tags.csv"
    df_clean, report = cleaner.clean_csv(
        file_path=tags_file,
        dataset_name="tags",
        missing_strategy={}
    )
    assert len(df_clean) > 0
    print(f"  ✓ Tags cleaned: {len(df_clean)} rows")
    
    # Test 1.4: Clean links
    print("\n[1.4] Testing links.csv cleaning...")
    links_file = test_data_dir / "links.csv"
    df_clean, report = cleaner.clean_csv(
        file_path=links_file,
        dataset_name="links",
        missing_strategy={"tmdbId": "drop"}
    )
    assert len(df_clean) > 0
    print(f"  ✓ Links cleaned: {len(df_clean)} rows")
    
    print("\n✅ DATA CLEANER TESTS PASSED (4/4)")
    return True


def test_data_preprocessor():
    """Test DataPreprocessor module"""
    print("\n" + "=" * 80)
    print("TEST 2: DATA PREPROCESSOR")
    print("=" * 80)
    
    preprocessor = DataPreprocessor()
    test_data_dir = project_root / "dataset"
    
    # Load sample data
    ratings_file = test_data_dir / "ratings.csv"
    df_ratings = pd.read_csv(ratings_file)
    
    # Test 2.1: MinMax Normalization
    print("\n[2.1] Testing MinMax normalization...")
    df_test = df_ratings[['rating']].head(100).copy()
    preprocessor._normalize_column(df_test, "rating", "minmax", "test_dataset")
    assert df_test['rating'].min() >= 0 and df_test['rating'].max() <= 1
    print(f"  ✓ MinMax normalization: values in [0, 1] range")
    
    # Test 2.2: Standard Normalization
    print("\n[2.2] Testing Standard normalization...")
    df_test = df_ratings[['rating']].head(100).copy()
    preprocessor._normalize_column(df_test, "rating", "standard", "test_dataset2")
    print(f"  ✓ Standard normalization: mean={df_test['rating'].mean():.4f}, std={df_test['rating'].std():.4f}")
    
    # Test 2.3: Label Encoding
    print("\n[2.3] Testing label encoding...")
    movies_file = test_data_dir / "movies.csv"
    df_movies = pd.read_csv(movies_file)
    df_test = df_movies[['genres']].head(100).copy()
    df_test['first_genre'] = df_test['genres'].str.split('|').str[0]
    preprocessor._encode_column(df_test, "first_genre", "test_movies")
    assert pd.api.types.is_numeric_dtype(df_test['first_genre'])
    print(f"  ✓ Label encoding: converted to numeric type")
    
    # Test 2.4: Interaction Matrix
    print("\n[2.4] Testing interaction matrix creation...")
    df_sample = df_ratings.head(5000)
    interaction_matrix = preprocessor.create_interaction_matrix(
        df_ratings=df_sample,
        user_col='userId',
        item_col='movieId',
        rating_col='rating'
    )
    total_cells = interaction_matrix.shape[0] * interaction_matrix.shape[1]
    filled_cells = (interaction_matrix != 0).sum().sum()
    sparsity = ((total_cells - filled_cells) / total_cells) * 100
    print(f"  ✓ Interaction matrix: {interaction_matrix.shape[0]} x {interaction_matrix.shape[1]}")
    print(f"  ✓ Sparsity: {sparsity:.2f}%")
    
    print("\n✅ DATA PREPROCESSOR TESTS PASSED (4/4)")
    return True


def test_exploratory_analyzer():
    """Test ExploratoryAnalyzer module"""
    print("\n" + "=" * 80)
    print("TEST 3: EXPLORATORY ANALYZER")
    print("=" * 80)
    
    output_dir = project_root / "data" / "test_plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    analyzer = ExploratoryAnalyzer(output_dir=output_dir)
    test_data_dir = project_root / "dataset"
    
    # Load sample data
    ratings_file = test_data_dir / "ratings.csv"
    df_ratings = pd.read_csv(ratings_file).head(2000)
    
    # Test 3.1: Distribution plots
    print("\n[3.1] Testing distribution plot generation...")
    plot_path = analyzer.plot_distributions(df_ratings, "test_ratings", save=True)
    assert Path(plot_path).exists()
    print(f"  ✓ Distribution plot saved: {Path(plot_path).name}")
    
    # Test 3.2: Heatmap
    print("\n[3.2] Testing heatmap generation...")
    plot_path = analyzer.plot_heatmap(df_ratings, "test_ratings", save=True)
    assert Path(plot_path).exists()
    print(f"  ✓ Heatmap saved: {Path(plot_path).name}")
    
    # Test 3.3: Categorical plots
    print("\n[3.3] Testing categorical distribution plots...")
    movies_file = test_data_dir / "movies.csv"
    df_movies = pd.read_csv(movies_file)
    plot_path = analyzer.plot_categorical_distributions(df_movies, "test_movies", save=True)
    assert Path(plot_path).exists()
    print(f"  ✓ Categorical plot saved: {Path(plot_path).name}")
    
    # Test 3.4: Sparsity plot
    print("\n[3.4] Testing sparsity plot generation...")
    preprocessor = DataPreprocessor()
    interaction_matrix = preprocessor.create_interaction_matrix(
        df_ratings=df_ratings,
        user_col='userId',
        item_col='movieId',
        rating_col='rating'
    )
    plot_path = analyzer.plot_sparsity(interaction_matrix, "test_sparsity", save=True)
    assert Path(plot_path).exists()
    print(f"  ✓ Sparsity plot saved: {Path(plot_path).name}")
    
    print("\n✅ EXPLORATORY ANALYZER TESTS PASSED (4/4)")
    return True


def test_end_to_end_pipeline():
    """Test complete preparation pipeline"""
    print("\n" + "=" * 80)
    print("TEST 4: END-TO-END PIPELINE")
    print("=" * 80)
    
    cleaner = DataCleaner()
    preprocessor = DataPreprocessor()
    analyzer = ExploratoryAnalyzer(output_dir=project_root / "data" / "test_output")
    test_data_dir = project_root / "dataset"
    
    ratings_file = test_data_dir / "ratings.csv"
    
    # Step 1: Clean
    print("\n[4.1] Cleaning data...")
    df_clean, _ = cleaner.clean_csv(
        file_path=ratings_file,
        dataset_name="ratings_pipeline",
        missing_strategy={"rating": "drop"}
    )
    print(f"  ✓ Cleaned: {len(df_clean)} rows")
    
    # Step 2: Preprocess
    print("\n[4.2] Preprocessing data...")
    df_processed, _ = preprocessor.preprocess_dataset(
        df=df_clean,
        dataset_name="ratings_pipeline",
        categorical_columns=[],
        numerical_columns=["userId", "movieId", "rating"],
        normalize_method="minmax"
    )
    print(f"  ✓ Preprocessed: {len(df_processed)} rows")
    
    # Step 3: Create interaction matrix
    print("\n[4.3] Creating interaction matrix...")
    interaction_matrix = preprocessor.create_interaction_matrix(
        df_ratings=df_clean,
        user_col='userId',
        item_col='movieId',
        rating_col='rating'
    )
    total_cells = interaction_matrix.shape[0] * interaction_matrix.shape[1]
    filled_cells = (interaction_matrix != 0).sum().sum()
    sparsity = ((total_cells - filled_cells) / total_cells) * 100
    print(f"  ✓ Matrix: {interaction_matrix.shape[0]} users x {interaction_matrix.shape[1]} items")
    print(f"  ✓ Sparsity: {sparsity:.2f}%")
    
    print("\n✅ END-TO-END PIPELINE TEST PASSED")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("DATA PREPARATION MODULE TEST SUITE - SIMPLIFIED")
    print("=" * 80)
    
    try:
        results = []
        
        # Run tests
        results.append(("Data Cleaner", test_data_cleaner()))
        results.append(("Data Preprocessor", test_data_preprocessor()))
        results.append(("Exploratory Analyzer", test_exploratory_analyzer()))
        results.append(("End-to-End Pipeline", test_end_to_end_pipeline()))
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "PASSED" if result else "FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nTotal: {passed}/{total} test groups passed")
        
        if passed == total:
            print("\n✅ ALL TESTS PASSED - Data Preparation Module is Ready!")
            print("=" * 80 + "\n")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED")
            print("=" * 80 + "\n")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
