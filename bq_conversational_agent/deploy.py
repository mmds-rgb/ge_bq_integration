import os
import vertexai
from google.protobuf import json_format
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Monkeypatch json_format.Parse to ignore unknown fields
original_parse = json_format.Parse
def patched_parse(text, message, ignore_unknown_fields=False, descriptor_pool=None, max_recursion_depth=100):
    return original_parse(text, message, ignore_unknown_fields=True, descriptor_pool=descriptor_pool, max_recursion_depth=max_recursion_depth)
json_format.Parse = patched_parse

def deploy():
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set. Please check your .env file.")
        
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    staging_bucket = os.environ.get("STAGING_BUCKET", f"gs://{project_id}-insurance-agent-assets")
    
    # Import app first so its global init doesn't override our deployment init
    from agent import app
    from vertexai import agent_engines

    print(f"Initializing Vertex AI for project {project_id} in {location}...")
    vertexai.init(project=project_id, location=location, staging_bucket=staging_bucket)

    print("Deploying agent to Reasoning Engine...")
    try:
        remote_agent = agent_engines.create(
            agent_engine=app,
            requirements=[
                "google-adk",
                "google-cloud-aiplatform[adk,agent_engines]",
                "google-cloud-bigquery",
                "cloudpickle",
                "functions-framework",
                "uvicorn",
                "fastapi"
            ],
            display_name="bq-conversational-agent",
            description="Agent for querying financial data in BigQuery",
            extra_packages=["agent.py"],
        )
        print(f"Deployment successful!")
        print(f"Resource Name: {remote_agent.resource_name}")
        return remote_agent
    except Exception as e:
        print(f"Deployment failed: {e}")
        raise

if __name__ == "__main__":
    deploy()
