import os
import sys
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add backend directory to path so we can import dataset_manager
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.utils.dataset_manager import dataset_manager

async def main():
    print("==================================================")
    print("      InsightPilot AI - MCP Server Demo Run")
    print("==================================================\n")

    # 1. Ensure a mock dataset exists on disk so the tools can return data
    print("1. Preparing a mock dataset in temp_uploads...")
    mock_csv_content = (
        "TransactionID,Date,Customer,Amount,Region\n"
        "TX101,2026-06-01,Acme Corp,150.50,North\n"
        "TX102,2026-06-02,Beta LLC,250.00,West\n"
        "TX103,2026-06-03,Acme Corp,350.25,East\n"
        "TX104,2026-06-04,Gamma Inc,,South\n"
    )
    # Save the mock dataset using DatasetManager (this writes the file to disk)
    dataset_id = dataset_manager.save_dataset(
        filename="mock_mcp_data.csv",
        content_bytes=mock_csv_content.encode("utf-8")
    )
    print(f"Mock dataset created with ID: {dataset_id}\n")

    # 2. Configure server parameters to launch our server.py
    # We use sys.executable to ensure we launch using the same virtual env python interpreter
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "backend.mcp.server"],
        env=os.environ.copy()
    )

    print("2. Connecting to MCP Server via stdio transport...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize connection
            await session.initialize()
            print("Successfully initialized Client Session!\n")

            # Discover available tools
            tools = await session.list_tools()
            print("Available Tools on Server:")
            for t in tools.tools:
                print(f" - {t.name}: {t.description}")
            print()

            # Test 1: list_datasets
            print("--------------------------------------------------")
            print("Test 1: Calling list_datasets()...")
            res_list = await session.call_tool("list_datasets", arguments={})
            print("Response text:")
            print(res_list.content[0].text)
            print()

            # Test 2: get_dataset_metadata
            print("--------------------------------------------------")
            print(f"Test 2: Calling get_dataset_metadata(dataset_id='{dataset_id}')...")
            res_meta = await session.call_tool("get_dataset_metadata", arguments={"dataset_id": dataset_id})
            print("Response text:")
            print(res_meta.content[0].text)
            print()

            # Test 3: get_dataset_schema
            print("--------------------------------------------------")
            print(f"Test 3: Calling get_dataset_schema(dataset_id='{dataset_id}')...")
            res_schema = await session.call_tool("get_dataset_schema", arguments={"dataset_id": dataset_id})
            print("Response text:")
            print(res_schema.content[0].text)
            print()

            # Test 4: get_dataset_preview
            print("--------------------------------------------------")
            print(f"Test 4: Calling get_dataset_preview(dataset_id='{dataset_id}', limit=3)...")
            res_preview = await session.call_tool("get_dataset_preview", arguments={"dataset_id": dataset_id, "limit": 3})
            print("Response text:")
            print(res_preview.content[0].text)
            print()

    print("==================================================")
    print("            MCP Demo Run Finished")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
