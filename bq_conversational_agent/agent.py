import os
from typing import Dict, Any, List
from google.adk.agents.llm_agent import Agent
from vertexai import agent_engines
import vertexai
import google.cloud.geminidataanalytics as geminidataanalytics
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

# Load environment variables from .env file
load_dotenv()

# Initialize Vertex AI
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
dataset_id = os.environ.get("BQ_DATASET_ID", "financial_services_mock")

if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set. Please check your .env file.")

vertexai.init(project=project_id, location=location)

def ask_conversational_analytics(query: str, tool_context=None) -> str:
    """
    Asks a standalone question about the financial data using the Conversational Analytics API.
    
    Args:
        query: The natural language question to ask. MUST be a standalone question with all necessary context.
        tool_context: Optional context passed by ADK containing user state (OAuth tokens).
        
    Returns:
        The answer from the Conversational Analytics API.
    """
    print(f"DEBUG: ask_conversational_analytics called with query='{query}'")
    
    access_token = None
    if tool_context and hasattr(tool_context, "state"):
        access_token = tool_context.state.get("temp:bq_auth_v7") or tool_context.state.get("bq_auth_v7")
        
    if not access_token:
        print("ERROR: No user OAuth token found. Access denied.")
        return "Authentication Error: You do not have valid credentials to access this agent. Please click 'Authorize' to log in."

    print("DEBUG: Using user OAuth token for BigQuery access.")
    creds = Credentials(access_token)
    client = geminidataanalytics.DataChatServiceClient(credentials=creds)
    inline_context = geminidataanalytics.Context()
    
    # Connect to BigQuery tables. You may want to add some code to make this
    # more dynamic, e.g. by querying the BigQuery API to get the list of tables.
    tables = ["customers", "accounts", "transactions", "loans", "support_tickets", "portfolios"]
    table_refs = []
    for table in tables:
        bq_ref = geminidataanalytics.BigQueryTableReference()
        bq_ref.project_id = project_id
        bq_ref.dataset_id = dataset_id
        bq_ref.table_id = table
        table_refs.append(bq_ref)
        
    datasource_references = geminidataanalytics.DatasourceReferences()
    datasource_references.bq.table_references = table_refs
    inline_context.datasource_references = datasource_references
    
    message = geminidataanalytics.Message()
    message.user_message.text = query
    
    request = geminidataanalytics.ChatRequest(
        parent=f"projects/{project_id}/locations/{location}",
        messages=[message],
        inline_context=inline_context
    )
    
    try:
        stream = client.chat(request=request)
        final_answer = ""
        for response in stream:
            if response.system_message and response.system_message.text:
                if response.system_message.text.text_type == geminidataanalytics.TextMessage.TextType.FINAL_RESPONSE:
                    for part in response.system_message.text.parts:
                        final_answer += part + "\n"
        
        if not final_answer:
            return "The API did not return a final text response. It might have returned a chart or data table."
            
        return final_answer.strip()
    except Exception as e:
        return f"Error from Conversational Analytics API: {str(e)}"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='bq_conversational_agent',
    instruction="""
    You are an expert Financial Data Analyst. Your goal is to answer questions about the company's financial data.
    
    You have access to a BigQuery dataset named `financial_services_mock` containing the following tables:
    - `customers`: Customer profiles (customer_id, first_name, last_name, risk_profile, join_date).
    - `accounts`: Account balances and types.
    - `transactions`: Individual transaction records (transaction_id, account_id, merchant_name, amount, transaction_date, category).
    - `loans`: Outstanding loans (loan_amount, interest_rate, status).
    - `support_tickets`: Customer support logs (category, status, resolution_time_hours).
    - `portfolios`: Investment asset valuations (asset_type, value).
    
    **Workflow:**
    1. Analyze the user's question and the conversation history.
    2. If the user's question relies on previous context (e.g., "what are their emails?"), formulate a standalone question that includes all necessary context (e.g., "What are the emails of customers with a Low risk profile?").
    3. Use the `ask_conversational_analytics` tool to query the data using your standalone natural language question. Do NOT write SQL yourself.
    4. Interpret the results from the tool and provide a clear, concise, and helpful answer to the user.
    """,
    tools=[ask_conversational_analytics],
)

app = agent_engines.AdkApp(
    agent=root_agent,
    app_name="bq-conversational-agent",
    enable_tracing=True,
)
