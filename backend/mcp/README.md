# Model Context Protocol (MCP) Server for InsightPilot AI

This folder implements a lightweight **Model Context Protocol (MCP)** server for the InsightPilot AI application. 

## Why MCP is Used
The Model Context Protocol (MCP) provides a standardized, open protocol for exposing data and services to LLMs (Large Language Models). By implementing an MCP server, InsightPilot AI enables any MCP-compatible LLM agent to securely discover, inspect, and analyze datasets directly via standard tools without requiring custom client integrations.

## Available Tools

The MCP server exposes the following 4 tools (reusing the existing `DatasetManager` and `read_csv_with_encodings` code-base):

1. **`list_datasets()`**
   - **Description**: List all available datasets and their metadata (ID, original filename, clean path, status).
   
2. **`get_dataset_metadata(dataset_id: str)`**
   - **Description**: Retrieve the detailed metadata for a specific dataset using its unique ID.
   
3. **`get_dataset_schema(dataset_id: str)`**
   - **Description**: Get the column schemas, datatypes, and null counts for a specific dataset. Automatically handles fallback encoding detection.
   
4. **`get_dataset_preview(dataset_id: str, limit: int = 5)`**
   - **Description**: Get a preview of the first few rows of a dataset. Gracefully handles non-JSON-serializable values like `NaN` and `NaT`.

## How to Run the Demo

You can run the standalone verification script to launch the server as a subprocess, establish a connection using standard input/output (stdio) transport, and invoke every tool sequentially:

```bash
python run_mcp_demo.py
```
