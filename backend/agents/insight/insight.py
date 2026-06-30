from typing import Dict, Any
from backend.services.gemini_service import GeminiService

class InsightAgent:
    """
    InsightAgent synthesizes analytical metrics, anomalies, and chart data
    to generate natural language summaries, business observations, and recommended actions.
    It writes key findings in plain English by delegating content generation
    to a dedicated GeminiService.
    """

    def __init__(self, tone: str = "professional") -> None:
        """
        Initializes the InsightAgent.

        Args:
            tone (str): Communication style tone (e.g. 'professional', 'concise', 'executive').
        """
        self.tone = tone
        # Instantiate the Gemini service
        self.gemini_service = GeminiService()

    def generate_narratives(self, analysis_results: Dict[str, Any], cleaning_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes results into narrative insights by calling GeminiService.
        Falls back gracefully if the API fails or is unconfigured.

        Args:
            analysis_results (dict): Calculated metrics and correlations from AnalyzerAgent.
            cleaning_report (dict): Anomalies or actions taken by CleanerAgent.

        Returns:
            dict: Structured observations, key action items, and text explanations.
        """
        return self.gemini_service.generate_insights(analysis_results, cleaning_report)
