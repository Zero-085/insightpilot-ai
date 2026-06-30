import os
import asyncio
import json
import logging
from dotenv import load_dotenv

# Configure logging to display INFO logs including our ADK startup/completion logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Load environment variables (such as GEMINI_API_KEY)
    load_dotenv()
    
    # Import the ADK coordinator
    from backend.adk.coordinator import ADKCoordinator
    
    csv_path = os.path.abspath("mock_dashboard_data.csv")
    user_query = "Summarize the transactions and tell me if there are any interesting trends or region distributions."
    
    print("\n==================================================")
    print("      InsightPilot AI - Google ADK Demo Run")
    print("==================================================\n")
    
    print(f"Dataset path: {csv_path}")
    print(f"User Query: {user_query}\n")
    
    coordinator = ADKCoordinator()
    
    # Run the orchestrator workflow
    response = await coordinator.run(csv_path=csv_path, user_query=user_query)
    
    print("\n==================================================")
    print("              ADK Execution Finished")
    print("==================================================\n")
    
    if response.get("success", False):
        print("Success! Combined Output Structure:\n")
        # Print a formatted version of the final response
        print(json.dumps(response, indent=2, default=str)[:3000])
        print("\n... [Output Truncated for Readability] ...")
    else:
        print(f"Pipeline Run Failed: {response.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
