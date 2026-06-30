import os
import time
import logging
from typing import Dict, Any
from google import adk

from backend.agents.cleaner.cleaner import CleanerAgent
from backend.agents.analyzer.analyzer import AnalyzerAgent
from backend.agents.visualizer.visualizer import VisualizerAgent
from backend.agents.insight.insight import InsightAgent

logger = logging.getLogger(__name__)

# Reusable helper to run agent logic with standard ADK metrics logging
async def execute_adk_node(node_name: str, action_callable, *args, **kwargs) -> Any:
    """
    Executes the given callable (synchronous or asynchronous), logging
    agent startup, completion, duration, and failures with full tracebacks.
    """
    logger.info(f"ADK Agent [{node_name}] - Execution Started.")
    start_time = time.time()
    try:
        # Check if the callable is a coroutine or normal function
        import inspect
        if inspect.iscoroutinefunction(action_callable):
            res = await action_callable(*args, **kwargs)
        else:
            res = action_callable(*args, **kwargs)
            
        duration = time.time() - start_time
        logger.info(f"ADK Agent [{node_name}] - Execution Completed successfully. Duration: {duration:.4f}s.")
        return res
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"ADK Agent [{node_name}] - Execution Failed after {duration:.4f}s. Error: {str(e)}", exc_info=True)
        raise e

@adk.workflow.node(name="CleanerAgent")
async def cleaner_node(ctx: adk.Context, file_path: str) -> Dict[str, Any]:
    """
    Exposes CleanerAgent as an ADK-compatible node.
    Cleans raw uploaded CSV dataset.
    """
    try:
        cleaner = CleanerAgent(auto_clean=True)
        result = await execute_adk_node("CleanerAgent", cleaner.clean, file_path)
        ctx.state["cleaning_report"] = {"success": True, "result": result}
        ctx.state["clean_file_path"] = result.get("clean_file_path")
        return {"success": True, "result": result}
    except Exception as e:
        err_dict = {"success": False, "error": str(e)}
        ctx.state["cleaning_report"] = err_dict
        return err_dict

@adk.workflow.node(name="AnalyzerAgent")
async def analyzer_node(ctx: adk.Context, cleaning_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exposes AnalyzerAgent as an ADK-compatible node.
    Performs descriptive statistics and correlations.
    """
    # Check if cleaner failed
    if not cleaning_report.get("success", True):
        err_dict = {"success": False, "error": "Skipped due to cleaner failure."}
        ctx.state["analysis_results"] = err_dict
        return err_dict

    try:
        analyzer = AnalyzerAgent()
        clean_file_path = ctx.state.get("clean_file_path")
        user_query = ctx.state.get("user_query")
        
        # Fallback to check input if not found in state
        if not clean_file_path and cleaning_report:
            clean_file_path = cleaning_report.get("result", {}).get("clean_file_path")

        if not clean_file_path:
            raise ValueError("Cannot run AnalyzerAgent: No valid cleaned file path found.")

        result = await execute_adk_node("AnalyzerAgent", analyzer.analyze, clean_file_path, query=user_query)
        ctx.state["analysis_results"] = {"success": True, "result": result}
        return {"success": True, "result": result}
    except Exception as e:
        err_dict = {"success": False, "error": str(e)}
        ctx.state["analysis_results"] = err_dict
        return err_dict

@adk.workflow.node(name="VisualizerAgent")
async def visualizer_node(ctx: adk.Context, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exposes VisualizerAgent as an ADK-compatible node.
    Generates suitable Plotly charts.
    """
    clean_file_path = ctx.state.get("clean_file_path")
    
    # Check if cleaner/analyzer failed
    if not clean_file_path:
        err_dict = {"success": False, "error": "Skipped due to missing cleaned file."}
        ctx.state["chart_results"] = err_dict
        return err_dict

    try:
        visualizer = VisualizerAgent()
        result = await execute_adk_node("VisualizerAgent", visualizer.generate_charts, clean_file_path)
        ctx.state["chart_results"] = {"success": True, "result": result}
        return {"success": True, "result": result}
    except Exception as e:
        err_dict = {"success": False, "error": str(e)}
        ctx.state["chart_results"] = err_dict
        return err_dict

@adk.workflow.node(name="InsightAgent")
async def insight_node(ctx: adk.Context, chart_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exposes InsightAgent as an ADK-compatible node.
    Delegates natural language insight generation to Gemini.
    """
    analysis_state = ctx.state.get("analysis_results", {})
    cleaning_state = ctx.state.get("cleaning_report", {})
    
    # Check if cleaner/analyzer failed
    if not analysis_state.get("success", False) or not cleaning_state.get("success", False):
        err_dict = {"success": False, "error": "Skipped due to upstream failure."}
        ctx.state["insights"] = err_dict
        return err_dict

    try:
        insight = InsightAgent()
        analysis_results = analysis_state.get("result")
        cleaning_report = cleaning_state.get("result")
        
        if not analysis_results or not cleaning_report:
            raise ValueError("Cannot run InsightAgent: Missing analysis results or cleaning report in session state.")

        result = await execute_adk_node("InsightAgent", insight.generate_narratives, analysis_results, cleaning_report)
        ctx.state["insights"] = {"success": True, "result": result}
        return {"success": True, "result": result}
    except Exception as e:
        err_dict = {"success": False, "error": str(e)}
        ctx.state["insights"] = err_dict
        return err_dict
