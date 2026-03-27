import os
import asyncio
from agent import app

async def run_test_cases():
    print("Testing BQ Conversational Agent with Assertions...")
    
    test_cases = [
        {
            "query": "what data about customers do you have?",
            "expected_keywords": ["customer_id", "first_name", "risk_profile"]
        },
        {
            "query": "show me all customers with low risk?",
            "expected_keywords": ["14", "customers"]
        },
        {
            "query": "what are their emails?",
            "expected_keywords": ["14", "email addresses"]
        },
        {
            "query": "what are their balances?",
            "expected_keywords": ["balances"]
        },
        {
            "query": "show me a list of all emails along with the all of their accounts and their balances",
            "expected_keywords": ["emails", "accounts", "balances"]
        },
        {
            "query": "Can you tell me about the dataset?",
            "expected_keywords": ["customers", "accounts", "transactions"]
        },
        {
            "query": "What are some interesting questions you can answer?",
            "expected_keywords": ["?"]
        },
        {
            "query": "Can I see the email addresses of customers who have made a transaction with a specific merchant?",
            "expected_keywords": ["Yes", "merchant"]
        },
        {
            "query": "what merchants are in the system?",
            "expected_keywords": ["merchants"]
        },
        {
            "query": "lets say 'Target'",
            "expected_keywords": ["32", "email addresses"]
        },
        {
            "query": "can you correlate that with the risk profile and produce a summary?",
            "expected_keywords": ["Medium", "High", "Low"]
        },
        {
            "query": "are you able to use analytical functions?",
            "expected_keywords": ["Yes", "average"]
        },
        {
            "query": "Rank customers based on their account balances.",
            "expected_keywords": ["Patricia Williams"]
        },
        {
            "query": "what SQL did you use for this?",
            "expected_keywords": ["SQL"]
        },
        {
            "query": "Are there really two customers with the name 'Patricia Williams'?",
            "expected_keywords": ["Yes", "two"]
        },
        {
            "query": "what is the SQL you used to figure this out?",
            "expected_keywords": ["don't", "SQL"]
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
                failed_tests += 1
            else:
                print(f"✅ PASSED")
                passed_tests += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed_tests += 1
            
    print(f"\\n--- Test Summary ---")
    print(f"Passed: {passed_tests}/{len(test_cases)}")
    print(f"Failed: {failed_tests}/{len(test_cases)}")
    
    if failed_tests > 0:
        exit(1)

if __name__ == "__main__":
    asyncio.run(run_test_cases())
