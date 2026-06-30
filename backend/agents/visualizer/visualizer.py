import os
import json
import pandas as pd
import numpy as np
import logging
from backend.utils.csv_reader import read_csv_with_encodings
import plotly.express as px
import plotly.io as pio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VisualizerAgent:
    """
    VisualizerAgent handles chart generation based on analysis results.
    It automatically produces Plotly figures (histogram, bar chart, line chart, pie chart)
    tailored to the dataset attributes and returns their JSON-serializable dictionaries.
    """

    def __init__(self, theme: str = "plotly_white") -> None:
        """
        Initializes the VisualizerAgent.

        Args:
            theme (str): Plotly template theme to use.
        """
        self.theme = theme

    def generate_charts(self, file_path: str) -> Dict[str, Any]:
        """
        Generates suitable Plotly figures from the clean dataset.

        Args:
            file_path (str): The absolute path to the clean CSV file.

        Returns:
            Dict[str, Any]: Dictionaries containing Plotly chart configurations.
        """
        logger.info(f"VisualizerAgent starting on file: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            df = read_csv_with_encodings(file_path)
            
            # Select column types
            numeric_cols = []
            categorical_cols = []

            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    numeric_cols.append(col)
                elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                    categorical_cols.append(col)

            # Identify datetime column
            date_col = self._detect_date_column(df)

            charts = {
                "histogram": None,
                "bar_chart": None,
                "line_chart": None,
                "pie_chart": None
            }

            # Helper function to convert a Plotly figure to a pure JSON-serializable dict
            def fig_to_pure_json(fig) -> dict:
                return json.loads(pio.to_json(fig))

            # 1. Histogram: Distribution of the first numeric column
            if numeric_cols:
                num_col = numeric_cols[0]
                fig_hist = px.histogram(
                    df, 
                    x=num_col, 
                    title=f"Distribution of {num_col}",
                    template=self.theme,
                    labels={num_col: num_col}
                )
                fig_hist.update_layout(bargap=0.05)
                charts["histogram"] = fig_to_pure_json(fig_hist)

            # 2. Bar Chart: Value counts of the first categorical column
            if categorical_cols:
                cat_col = categorical_cols[0]
                counts = df[cat_col].value_counts().reset_index()
                counts.columns = [cat_col, "count"]
                # Top 15 to keep it clean
                counts = counts.head(15)
                fig_bar = px.bar(
                    counts, 
                    x=cat_col, 
                    y="count", 
                    title=f"Distribution of {cat_col} (Top 15)",
                    template=self.theme
                )
                charts["bar_chart"] = fig_to_pure_json(fig_bar)

            # 3. Line Chart: If datetime column exists and numeric column exists
            if date_col and numeric_cols:
                # Pick numeric column (preferably not date index/ID)
                filtered_nums = [c for c in numeric_cols if "id" not in c.lower() and c != date_col]
                num_col_for_line = filtered_nums[0] if filtered_nums else numeric_cols[0]
                
                # Copy and convert date
                df_temp = df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                df_temp = df_temp.dropna(subset=[date_col])
                df_temp = df_temp.sort_values(by=date_col)
                
                # Group by date to aggregate sums
                df_grouped = df_temp.groupby(date_col)[num_col_for_line].sum().reset_index()
                
                fig_line = px.line(
                    df_grouped, 
                    x=date_col, 
                    y=num_col_for_line, 
                    title=f"Trend of {num_col_for_line} over Time",
                    template=self.theme
                )
                charts["line_chart"] = fig_to_pure_json(fig_line)

            # 4. Pie Chart: If a categorical column is suitable (unique values between 2 and 10)
            suitable_pie_col = None
            for col in categorical_cols:
                unique_cnt = df[col].nunique()
                if 2 <= unique_cnt <= 10:
                    suitable_pie_col = col
                    break
            
            if suitable_pie_col:
                pie_counts = df[suitable_pie_col].value_counts().reset_index()
                pie_counts.columns = [suitable_pie_col, "count"]
                fig_pie = px.pie(
                    pie_counts, 
                    names=suitable_pie_col, 
                    values="count", 
                    title=f"Market Share of {suitable_pie_col}",
                    template=self.theme
                )
                charts["pie_chart"] = fig_to_pure_json(fig_pie)

            return charts

        except Exception as e:
            logger.error(f"Error occurred during chart generation: {str(e)}")
            raise e

    def _detect_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Attempts to detect the primary datetime column.
        """
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
        # If not explicitly typed, look at strings containing date keywords
        for col in df.columns:
            name_lower = col.lower()
            if any(k in name_lower for k in ["date", "time", "timestamp", "day", "month"]):
                try:
                    # Test parsing the first few rows
                    pd.to_datetime(df[col].dropna().head(5), errors='raise')
                    return col
                except Exception:
                    continue
        return None
