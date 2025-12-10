"""
Azure AI Agents v2 SDK client and agent definitions.
Uses agent names (not IDs) and the azure.ai.projects SDK.
"""
import os
from dotenv import load_dotenv
load_dotenv("../.env")

from agent_framework.azure import AzureAIClient
from agent_framework import ChatAgent
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from maf.middleware import simple_logging_agent_middleware

from common.data_models import (
    ResearchPlan,
    ComprehensiveResearchReport,
    PeerReviewFeedbackMultiChoice
)

# Use async credential for Azure AI Agents v2 (for agent_framework ChatAgents)
async_credential = AsyncDefaultAzureCredential()

# Standard project client for most operations
project_client = AsyncAIProjectClient(
    credential=async_credential,
    endpoint=os.getenv("PROJECT_ENDPOINT")
)

# Async OpenAI client for parallel Bing search with citations
openai_client = project_client.get_openai_client()

# =================================================== CLIENTS ===================================================
# Note: v2 SDK uses agent_name instead of agent_id
planner_agent_client = AzureAIClient(
    project_client=project_client,
    model_deployment_name=os.getenv("chatModel"),
    async_credential=async_credential,
    agent_name="ResearchPlanAgent-v2"
)

summary_agent_client = AzureAIClient(
    project_client=project_client,
    model_deployment_name=os.getenv("chatModel"),
    async_credential=async_credential,
    agent_name="SummaryAgent-v2"
)

research_report_agent_client = AzureAIClient(
    project_client=project_client,
    model_deployment_name=os.getenv("chatModel"),
    async_credential=async_credential,
    agent_name="ResearchReportAgent-v2"
)

peer_review_agent_multi_choice_client = AzureAIClient(
    project_client=project_client,
    model_deployment_name=os.getenv("chatModel"),
    async_credential=async_credential,
    agent_name="PeerReviewAgentMultiChoice-v2"
)

# =================================================== AGENTS ===================================================
planner_agent = ChatAgent(
    name="PlannerAgent",
    chat_client=planner_agent_client,
    middleware=[simple_logging_agent_middleware],
    response_format=ResearchPlan
)

summary_agent = ChatAgent(
    name="SummaryAgent",
    chat_client=summary_agent_client,
    middleware=[simple_logging_agent_middleware]
)

research_report_agent = ChatAgent(
    name="ResearchReportAgent",
    chat_client=research_report_agent_client,
    middleware=[simple_logging_agent_middleware],
    response_format=ComprehensiveResearchReport
)

peer_review_agent_multi_choice = ChatAgent(
    name="PeerReviewAgentMultiChoice",
    chat_client=peer_review_agent_multi_choice_client,
    middleware=[simple_logging_agent_middleware],
    response_format=PeerReviewFeedbackMultiChoice
)

# =================================================== CLEANUP ===================================================
async def cleanup_all_agents():
    """
    Close all Azure AI Agent client sessions to prevent resource leaks.
    Call this at the end of your application lifecycle.
    """
    import asyncio
    
    clients = [
        planner_agent_client,
        summary_agent_client,
        research_report_agent_client,
        peer_review_agent_multi_choice_client,
    ]
    
    for client in clients:
        try:
            # Try multiple approaches to close the underlying HTTP client
            if hasattr(client, '_client'):
                inner_client = client._client
                if hasattr(inner_client, 'close'):
                    if asyncio.iscoroutinefunction(inner_client.close):
                        await inner_client.close()
                    else:
                        inner_client.close()
                elif hasattr(inner_client, '__aexit__'):
                    await inner_client.__aexit__(None, None, None)
            
            if hasattr(client, 'close'):
                if asyncio.iscoroutinefunction(client.close):
                    await client.close()
                else:
                    client.close()
            elif hasattr(client, '__aexit__'):
                await client.__aexit__(None, None, None)
                
        except Exception as e:
            print(f"[Cleanup] Warning: Error closing client: {e}")
    
    # Close the async credential
    try:
        await async_credential.close()
    except Exception as e:
        print(f"[Cleanup] Warning: Error closing credential: {e}")
    
    await asyncio.sleep(0.5)
    print("[Cleanup] All agent clients closed successfully")
