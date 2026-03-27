import os
from typing import Dict, Any, List
from google.adk.agents.llm_agent import Agent
from google.cloud import bigquery
from vertexai import agent_engines
import vertexai

# Initialize Vertex AI
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "primary-394719")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
vertexai.init(project=project_id, location=location)

def execute_bigquery_sql(query: str) -> str:
    """
    Executes a BigQuery SQL query and returns the results as a string.
    
    Args:
        query: The SQL query to execute. MUST be a SELECT statement.
        
    Returns:
        A string representation of the query results or an error message.
    """
    print(f"DEBUG: execute_bigquery_sql called with query='{query}'")
    
    # Security check: Block DML/DDL
    forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "MERGE", "GRANT", "REVOKE"]
    query_upper = query.upper()
    for keyword in forbidden_keywords:
        import re
        if re.search(r'\b' + keyword + r'\b', query_upper):
            return f"Error: The query contains a forbidden keyword '{keyword}'. Only SELECT queries are allowed."
            
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "primary-394719")
        client = bigquery.Client(project=project_id)
        
        # Enforce a LIMIT if not present to prevent massive data transfers
        if "LIMIT" not in query_upper:
            query = query + " LIMIT 100"
            
        query_job = client.query(query)
        results = query_job.result()
        
        rows = [dict(row) for row in results]
        
        if not rows:
            return "Query executed successfully. No results found."
            
        import json
        # Convert datetime/date objects to string for JSON serialization
        def default_serializer(obj):
            from datetime import date, datetime
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
            
        return json.dumps(rows, default=default_serializer, indent=2)
        
    except Exception as e:
        return f"Error executing query: {str(e)}"

# Define the schema context for the LLM
schema_context = f"""
You have access to a BigQuery dataset named `financial_services_mock`.
The dataset contains the following tables:

1. `customers`
   - `customer_id` (STRING): Unique identifier for the customer.
   - `first_name` (STRING): Customer's first name.
   - `last_name` (STRING): Customer's last name.
   - `email` (STRING): Customer's email address.
   - `phone` (STRING): Customer's phone number.
   - `address` (STRING): Customer's address.
   - `join_date` (DATE): Date the customer joined.
   - `risk_profile` (STRING): Risk profile (Low, Medium, High).

2. `accounts`
   - `account_id` (STRING): Unique identifier for the account.
   - `customer_id` (STRING): Foreign key to the `customers` table.
   - `account_type` (STRING): Type of account (Checking, Savings, Credit, Investment).
   - `balance` (FLOAT): Current balance of the account.
   - `open_date` (DATE): Date the account was opened.
   - `status` (STRING): Account status (Active, Closed, Suspended).

3. `transactions`
   - `transaction_id` (STRING): Unique identifier for the transaction.
   - `account_id` (STRING): Foreign key to the `accounts` table.
   - `transaction_date` (TIMESTAMP): Date and time of the transaction.
   - `amount` (FLOAT): Transaction amount (positive for deposits, negative for withdrawals/payments).
   - `transaction_type` (STRING): Type of transaction (Deposit, Withdrawal, Transfer, Payment).
   - `merchant_name` (STRING): Name of the merchant (if applicable).
   - `category` (STRING): Transaction category (e.g., Groceries, Entertainment).
   - `status` (STRING): Transaction status (Completed, Pending, Failed).

Use the `execute_bigquery_sql` tool to query these tables to answer user questions.
Always use fully qualified table names in your queries: `{project_id}.financial_services_mock.table_name`.
For example: `SELECT * FROM {project_id}.financial_services_mock.customers LIMIT 10`
"""

root_agent = Agent(
    model='gemini-2.5-flash',
    name='bq_conversational_agent',
    instruction=f"""
    You are an expert Financial Data Analyst. Your goal is to answer questions about the company's financial data.
    
    {schema_context}
    
    **Workflow:**
    1. Analyze the user's question.
    2. Formulate a BigQuery SQL `SELECT` query to retrieve the necessary data.
    3. Use the `execute_bigquery_sql` tool to run the query.
    4. Interpret the results and provide a clear, concise, and helpful answer to the user.
    
    **Rules:**
    - Only use `SELECT` statements. Do not attempt to modify the data.
    - Always explain your findings based on the data retrieved.
    - If a query fails, analyze the error message, correct the SQL, and try again.
    """,
    tools=[execute_bigquery_sql],
)

app = agent_engines.AdkApp(
    agent=root_agent,
    app_name="bq-conversational-agent",
    enable_tracing=True,
)
