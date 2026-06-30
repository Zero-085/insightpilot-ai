import asyncio
from google import adk
from google.adk.sessions import InMemorySessionService

@adk.workflow.node(name="cleaner")
async def cleaner_node(ctx: adk.Context, node_input: str) -> dict:
    print("Cleaner received:", node_input)
    return {"clean_file": node_input + "_cleaned"}

@adk.workflow.node(name="analyzer")
async def analyzer_node(ctx: adk.Context, node_input: dict) -> dict:
    print("Analyzer received:", node_input)
    return {"analysis": "looks good"}

async def main():
    # Define workflow edges
    workflow = adk.Workflow(
        name="root_workflow",
        edges=[
            ("START", cleaner_node),
            (cleaner_node, analyzer_node)
        ]
    )
    
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="user1")
    runner = adk.Runner(
        app_name="test_app",
        node=workflow,
        session_service=session_service
    )
    
    from google.genai import types
    content = types.Content(role='user', parts=[types.Part(text="my_raw_file.csv")])
    async for event in runner.run_async(session_id=session.id, user_id="user1", new_message=content):
        print("Event:", event)

if __name__ == "__main__":
    asyncio.run(main())
