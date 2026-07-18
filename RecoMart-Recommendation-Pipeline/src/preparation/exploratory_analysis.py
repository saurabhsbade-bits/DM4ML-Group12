"""
Exploratory Data Analysis Module

Performs comprehensive EDA including distributions, patterns, and sparsity analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Tuple
from src.utils.logger import logger


class ExploratoryAnalyzer:
    """
    Performs exploratory data analysis with visualizations.
    """

    def __init__(self, output_dir: Path = None):
        """Initialize analyzer with output directory."""
        if output_dir is None:
            output_dir = Path(__file__).resolve().parents[2] / "data" / "plots"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = (12, 6)

    def analyze_dataset(self, df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """
        Perform comprehensive EDA on dataset.

        Args:
            df: Input DataFrame
            dataset_name: Name of dataset

        Returns:
            Dictionary with analysis results
        """

        logger.info(f"Analyzing dataset: {dataset_name}")

        analysis = {
            "dataset": dataset_name,
            "basic_stats": self._basic_statistics(df),
            "distributions": self._analyze_distributions(df, dataset_name),
            "correlations": self._analyze_correlations(df, dataset_name),
        }

        return analysis

    def _basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistics."""
        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isna().sum().to_dict(),
            "duplicates": int(df.duplicated().sum()),
            "numerical_stats": df.describe().to_dict(),
        }

    def _analyze_distributions(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Dict[str, Any]:
        """Analyze column distributions."""
        distributions = {}

        # Numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns

        for col in numerical_cols:
            distributions[col] = {
                "type": "numerical",
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "skewness": float(df[col].skew()),
                "kurtosis": float(df[col].kurtosis()),
            }

        # Categorical columns
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns

        for col in categorical_cols:
            distributions[col] = {
                "type": "categorical",
                "unique_values": int(df[col].nunique()),
                "top_values": df[col].value_counts().head(10).to_dict(),
            }

        return distributions

    def _analyze_correlations(
        self, df: pd.DataFrame, dataset_name: str
    ) -> Dict[str, Any]:
        """Analyze correlations between numerical columns."""
        numerical_df = df.select_dtypes(include=[np.number])

        if len(numerical_df.columns) < 2:
            return {"status": "Not enough numerical columns for correlation"}

        corr_matrix = numerical_df.corr()

        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "highly_correlated_pairs": self._find_high_correlations(corr_matrix),
        }

    def _find_high_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Tuple]:
        """Find highly correlated feature pairs."""
        pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    pairs.append({
                        "feature1": corr_matrix.columns[i],
                        "feature2": corr_matrix.columns[j],
                        "correlation": float(corr_matrix.iloc[i, j]),
                    })

        return pairs

    def plot_distributions(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        save: bool = True,
    ) -> Path:
        """
        Plot distributions of numerical columns.

        Args:
            df: Input DataFrame
            dataset_name: Name of dataset
            save: Whether to save plot

        Returns:
            Path to saved plot
        """

        numerical_cols = df.select_dtypes(include=[np.number]).columns

        if len(numerical_cols) == 0:
            logger.warning(f"No numerical columns found in {dataset_name}")
            return None

        # Create subplots
        n_cols = min(3, len(numerical_cols))
        n_rows = (len(numerical_cols) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))

        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1 or n_cols == 1:
            axes = axes.reshape(n_rows, n_cols)

        for idx, col in enumerate(numerical_cols):
            row = idx // n_cols
            col_idx = idx % n_cols

            ax = axes[row, col_idx]

            # Histogram with KDE
            ax.hist(df[col], bins=30, alpha=0.7, edgecolor="black")
            ax.set_title(f"Distribution of {col}", fontsize=12, fontweight="bold")
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for idx in range(len(numerical_cols), n_rows * n_cols):
            row = idx // n_cols
            col_idx = idx % n_cols
            axes[row, col_idx].set_visible(False)

        plt.tight_layout()

        if save:
            plot_path = self.output_dir / f"{dataset_name}_distributions.png"
            plt.savefig(plot_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved distribution plot: {plot_path}")
            plt.close()
            return plot_path

        return None

    def plot_heatmap(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        save: bool = True,
    ) -> Path:
        """
        Plot correlation heatmap for numerical columns.

        Args:
            df: Input DataFrame
            dataset_name: Name of dataset
            save: Whether to save plot

        Returns:
            Path to saved plot
        """

        numerical_df = df.select_dtypes(include=[np.number])

        if len(numerical_df.columns) < 2:
            logger.warning(f"Not enough numerical columns for heatmap in {dataset_name}")
            return None

        corr_matrix = numerical_df.corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"label": "Correlation"},
            ax=ax,
        )

        ax.set_title(f"Correlation Heatmap - {dataset_name}", fontsize=14, fontweight="bold")
        plt.tight_layout()

        if save:
            plot_path = self.output_dir / f"{dataset_name}_heatmap.png"
            plt.savefig(plot_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved heatmap: {plot_path}")
            plt.close()
            return plot_path

        return None

    def plot_sparsity(
        self,
        interaction_matrix: pd.DataFrame,
        dataset_name: str = "interactions",
        save: bool = True,
    ) -> Path:
        """
        Plot sparsity analysis of interaction matrix.

        Args:
            interaction_matrix: User-item interaction matrix
            dataset_name: Name of dataset
            save: Whether to save plot

        Returns:
            Path to saved plot
        """

        # Calculate sparsity metrics
        total_cells = interaction_matrix.shape[0] * interaction_matrix.shape[1]
        filled_cells = (interaction_matrix != 0).sum().sum()
        sparsity = ((total_cells - filled_cells) / total_cells) * 100

        # Calculate per-user and per-item statistics
        user_interactions = (interaction_matrix != 0).sum(axis=1)
        item_interactions = (interaction_matrix != 0).sum(axis=0)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot 1: User interaction distribution
        axes[0, 0].hist(user_interactions, bins=50, alpha=0.7, edgecolor="black", color="skyblue")
        axes[0, 0].set_title("Distribution of User Interactions", fontweight="bold")
        axes[0, 0].set_xlabel("Number of Items Rated per User")
        axes[0, 0].set_ylabel("Number of Users")
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Item popularity distribution
        axes[0, 1].hist(item_interactions, bins=50, alpha=0.7, edgecolor="black", color="lightcoral")
        axes[0, 1].set_title("Distribution of Item Popularity", fontweight="bold")
        axes[0, 1].set_xlabel("Number of Users Who Rated Item")
        axes[0, 1].set_ylabel("Number of Items")
        axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Sparsity pie chart
        sparsity_data = [filled_cells, total_cells - filled_cells]
        axes[1, 0].pie(
            sparsity_data,
            labels=["Filled", "Empty"],
            autopct="%1.2f%%",
            colors=["#66c2a5", "#fc8d62"],
        )
        axes[1, 0].set_title(f"Matrix Sparsity: {sparsity:.2f}%", fontweight="bold")

        # Plot 4: Sparsity statistics
        axes[1, 1].axis("off")
        sparsity_stats = f"""
        Matrix Shape: {interaction_matrix.shape[0]} users × {interaction_matrix.shape[1]} items
        
        Total Cells: {total_cells:,}
        Filled Cells: {filled_cells:,}
        Empty Cells: {total_cells - filled_cells:,}
        
        Sparsity: {sparsity:.2f}%
        Density: {(filled_cells/total_cells)*100:.2f}%
        
        User Stats:
          Min interactions: {user_interactions.min()}
          Max interactions: {user_interactions.max()}
          Mean interactions: {user_interactions.mean():.2f}
          
        Item Stats:
          Min popularity: {item_interactions.min()}
          Max popularity: {item_interactions.max()}
          Mean popularity: {item_interactions.mean():.2f}
        """
        axes[1, 1].text(0.1, 0.5, sparsity_stats, fontsize=11, family="monospace",
                       verticalalignment="center")

        plt.tight_layout()

        if save:
            plot_path = self.output_dir / f"{dataset_name}_sparsity.png"
            plt.savefig(plot_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved sparsity plot: {plot_path}")
            plt.close()
            return plot_path

        return None

    def plot_categorical_distributions(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        save: bool = True,
    ) -> Path:
        """
        Plot distributions of categorical columns.

        Args:
            df: Input DataFrame
            dataset_name: Name of dataset
            save: Whether to save plot

        Returns:
            Path to saved plot
        """

        categorical_cols = df.select_dtypes(include=["object", "category"]).columns

        if len(categorical_cols) == 0:
            logger.warning(f"No categorical columns found in {dataset_name}")
            return None

        n_cols = min(2, len(categorical_cols))
        n_rows = (len(categorical_cols) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 5 * n_rows))

        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1 or n_cols == 1:
            axes = axes.reshape(n_rows, n_cols)

        for idx, col in enumerate(categorical_cols):
            row = idx // n_cols
            col_idx = idx % n_cols

            ax = axes[row, col_idx]

            # Get top 10 categories
            top_values = df[col].value_counts().head(10)

            ax.barh(top_values.index, top_values.values, color="steelblue")
            ax.set_title(f"Top Categories - {col}", fontsize=12, fontweight="bold")
            ax.set_xlabel("Frequency")
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3, axis="x")

        # Hide unused subplots
        for idx in range(len(categorical_cols), n_rows * n_cols):
            row = idx // n_cols
            col_idx = idx % n_cols
            axes[row, col_idx].set_visible(False)

        plt.tight_layout()

        if save:
            plot_path = self.output_dir / f"{dataset_name}_categorical.png"
            plt.savefig(plot_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved categorical plot: {plot_path}")
            plt.close()
            return plot_path

        return None
