import os
import asyncio
from agent import app

os.environ["GOOGLE_CLOUD_PROJECT"] = "primary-394719"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

async def run_test():
    print("Testing BQ Conversational Agent...")
    question = "What is the total balance of all checking accounts?"
    print(f"Question: {question}")
    
    try:
        await app.async_create_session(session_id="test_session", user_id="test_user")
    except Exception as e:
        pass # Session might already exist

    try:
        response_stream = app.async_stream_query(
            message=question,
            user_id="test_user",
            session_id="test_session"
        )
        print("\nResponse:")
        async for chunk in response_stream:
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"Local query failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
