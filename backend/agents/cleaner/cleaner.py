import os
import pandas as pd
import numpy as np
import logging
from backend.utils.csv_reader import read_csv_with_encodings
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CleanerAgent:
    """
    CleanerAgent processes raw uploaded CSV files to prepare them for analysis.
    It removes duplicates, detects/summarizes missing values, infers column datatypes,
    and returns a structured cleaning report along with a clean file path.
    """

    def __init__(self, auto_clean: bool = True) -> None:
        """
        Initializes the CleanerAgent.

        Args:
            auto_clean (bool): Whether to run cleaning actions automatically.
        """
        self.auto_clean = auto_clean

    def clean(self, file_path: str) -> Dict[str, Any]:
        """
        Loads the file, runs deduplication, missing value checks, datatype inference,
        and saves a cleaned copy of the file.

        Args:
            file_path (str): The absolute path to the raw CSV file.

        Returns:
            Dict[str, Any]: Cleaning report summary and cleaned file path.
        """
        logger.info(f"CleanerAgent starting on file: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Read dataset
            df = read_csv_with_encodings(file_path)
            original_row_count = len(df)
            original_col_count = len(df.columns)

            # 1. Detect and summarize missing values
            missing_values = self.detect_missing_values(df)

            # 2. Infer data types
            inferred_types = self.infer_data_types(df)

            # 3. Remove duplicates
            df_cleaned, duplicates_removed = self.remove_duplicates(df)

            # Define path for cleaned file
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            clean_filename = base_name.replace("_raw_", "_cleaned_")
            # If name hasn't changed, append _cleaned
            if clean_filename == base_name:
                name, ext = os.path.splitext(base_name)
                clean_filename = f"{name}_cleaned{ext}"

            clean_file_path = os.path.join(dir_name, clean_filename)
            
            # Save cleaned CSV
            df_cleaned.to_csv(clean_file_path, index=False)
            logger.info(f"CleanerAgent successfully saved cleaned file to {clean_file_path}")

            # 4. Formulate cleaning report
            report = {
                "original_row_count": original_row_count,
                "original_col_count": original_col_count,
                "cleaned_row_count": len(df_cleaned),
                "duplicates_removed": duplicates_removed,
                "missing_values_summary": missing_values,
                "inferred_data_types": inferred_types,
                "clean_file_path": clean_file_path
            }
            return report

        except Exception as e:
            logger.error(f"Error occurred during cleaning process: {str(e)}")
            raise e

    def remove_duplicates(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        """
        Detects and removes duplicate rows from the DataFrame.
        """
        initial_count = len(df)
        df_cleaned = df.drop_duplicates()
        duplicates_removed = initial_count - len(df_cleaned)
        logger.info(f"Removed {duplicates_removed} duplicate rows.")
        return df_cleaned, duplicates_removed

    def detect_missing_values(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Detects count of missing values per column.
        """
        null_counts = df.isnull().sum().to_dict()
        # Convert keys to string representation for JSON compatibility
        return {str(col): int(count) for col, count in null_counts.items()}

    def infer_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Infers column data types into 'numeric', 'datetime', 'categorical', or 'text'.
        """
        inferred = {}
        for col in df.columns:
            # Check if column is numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                inferred[col] = "numeric"
            else:
                # Check if it could be datetime
                try:
                    # Sample non-null values to test datetime conversion
                    non_null_samples = df[col].dropna().head(10)
                    if len(non_null_samples) > 0:
                        # Attempt conversion, reject if integers or short strings are false positives
                        parsed = pd.to_datetime(non_null_samples, errors='raise')
                        inferred[col] = "datetime"
                    else:
                        inferred[col] = "text"
                except (ValueError, TypeError):
                    # Check if categorical (few unique values compared to row count)
                    unique_count = df[col].nunique()
                    total_count = len(df)
                    if total_count > 0 and (unique_count / total_count < 0.15 or unique_count < 15):
                        inferred[col] = "categorical"
                    else:
                        inferred[col] = "text"
        return inferred
