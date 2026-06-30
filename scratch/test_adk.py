import os
import asyncio
import logging
from dotenv import load_dotenv
from google import adk
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    agent = adk.Agent(
        name="hello_agent",
        instruction="Tell a short greeting.",
    )
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name="test_app", user_id="user1")
    runner = adk.Runner(
        app_name="test_app",
        agent=agent,
        session_service=session_service
    )
    
    content = types.Content(role='user', parts=[types.Part(text="Hello")])
    async for event in runner.run_async(session_id=session.id, user_id="user1", new_message=content):
        print("Event:", event)

if __name__ == "__main__":
    asyncio.run(main())
