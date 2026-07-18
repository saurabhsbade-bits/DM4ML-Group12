"""
Data Fusion Module

Integrates CSV and API data for hybrid recommendation system.
Combines user interaction data with product metadata.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple

from src.utils.logger import logger


class DataFusionEngine:
    """
    Fuses CSV and API data for recommendation system.
    
    Operations:
    - Join ratings with product metadata
    - Create enhanced item features
    - Align schemas
    - Generate hybrid features
    """

    def __init__(self):
        """Initialize data fusion engine."""
        self.fused_datasets = {}

    def fuse_ratings_with_products(
        self,
        df_ratings: pd.DataFrame,
        df_products: pd.DataFrame,
        user_col: str = "userId",
        item_col: str = "movieId",
        product_id_col: str = "id",
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fuse ratings data with product metadata from API.

        Args:
            df_ratings: Ratings DataFrame (userId, movieId, rating, timestamp)
            df_products: Products DataFrame from API (id, title, price, rating, etc.)
            user_col: User column name in ratings
            item_col: Item column name in ratings
            product_id_col: Product ID column in products

        Returns:
            Tuple of (fused_df, report)
        """
        logger.info("Fusing ratings with product metadata")

        report = {
            "initial_ratings": len(df_ratings),
            "total_products": len(df_products),
            "operations": [],
        }

        # Prepare ratings copy
        df_fused = df_ratings.copy()

        # Rename columns for joining
        df_products_join = df_products.copy()
        df_products_join = df_products_join.rename(
            columns={product_id_col: item_col}
        )

        # Join ratings with product metadata
        df_fused = df_fused.merge(
            df_products_join,
            on=item_col,
            how="left",
            suffixes=("_rating", "_product")
        )

        report["operations"].append("Joined ratings with product metadata")
        report["fused_rows"] = len(df_fused)
        report["matched_products"] = df_fused[item_col].notna().sum()
        report["unmatched_products"] = df_fused[item_col].isna().sum()

        self.fused_datasets["ratings_products"] = df_fused

        logger.info(
            f"Fused data: {len(df_fused)} rows, "
            f"{report['matched_products']} matched products"
        )

        return df_fused, report

    def create_hybrid_features(
        self,
        df_fused: pd.DataFrame,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Create hybrid features combining user-item interactions with product features.

        Args:
            df_fused: Fused ratings and products DataFrame

        Returns:
            Tuple of (df_with_features, report)
        """
        logger.info("Creating hybrid features")

        df_features = df_fused.copy()
        report = {
            "new_features": [],
        }

        # User popularity features
        if "userId" in df_features.columns:
            user_rating_counts = df_features.groupby("userId").size()
            df_features["user_rating_count"] = df_features["userId"].map(
                user_rating_counts
            )
            report["new_features"].append("user_rating_count")

        # Item popularity features
        if "movieId" in df_features.columns or "id" in df_features.columns:
            item_col = "movieId" if "movieId" in df_features.columns else "id"
            item_rating_counts = df_features.groupby(item_col).size()
            df_features["item_rating_count"] = df_features[item_col].map(
                item_rating_counts
            )
            report["new_features"].append("item_rating_count")

        # Rating quality score
        if "rating_rating" in df_features.columns and "rating_product" in df_features.columns:
            df_features["rating_alignment"] = (
                df_features["rating_rating"] / (df_features["rating_product"] + 0.1)
            )
            report["new_features"].append("rating_alignment")

        # Price-based features
        if "price" in df_features.columns:
            df_features["price_log"] = df_features["price"].apply(
                lambda x: __import__("math").log(x + 1)
            )
            report["new_features"].append("price_log")

            # Price range bucket
            df_features["price_range"] = pd.cut(
                df_features["price"],
                bins=[0, 50, 100, 500, 1000, 10000],
                labels=["budget", "economy", "mid", "premium", "luxury"]
            )
            report["new_features"].append("price_range")

        # Freshness features
        if "timestamp" in df_features.columns:
            df_features["rating_age_days"] = (
                (pd.Timestamp.now() - pd.to_datetime(df_features["timestamp"])).dt.days
            )
            report["new_features"].append("rating_age_days")

        logger.info(f"Created {len(report['new_features'])} hybrid features")
        return df_features, report

    def align_schemas(
        self,
        df_csv: pd.DataFrame,
        df_api: pd.DataFrame,
        mapping: Dict[str, str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Align column names and types between CSV and API data.

        Args:
            df_csv: CSV DataFrame
            df_api: API DataFrame
            mapping: Column name mapping {csv_name: api_name}

        Returns:
            Tuple of (df_csv_aligned, df_api_aligned)
        """
        logger.info("Aligning schemas between CSV and API data")

        df_csv_aligned = df_csv.copy()
        df_api_aligned = df_api.copy()

        if mapping:
            # Rename CSV columns
            reverse_mapping = {v: k for k, v in mapping.items()}
            df_csv_aligned = df_csv_aligned.rename(columns=reverse_mapping)

            # Rename API columns
            df_api_aligned = df_api_aligned.rename(columns=mapping)

        # Convert types to common standards
        for col in df_csv_aligned.columns:
            if col in df_api_aligned.columns:
                # Try to align types
                if df_csv_aligned[col].dtype == "object":
                    try:
                        df_csv_aligned[col] = pd.to_numeric(df_csv_aligned[col])
                    except:
                        pass

                if df_api_aligned[col].dtype == "object":
                    try:
                        df_api_aligned[col] = pd.to_numeric(df_api_aligned[col])
                    except:
                        pass

        logger.info("Schema alignment completed")
        return df_csv_aligned, df_api_aligned

    def merge_dataset_comparison(
        self,
        df_csv: pd.DataFrame,
        df_api: pd.DataFrame,
        csv_id_col: str,
        api_id_col: str,
    ) -> Dict[str, Any]:
        """
        Analyze overlap and differences between CSV and API datasets.

        Args:
            df_csv: CSV DataFrame
            df_api: API DataFrame
            csv_id_col: ID column in CSV
            api_id_col: ID column in API

        Returns:
            Comparison report
        """
        logger.info("Comparing CSV and API datasets")

        csv_ids = set(df_csv[csv_id_col].unique())
        api_ids = set(df_api[api_id_col].unique())

        overlap = csv_ids & api_ids
        csv_only = csv_ids - api_ids
        api_only = api_ids - csv_ids

        report = {
            "csv_total_items": len(csv_ids),
            "api_total_items": len(api_ids),
            "overlap_count": len(overlap),
            "overlap_percentage": (len(overlap) / max(len(csv_ids), len(api_ids))) * 100,
            "csv_only_count": len(csv_only),
            "api_only_count": len(api_only),
        }

        logger.info(
            f"Dataset comparison: {report['overlap_count']} overlapping items "
            f"({report['overlap_percentage']:.1f}%)"
        )

        return report

    def save_fused_data(self, output_dir: Path = None) -> Dict[str, Path]:
        """Save fused datasets to CSV."""
        if output_dir is None:
            output_dir = Path.cwd() / "data" / "processed"

        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}
        for dataset_name, df in self.fused_datasets.items():
            output_file = output_dir / f"fused_{dataset_name}.csv"
            df.to_csv(output_file, index=False)
            saved_files[dataset_name] = output_file
            logger.info(f"Saved fused data: {output_file}")

        return saved_files


class HybridRecommendationPreparator:
    """
    Prepares data specifically for hybrid recommendation models.
    Combines collaborative filtering with content-based features.
    """

    def __init__(self):
        """Initialize hybrid recommendation preparator."""
        self.prepared_data = {}

    def prepare_for_hybrid_model(
        self,
        df_ratings: pd.DataFrame,
        df_products: pd.DataFrame,
        user_col: str = "userId",
        item_col: str = "movieId",
        rating_col: str = "rating",
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        """
        Prepare data for hybrid recommendation model.

        Args:
            df_ratings: Ratings DataFrame
            df_products: Products DataFrame (API data)
            user_col: User column name
            item_col: Item column name
            rating_col: Rating column name

        Returns:
            Tuple of (prepared_datasets, report)
        """
        logger.info("Preparing data for hybrid recommendation model")

        prepared = {}
        report = {
            "components": [],
        }

        # 1. User-Item interaction matrix (for collaborative filtering)
        df_interactions = df_ratings[[user_col, item_col, rating_col]].copy()
        interaction_matrix = df_interactions.pivot_table(
            index=user_col,
            columns=item_col,
            values=rating_col,
            fill_value=0
        )
        prepared["interaction_matrix"] = interaction_matrix
        report["components"].append("Interaction matrix (collaborative filtering)")

        # 2. User features
        user_features = df_ratings.groupby(user_col).agg({
            rating_col: ["count", "mean", "std"],
        }).fillna(0)
        user_features.columns = ["rating_count", "avg_rating", "rating_std"]
        prepared["user_features"] = user_features
        report["components"].append("User features")

        # 3. Item features (from products)
        item_features = df_products.copy()
        if "id" in item_features.columns:
            item_features = item_features.set_index("id")
        prepared["item_features"] = item_features
        report["components"].append("Item features (content-based)")

        # 4. User-Item similarity features
        user_item_features = df_ratings.merge(
            df_products,
            left_on=item_col,
            right_on="id",
            how="left"
        )
        prepared["user_item_features"] = user_item_features
        report["components"].append("User-item combined features")

        self.prepared_data = prepared

        logger.info(f"Prepared {len(prepared)} datasets for hybrid model")
        return prepared, report

    def save_prepared_data(self, output_dir: Path = None) -> Dict[str, Path]:
        """Save prepared data for hybrid model."""
        if output_dir is None:
            output_dir = Path.cwd() / "data" / "processed"

        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}
        for component_name, df in self.prepared_data.items():
            output_file = output_dir / f"hybrid_{component_name}.csv"
            df.to_csv(output_file)
            saved_files[component_name] = output_file
            logger.info(f"Saved hybrid component: {output_file}")

        return saved_files
