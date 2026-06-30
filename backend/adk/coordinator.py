import os
import logging
from typing import Dict, Any
from google import adk
from google.adk.sessions import InMemorySessionService
from google.genai import types

from backend.adk.agent_wrappers import cleaner_node, analyzer_node, visualizer_node, insight_node

logger = logging.getLogger(__name__)

# Define the sequential ADK workflow graph connecting the wrapped nodes
adk_workflow = adk.Workflow(
    name="InsightPilotADKWorkflow",
    edges=[
        ("START", cleaner_node),
        (cleaner_node, analyzer_node),
        (analyzer_node, visualizer_node),
        (visualizer_node, insight_node)
    ]
)

class ADKCoordinator:
    """
    Coordinator Agent that orchestrates the InsightPilot execution pipeline using Google ADK.
    It resolves session states, invokes the workflow node, and reformats the results into the
    exact output expected by the application frontend.
    """
    def __init__(self) -> None:
        self.session_service = InMemorySessionService()

    async def run(self, csv_path: str, user_query: str = None) -> Dict[str, Any]:
        """
        Runs the ADK pipeline:
        CleanerAgent -> AnalyzerAgent -> VisualizerAgent -> InsightAgent (Gemini).
        
        Args:
            csv_path (str): The absolute path to the raw uploaded CSV file.
            user_query (str, optional): Custom prompt/guidelines to tailor reports.

        Returns:
            Dict[str, Any]: Consolidated payload containing all cleaning stats, analytics,
                           charts, and narratives.
        """
        logger.info(f"ADKCoordinator initiating execution pipeline for CSV: {csv_path}")
        
        # 1. Create a session for the ADK execution context
        session = await self.session_service.create_session(app_name="InsightPilot", user_id="system")
        
        # 2. Setup Runner for the workflow
        runner = adk.Runner(
            app_name="InsightPilot",
            node=adk_workflow,
            session_service=self.session_service
        )
        
        # 3. Setup initial state
        state_delta = {
            "file_path": csv_path,
            "user_query": user_query
        }
        
        # 4. Prepare message input containing the file path
        content = types.Content(role='user', parts=[types.Part(text=csv_path)])
        
        # 5. Run the workflow asynchronously
        try:
            async for event in runner.run_async(
                session_id=session.id,
                user_id="system",
                new_message=content,
                state_delta=state_delta
            ):
                logger.debug(f"ADK Workflow event received: {event}")
        except Exception as e:
            logger.error(f"ADK Workflow Runner execution error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"ADK workflow run encountered a critical error: {str(e)}"
            }
            
        # 6. Retrieve the final state from the session service to compile responses
        final_session = await self.session_service.get_session(
            session_id=session.id,
            app_name="InsightPilot",
            user_id="system"
        )
        final_state = final_session.state or {}
        
        cleaning_report_state = final_state.get("cleaning_report", {})
        analysis_results_state = final_state.get("analysis_results", {})
        chart_results_state = final_state.get("chart_results", {})
        insights_state = final_state.get("insights", {})
        
        # Check if the cleaning step succeeded
        if not cleaning_report_state.get("success", False):
            return {
                "success": False,
                "error": f"Data cleaning failed: {cleaning_report_state.get('error', 'Unknown cleaner error')}"
            }
            
        cleaning_report = cleaning_report_state.get("result", {})
        analysis_results = analysis_results_state.get("result", {}) if analysis_results_state.get("success", False) else {}
        chart_results = chart_results_state.get("result", {}) if chart_results_state.get("success", False) else {}
        insights = insights_state.get("result", {}) if insights_state.get("success", False) else {}
        
        # Re-assemble the combined response payload format matching original CoordinatorAgent logic
        combined_response = {
            "success": True,
            "filename": os.path.basename(csv_path),
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
        
        logger.info("ADKCoordinator pipeline execution completed.")
        return combined_response
