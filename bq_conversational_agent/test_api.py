import os
import google.cloud.geminidataanalytics as geminidataanalytics

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "primary-394719")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

client = geminidataanalytics.DataChatServiceClient()

inline_context = geminidataanalytics.Context()

bq_ref = geminidataanalytics.BigQueryTableReference()
bq_ref.project_id = project_id
bq_ref.dataset_id = "financial_services_mock"
bq_ref.table_id = "customers"

datasource_references = geminidataanalytics.DatasourceReferences()
datasource_references.bq.table_references = [bq_ref]
inline_context.datasource_references = datasource_references

message = geminidataanalytics.Message()
message.user_message.text = "How many customers are there?"

data_agent_client = geminidataanalytics.DataAgentServiceClient()
data_agent = geminidataanalytics.DataAgent()
data_agent.data_analytics_agent.published_context = inline_context
data_agent.name = f"projects/{project_id}/locations/{location}/dataAgents/test_agent_1"

request = geminidataanalytics.CreateDataAgentRequest(
    parent=f"projects/{project_id}/locations/{location}",
    data_agent_id="test_agent_1",
    data_agent=data_agent
)

try:
    response = data_agent_client.create_data_agent(request=request)
    print("Data Agent created:", response.name)
except Exception as e:
    print("Error:", e)
