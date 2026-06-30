import os
import pandas as pd
import numpy as np
import logging
from backend.utils.csv_reader import read_csv_with_encodings
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AnalyzerAgent:
    """
    AnalyzerAgent runs statistical computations on clean datasets.
    It extracts row/col counts, classifies column types, calculates descriptive statistics,
    identifies null distributions, creates correlation matrices, and summarizes categorical variables.
    """

    def __init__(self, calculation_depth: str = "standard") -> None:
        """
        Initializes the AnalyzerAgent.

        Args:
            calculation_depth (str): Detail level of analysis (e.g. 'standard', 'deep').
        """
        self.calculation_depth = calculation_depth

    def analyze(self, clean_file_path: str, query: str = None) -> Dict[str, Any]:
        """
        Runs statistical analyses and custom operations on the clean dataset.

        Args:
            clean_file_path (str): The absolute path to the clean CSV file.
            query (str, optional): Custom analytical question or target metrics.

        Returns:
            Dict[str, Any]: Structured summary metrics, column details, and correlations.
        """
        logger.info(f"AnalyzerAgent starting on file: {clean_file_path}")
        if not os.path.exists(clean_file_path):
            raise FileNotFoundError(f"File not found: {clean_file_path}")

        try:
            df = read_csv_with_encodings(clean_file_path)
            
            # Extract basic structure
            num_rows = int(df.shape[0])
            num_cols = int(df.shape[1])

            # Classify columns
            numeric_cols = []
            categorical_cols = []
            other_cols = []

            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    numeric_cols.append(col)
                elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                    # Treat small cardinality as categorical
                    categorical_cols.append(col)
                else:
                    other_cols.append(col)

            # Compute stats
            desc_stats = self.calculate_descriptive_statistics(df, numeric_cols)
            null_counts = self.calculate_null_counts(df)
            correlation_matrix = self.calculate_correlation_matrix(df, numeric_cols)
            top_categorical = self.calculate_top_categorical_values(df, categorical_cols)

            # Extract dataset preview (first 10 rows)
            preview_rows = df.head(10).replace({np.nan: None}).to_dict(orient="records")
            preview_columns = list(df.columns)

            analysis_result = {
                "num_rows": num_rows,
                "num_columns": num_cols,
                "numeric_columns": numeric_cols,
                "categorical_columns": categorical_cols,
                "other_columns": other_cols,
                "null_counts": null_counts,
                "descriptive_statistics": desc_stats,
                "correlation_matrix": correlation_matrix,
                "top_categorical_values": top_categorical,
                "dataset_preview": {
                    "columns": preview_columns,
                    "rows": preview_rows
                }
            }

            # Sanitize numpy types & NaN/Inf for JSON compliance
            return self._sanitize_for_json(analysis_result)

        except Exception as e:
            logger.error(f"Error occurred during analysis: {str(e)}")
            raise e

    def calculate_descriptive_statistics(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Calculates mean, median, min, max, std, and quantiles (25%, 50%, 75%) for numeric columns.
        """
        stats_summary = {}
        if not numeric_cols:
            return stats_summary

        # Compute using pandas describe & median
        desc = df[numeric_cols].describe()
        medians = df[numeric_cols].median()

        for col in numeric_cols:
            col_stats = desc[col]
            stats_summary[col] = {
                "count": float(col_stats.get("count", 0)),
                "mean": float(col_stats.get("mean", 0)),
                "std": float(col_stats.get("std", 0)),
                "min": float(col_stats.get("min", 0)),
                "q25": float(col_stats.get("25%", 0)),
                "median": float(medians.get(col, 0)),
                "q75": float(col_stats.get("75%", 0)),
                "max": float(col_stats.get("max", 0))
            }
        return stats_summary

    def calculate_null_counts(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Calculates null/NaN count per column.
        """
        return {str(col): int(count) for col, count in df.isnull().sum().to_dict().items()}

    def calculate_correlation_matrix(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Calculates the Pearson correlation matrix for numeric columns only.
        """
        if len(numeric_cols) < 2:
            return {}
        
        corr_df = df[numeric_cols].corr(method="pearson")
        return corr_df.to_dict()

    def calculate_top_categorical_values(self, df: pd.DataFrame, categorical_cols: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Calculates the most frequent values for each categorical column.
        """
        top_values = {}
        for col in categorical_cols:
            # Value counts of top 10 most common categories
            counts = df[col].value_counts().head(10)
            items = []
            for val, count in counts.items():
                items.append({
                    "value": str(val),
                    "count": int(count)
                })
            top_values[col] = items
        return top_values

    def _sanitize_for_json(self, obj: Any) -> Any:
        """
        Recursively cleans a dictionary or list, changing float NaN/Infs to None,
        and casting numpy types to python native types.
        """
        if isinstance(obj, dict):
            return {str(k): self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(v) for v in obj]
        elif isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return self._sanitize_for_json(obj.tolist())
        else:
            return obj
