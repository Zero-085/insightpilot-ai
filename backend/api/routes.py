import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional, Dict, Any

from backend.utils.dataset_manager import dataset_manager
from backend.agents.coordinator.coordinator import CoordinatorAgent

logger = logging.getLogger(__name__)
router = APIRouter()

# Global cache to store coordinator results and prevent double computations
# Structure: {dataset_id: combined_coordinator_response}
_pipeline_cache: Dict[str, Dict[str, Any]] = {}

def _run_pipeline_for_dataset(dataset_id: str) -> Dict[str, Any]:
    """
    Helper function to load dataset details, execute CoordinatorAgent, and cache results.
    """
    if dataset_id in _pipeline_cache:
        logger.info(f"Returning cached pipeline results for dataset: {dataset_id}")
        return _pipeline_cache[dataset_id]

    meta = dataset_manager.get_dataset(dataset_id)
    if not meta:
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset with ID '{dataset_id}' not found."
        )

    raw_path = meta.get("raw_path")
    if not raw_path or not os.path.exists(raw_path):
        raise HTTPException(
            status_code=404, 
            detail="Raw dataset file not found on disk."
        )

    # Initialize coordinator and run the multi-agent pipeline
    coordinator = CoordinatorAgent()
    result = coordinator.run(raw_path)

    if not result.get("success", False):
        logger.error(f"Pipeline execution failed: {result.get('error')}")
        raise HTTPException(
            status_code=500,
            detail=f"Data pipeline execution error: {result.get('error')}"
        )

    # Update cleaned path in dataset manager
    clean_path = result.get("cleaning_report", {}).get("clean_file_path")
    if clean_path:
        dataset_manager.set_clean_path(dataset_id, clean_path)

    # Cache results
    _pipeline_cache[dataset_id] = result
    return result

import os

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Uploads a CSV file, validates its format, and stores it temporarily.
    """
    logger.info(f"Received file upload request: {file.filename}")
    
    # 1. Validate file extension
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV files (.csv) are accepted."
        )

    try:
        content = await file.read()
        # 2. Save and register dataset
        dataset_id = dataset_manager.save_dataset(file.filename, content)
        logger.info(f"CSV uploaded successfully. Registered dataset ID: {dataset_id}")
        
        return {
            "success": True,
            "dataset_id": dataset_id,
            "filename": file.filename,
            "message": "File uploaded and validated successfully."
        }
    except ValueError as val_err:
        logger.warning(f"Validation failure during upload: {str(val_err)}")
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        logger.error(f"Unexpected error uploading file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while uploading the file: {str(e)}"
        )

@router.get("/analysis")
def get_analysis(dataset_id: Optional[str] = Query(None, description="The unique ID of the dataset")) -> Dict[str, Any]:
    """
    Runs the multi-agent pipeline and returns cleaning report, structured statistics, and insights.
    """
    # Fallback to latest uploaded if no ID provided
    target_id = dataset_id
    if not target_id:
        latest = dataset_manager.get_dataset()
        if not latest:
            raise HTTPException(
                status_code=400,
                detail="No datasets have been uploaded yet. Please upload a CSV first."
            )
        target_id = latest["id"]

    logger.info(f"Requesting analysis for dataset: {target_id}")
    pipeline_res = _run_pipeline_for_dataset(target_id)
    
    return {
        "success": True,
        "dataset_id": target_id,
        "filename": pipeline_res.get("filename"),
        "cleaning_report": pipeline_res.get("cleaning_report"),
        "analysis": pipeline_res.get("analysis"),
        "insights": pipeline_res.get("insights")
    }

@router.get("/charts")
def get_charts(dataset_id: Optional[str] = Query(None, description="The unique ID of the dataset")) -> Dict[str, Any]:
    """
    Generates and returns Plotly chart JSON specifications for rendering.
    """
    target_id = dataset_id
    if not target_id:
        latest = dataset_manager.get_dataset()
        if not latest:
            raise HTTPException(
                status_code=400,
                detail="No datasets have been uploaded yet. Please upload a CSV first."
            )
        target_id = latest["id"]

    logger.info(f"Requesting charts for dataset: {target_id}")
    pipeline_res = _run_pipeline_for_dataset(target_id)

    return {
        "success": True,
        "dataset_id": target_id,
        "charts": pipeline_res.get("charts")
    }

@router.get("/health")
def get_health() -> Dict[str, Any]:
    """
    Simple health status check of the BI backend.
    """
    return {
        "status": "healthy",
        "service": "InsightPilot AI Core API",
        "pipeline_cache_size": len(_pipeline_cache)
    }
