import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent import app

async def run_test_cases():
    print("Testing BQ Conversational Agent with Assertions...")
    
    test_cases = [
        {
            "query": "what merchants are in the system?",
            "expected_keywords": ["Walmart"]
        },
        {
            "query": "How many customers have made a transaction at Target?",
            "expected_keywords": ["32"]
        },
        {
            "query": "can you correlate that with the risk profile and produce a summary?",
            "expected_keywords": ["Medium", "12 customers", "High", "12 customers", "Low", "8 customers"]
        },
        {
            "query": "Rank customers based on their account balances.",
            "expected_keywords": ["Patricia Williams", "126,527"]
        },
        {
            "query": "Are there really two customers with the name 'Patricia Williams'? Provide their customer_id and a total balance (round to 1000s as in '34K')?",
            "expected_keywords": ["Yes", "CUST0014", "CUST0022", "K"]
        }
    ]
    
    session_id = "automated_test_session"
    user_id = "test_user"
    
    try:
        await app.async_create_session(session_id=session_id, user_id=user_id)
    except Exception as e:
        pass # Session might already exist
    
    passed_tests = 0
    failed_tests = 0
    failed_cases = []
    passed_cases = []
    
    for i, case in enumerate(test_cases):
        query = case["query"]
        expected_keywords = case["expected_keywords"]
        
        print(f"\\n[{i+1}/{len(test_cases)}] User: {query}")
        
        try:
            response_stream = app.async_stream_query(
                message=query,
                user_id=user_id,
                session_id=session_id
            )
            
            full_response = ""
            print("Agent: ", end="")
            async for chunk in response_stream:
                print(chunk, end="", flush=True)
                full_response += str(chunk)
            print()
            
            # Check assertions
            missing_keywords = [kw for kw in expected_keywords if kw.lower() not in full_response.lower()]
            
            if missing_keywords:
                print(f"❌ FAILED: Missing expected keywords: {missing_keywords}")
                failed_cases.append({
                    "query": query,
                    "response": full_response,
                    "missing": missing_keywords
                })
                failed_tests += 1
            else:
                print(f"✅ PASSED")
                passed_cases.append({
                    "query": query,
                    "response": full_response,
                    "matched": expected_keywords
                })
                passed_tests += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed_cases.append({
                "query": query,
                "response": f"Error: {e}",
                "missing": expected_keywords
            })
            failed_tests += 1
            
    print(f"\n--- Test Summary ---")
    print(f"Passed: {passed_tests}/{len(test_cases)}")
    print(f"Failed: {failed_tests}/{len(test_cases)}")
    
    if passed_cases:
        print("\n--- Passed Test Details ---")
        for pc in passed_cases:
            print(f"User: {pc['query']}")
            print(f"Matched: {pc['matched']}")
            print(f"Agent Response (first 200 chars): {pc['response'][:200]}...\n")
            
    if failed_cases:
        print(f"\n--- Failed Test Details ---")
        for fc in failed_cases:
            print(f"User: {fc['query']}")
            print(f"Missing: {fc['missing']}")
            print(f"Agent Response (first 200 chars): {fc['response'][:200]}...\n")
            
    if failed_tests > 0:
        exit(1)

if __name__ == "__main__":
    asyncio.run(run_test_cases())
