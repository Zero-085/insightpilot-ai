import logging
from typing import Dict, Any

from backend.agents.cleaner.cleaner import CleanerAgent
from backend.agents.analyzer.analyzer import AnalyzerAgent
from backend.agents.visualizer.visualizer import VisualizerAgent
from backend.agents.insight.insight import InsightAgent

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    """
    CoordinatorAgent coordinates the multi-agent execution pipeline.
    It takes raw CSV paths, delegates tasks to appropriate downstream agents,
    and aggregates their outputs into a final consolidated response.
    It does not perform data analysis or calculations directly.
    """

    def __init__(self, config: dict = None) -> None:
        """
        Initializes the CoordinatorAgent and instances of downstream agents.

        Args:
            config (dict, optional): Configuration settings for agent orchestration.
        """
        self.config = config or {}
        # Instantiate child agents
        self.cleaner = CleanerAgent(auto_clean=True)
        self.analyzer = AnalyzerAgent(calculation_depth="standard")
        self.visualizer = VisualizerAgent(theme="plotly_white")
        self.insight = InsightAgent(tone="professional")

    def run(self, csv_path: str, user_query: str = None) -> Dict[str, Any]:
        """
        Coordinates the multi-agent workflow:
        CleanerAgent -> AnalyzerAgent -> VisualizerAgent -> InsightAgent.

        Args:
            csv_path (str): The absolute path to the raw uploaded CSV file.
            user_query (str, optional): Custom prompt/guidelines to tailor reports.

        Returns:
            Dict[str, Any]: Consolidated payload containing all cleaning stats, analytics,
                           charts, and narratives.
        """
        logger.info(f"CoordinatorAgent running pipeline for CSV: {csv_path}")
        
        try:
            # 1. Clean the dataset
            cleaning_report = self.cleaner.clean(csv_path)
            clean_file_path = cleaning_report.get("clean_file_path")
            
            if not clean_file_path:
                raise ValueError("CleanerAgent did not return a valid cleaned file path.")

            # 2. Analyze the dataset
            analysis_results = self.analyzer.analyze(clean_file_path, query=user_query)

            # 3. Generate visual chart specifications
            chart_results = self.visualizer.generate_charts(clean_file_path)

            # 4. Synthesize plain English narrative insights
            insights = self.insight.generate_narratives(analysis_results, cleaning_report)

            # 5. Aggregate and return results
            combined_response = {
                "success": True,
                "filename": cleaning_report.get("original_name"),
                "cleaning_report": {
                    "original_row_count": cleaning_report.get("original_row_count"),
                    "cleaned_row_count": cleaning_report.get("cleaned_row_count"),
                    "duplicates_removed": cleaning_report.get("duplicates_removed"),
                    "missing_values_summary": cleaning_report.get("missing_values_summary"),
                    "inferred_data_types": cleaning_report.get("inferred_data_types")
                },
                "analysis": analysis_results,
                "charts": chart_results,
                "insights": insights
            }
            
            logger.info("CoordinatorAgent pipeline completed successfully.")
            return combined_response

        except Exception as e:
            logger.error(f"CoordinatorAgent workflow failure: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
