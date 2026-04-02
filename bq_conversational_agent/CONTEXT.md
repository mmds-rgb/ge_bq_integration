# Master Context & Architectural Guide - BQ Conversational Agent

This document serves as the **Master Guide** for the BigQuery Conversational Agent project. It outlines the system architecture, data models, testing paradigms, and deployment best practices for developers and operators.

---

## 🏗️ System Architecture

The BQ Conversational Agent leverages a layered architecture to translate natural language questions into secure SQL analytics without exposing raw database credentials to the LLM.

### 🔄 Data & Query Flow
1.  **User Query**: User asks a question (e.g., "What is the average resolution time for support tickets?").
2.  **ADK Agent (`agent.py`)**: The Agent Development Kit (ADK) receives the query and routes it to the `ask_conversational_analytics` tool.
3.  **Conversational Analytics (CA) API**: The tool creates a structured request specifying the BigQuery tables to query. The CA API securely translates the natural language into SQL, executes it against BigQuery, and returns a text answer.
4.  **Response**: The agent relays the answer back to the user.

> [!IMPORTANT]
> This architecture ensures that the LLM **does not write raw SQL**. Instead, it delegates SQL generation to a managed, secure service, minimizing prompt injection risks.

---

## 📊 Data Models & Schema

The dataset (`financial_services_mock`) contains 6 core tables representing common banking and customer success metrics.

### Core Tables
1.  **`customers`**: `customer_id`, `first_name`, `last_name`, `email`, `risk_profile`.
2.  **`accounts`**: `account_id`, `customer_id`, `account_type`, `balance`.
3.  **`transactions`**: `transaction_id`, `account_id`, `amount`, `transaction_date`, `merchant_name`.

### Extended Testing Tables
4.  **`loans`**: `loan_id`, `customer_id`, `loan_amount`, `interest_rate`, `status`.
5.  **`support_tickets`**: `ticket_id`, `customer_id`, `category`, `status`, `resolution_time_hours`.
6.  **`portfolios`**: `portfolio_id`, `customer_id`, `asset_type`, `value`.

> [!NOTE]
> To ensure the agent is aware of these tables, you must explicitly list them in the `tables` array in `agent.py` and describe their schemas in the `root_agent` prompt instructions.

---

## 🧪 Testing & Verification Paradigm

The test suite (`test_agent.py`) verifies accuracy using **Pre-Calculated Static Value Assertions** against known seeds.

### 🎯 exact Value Assertions
Instead of checking for fuzzy keywords (like `"K"`), the tests assert exact values (e.g., `"184K"`, `"70K"`, `"36.1"`). 
*   **Why?** Ensures the model is performing precise math and not just outputting generic text definitions.
*   **Limitation**: If you re-seed the DB randomly, these exact numbers will break. They are tied to the current stable seed state.

### ✍️ Prompt Constraints for Formatting
The Conversational Analytics API often favors **Summarization** over listing all details. To overcome this in testing, use heavy-handed constraints:
-   **Example Query**: `"List the names and balances of the top 3 customers... explicitly list all 3 names separately in text and ensure you round to nearest thousand in 36K format."`
-   **Lessons Learned**: Without explicit rounding instructions, the CA API may return raw decimals (e.g., `184.29K`), causing static test checks to fail if they expect `184K`.

---

## 🚀 Deployment Playbook (Vertex AI)

The `deploy.py` script packages the app and registers it with **Vertex AI Reasoning Engine**.

### ⚠️ Critical Dependency Tracking
Remote container initializations will fail if `agent.py` imports local modules that aren't explicitly declared in the deployment `requirements`:
-   **Override Required**: In `deploy.py`, ensure `google-cloud-geminidataanalytics` and `python-dotenv` are specified in the `requirements` array. 
-   **Symptom**: Without these, you will see generic `400 Reasoning Engine resource failed to start` errors (usually a `ModuleNotFoundError` during unpickling).

### ✅ Final Endpoint Reference
-   **Resource ID**: `projects/308598841699/locations/us-central1/reasoningEngines/6955053710229635072`
