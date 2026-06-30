import os
import math
import pandas as pd
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

from backend.utils.dataset_manager import dataset_manager
from backend.utils.csv_reader import read_csv_with_encodings

# Initialize FastMCP server
mcp = FastMCP("InsightPilot MCP Server")

def auto_register_existing_datasets():
    """
    Scans the upload directory and automatically registers any datasets found on disk.
    Allows the standalone MCP server process to discover datasets uploaded by the main app.
    """
    if not os.path.exists(dataset_manager.upload_dir):
        return
    for fname in os.listdir(dataset_manager.upload_dir):
        if "_raw_" in fname and fname.endswith(".csv"):
            parts = fname.split("_raw_", 1)
            if len(parts) == 2:
                dataset_id, original_name = parts
                if dataset_id not in dataset_manager._datasets:
                    raw_path = os.path.join(dataset_manager.upload_dir, fname)
                    # Check for a matching clean file
                    clean_filename = f"{dataset_id}_cleaned_{original_name}"
                    clean_path = os.path.join(dataset_manager.upload_dir, clean_filename)
                    if not os.path.exists(clean_path):
                        # Try fallback clean filename
                        cf = fname.replace("_raw_", "_cleaned_")
                        clean_path = os.path.join(dataset_manager.upload_dir, cf)
                    if not os.path.exists(clean_path):
                        clean_path = None
                        
                    dataset_manager._datasets[dataset_id] = {
                        "id": dataset_id,
                        "original_name": original_name,
                        "raw_path": raw_path,
                        "clean_path": clean_path,
                        "status": "cleaned" if clean_path else "raw"
                    }
                    dataset_manager._latest_dataset_id = dataset_id

# Auto register files at startup
auto_register_existing_datasets()

@mcp.tool()
def list_datasets() -> List[Dict[str, Any]]:
    """
    List all available datasets and their metadata (ID, filename, clean path, status).
    """
    auto_register_existing_datasets()
    return list(dataset_manager._datasets.values())

@mcp.tool()
def get_dataset_metadata(dataset_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve the metadata for a specific dataset using its unique ID.
    """
    auto_register_existing_datasets()
    return dataset_manager.get_dataset(dataset_id)

@mcp.tool()
def get_dataset_schema(dataset_id: str) -> Dict[str, Any]:
    """
    Get the columns, inferred data types, and null counts for a specific dataset.
    """
    auto_register_existing_datasets()
    metadata = dataset_manager.get_dataset(dataset_id)
    if not metadata:
        return {"success": False, "error": f"Dataset with ID {dataset_id} not found."}
    
    path = metadata.get("clean_path") or metadata.get("raw_path")
    if not path or not os.path.exists(path):
        return {"success": False, "error": "Dataset file path not found or invalid."}
        
    try:
        df = read_csv_with_encodings(path)
        schema = {}
        for col in df.columns:
            schema[col] = {
                "type": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum())
            }
        return {"success": True, "dataset_id": dataset_id, "schema": schema}
    except Exception as e:
        return {"success": False, "error": f"Failed to read schema: {str(e)}"}

@mcp.tool()
def get_dataset_preview(dataset_id: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get a preview of the first few rows (default 5) of the dataset.
    """
    auto_register_existing_datasets()
    metadata = dataset_manager.get_dataset(dataset_id)
    if not metadata:
        return {"success": False, "error": f"Dataset with ID {dataset_id} not found."}
        
    path = metadata.get("clean_path") or metadata.get("raw_path")
    if not path or not os.path.exists(path):
        return {"success": False, "error": "Dataset file path not found or invalid."}
        
    try:
        df = read_csv_with_encodings(path, nrows=limit)
        preview_data = df.to_dict(orient="records")
        
        # Handle non-serializable objects (like NaN/NaT)
        clean_preview = []
        for row in preview_data:
            clean_row = {}
            for k, v in row.items():
                if isinstance(v, float) and math.isnan(v):
                    clean_row[k] = None
                elif pd.isna(v):
                    clean_row[k] = None
                else:
                    clean_row[k] = v
            clean_preview.append(clean_row)
            
        return {
            "success": True,
            "dataset_id": dataset_id,
            "columns": list(df.columns),
            "preview": clean_preview
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to read preview: {str(e)}"}

if __name__ == "__main__":
    mcp.run()
