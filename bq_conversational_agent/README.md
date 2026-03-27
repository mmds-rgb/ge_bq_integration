# BigQuery Conversational Agent Demo

This project demonstrates how to build a conversational agent that can answer natural language questions about data stored in Google BigQuery. It leverages the **Google Cloud Conversational Analytics API** to securely and accurately translate user questions into SQL queries, execute them against a BigQuery dataset, and return the results in natural language.

## What This Demo Shows

*   **Natural Language to SQL**: The agent uses the Conversational Analytics API to understand complex questions about a mock financial dataset (`financial_services_mock`).
*   **Secure Data Access**: Instead of the agent writing and executing raw SQL directly (which can be a security risk), it delegates this to the managed Conversational Analytics API.
*   **Contextual Understanding**: The agent is grounded in the specific schema of the BigQuery tables (Customers, Accounts, Transactions) to provide accurate and relevant answers.
*   **Agentic Framework**: The agent is built using the Google Agent Development Kit (ADK) and can be deployed to Vertex AI Reasoning Engine.

## GCP Environment Setup

To run this demo, you need a Google Cloud Project with specific services enabled and IAM permissions configured.

### 1. Enable Required APIs
Ensure the following APIs are enabled in your Google Cloud Project:
*   **BigQuery API** (`bigquery.googleapis.com`)
*   **Vertex AI API** (`aiplatform.googleapis.com`)
*   **Conversational Analytics API** (`geminidataanalytics.googleapis.com`)

### 2. IAM Permissions
The service account or user account running this code must have the following IAM roles:
*   `roles/geminidataanalytics.dataAgentStatelessUser`: Required to use the Conversational Analytics `chat` API to query data.
*   `roles/bigquery.dataViewer`: Required to read data from the BigQuery dataset (`financial_services_mock`).
*   `roles/bigquery.jobUser`: Required to execute query jobs in BigQuery.
*   `roles/bigquery.dataEditor`: Required **only** if you need to run the data generation script (`create_bq_model.py`) to create the dataset, tables, and insert mock data.
*   `roles/aiplatform.user`: Required to deploy the agent to Vertex AI Reasoning Engine.
*   `roles/storage.objectAdmin`: Required to upload deployment artifacts to the Cloud Storage staging bucket.
*   `roles/iam.serviceAccountUser`: Required to attach a service account to the Reasoning Engine deployment.

## Local Environment Setup

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Authenticate with Google Cloud:**
    Ensure you are authenticated with an account that has the required IAM permissions.
    ```bash
    gcloud auth application-default login
    gcloud config set project YOUR_PROJECT_ID
    ```

## Generating Mock Data

Before running the agent, you need to populate BigQuery with the mock financial dataset.

Run the data generation script:
```bash
source .venv/bin/activate
python create_bq_model.py
```
This script will create a dataset named `financial_services_mock` and populate it with three tables: `customers`, `accounts`, and `transactions`.

## Running the Tests

The project includes a comprehensive test suite (`test_agent.py`) that verifies the agent's ability to answer various questions about the mock financial data.

To run the tests:
```bash
source .venv/bin/activate
python test_agent.py
```

The test script will simulate a conversation with the agent, asking questions like:
*   "What data about customers do you have?"
*   "Show me all customers with low risk."
*   "Rank customers based on their account balances."

It automatically asserts that the agent's responses contain the expected information and keywords, ensuring the Conversational Analytics API is functioning correctly.

## Deployment to Vertex AI Reasoning Engine

The `deploy.py` script packages the ADK agent and its dependencies and deploys it as a managed endpoint on **Vertex AI Reasoning Engine**. This allows the agent to be called via an API from other applications (like a frontend UI).

### Deployment Prerequisites

1.  **Create a Staging Bucket**: The deployment process requires a Cloud Storage bucket to stage the code artifacts. By default, the script looks for `gs://{project_id}-insurance-agent-assets`. You must create this bucket before deploying:
    ```bash
    gsutil mb -l us-central1 gs://YOUR_PROJECT_ID-insurance-agent-assets
    ```
2.  **Update Script Variables**: If you use a different bucket name or region, update the `location` and `staging_bucket` variables inside `deploy.py`.

### Running the Deployment

Execute the deployment script:
```bash
source .venv/bin/activate
python deploy.py
```

The script will initialize Vertex AI, package the `agent.py` code along with the requirements listed in the script, and create a new Reasoning Engine instance. This process may take a few minutes. Once complete, it will output the Reasoning Engine resource ID.
