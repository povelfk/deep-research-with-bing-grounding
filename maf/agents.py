from agent_framework.azure import AzureAIAgentClient
from agent_framework import ChatAgent
from azure.identity import DefaultAzureCredential
import os

from maf.middleware import (
    validate_and_parse_research_plan_middleware,
    validate_and_parse_research_report_middleware,
    validate_and_parse_peer_review_middleware,
    validate_and_parse_peer_review_multi_choice_middleware,
    simple_logging_agent_middleware,
)

credential = DefaultAzureCredential()

# =================================================== CLIENTS ===================================================
planner_agent_client = AzureAIAgentClient(
    project_endpoint=os.getenv("PROJECT_ENDPOINT"),
    model_deployment_name=os.getenv("chatModel"),
    async_credential=credential,
    agent_id=os.getenv("PlannerAgentID")
)

bing_search_agent_client = AzureAIAgentClient(
    project_endpoint=os.getenv("PROJECT_ENDPOINT"),
    model_deployment_name=os.getenv("chatModel"),
    async_credential=credential,
    agent_id=os.getenv("BingSearchAgentID")
)

summary_agent_client = AzureAIAgentClient(
    project_endpoint=os.getenv("PROJECT_ENDPOINT"),
    model_deployment_name=os.getenv("chatModel"),
    async_credential=credential,
    agent_id=os.getenv("SummaryAgentID")
)

research_report_agent_client = AzureAIAgentClient(
    project_endpoint=os.getenv("PROJECT_ENDPOINT"),
    model_deployment_name=os.getenv("chatModel"),
    async_credential=credential,
    agent_id=os.getenv("ResearchAgentID")
)

peer_review_agent_multi_choice_client = AzureAIAgentClient(
    project_endpoint=os.getenv("PROJECT_ENDPOINT"),
    model_deployment_name=os.getenv("chatModel"),
    async_credential=credential,
    agent_id=os.getenv("PeerReviewAgentMultiChoiceID")
)

# =================================================== AGENTS ===================================================
planner_agent = ChatAgent(
    name="PlannerAgent",
    chat_client=planner_agent_client,
    middleware=[validate_and_parse_research_plan_middleware]
)
bing_search_agent = ChatAgent(
    name="BingSearchAgent",
    chat_client=bing_search_agent_client,
    middleware=[simple_logging_agent_middleware]
)
summary_agent = ChatAgent(
    name="SummaryAgent",
    chat_client=summary_agent_client,
    middleware=[simple_logging_agent_middleware]
)
research_report_agent = ChatAgent(
    name="ResearchReportAgent",
    chat_client=research_report_agent_client,
    middleware=[validate_and_parse_research_report_middleware]
)
peer_review_agent_multi_choice = ChatAgent(
    name="PeerReviewAgent",
    chat_client=peer_review_agent_multi_choice_client,
    middleware=[validate_and_parse_peer_review_multi_choice_middleware]
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
        bing_search_agent_client,
        summary_agent_client,
        research_report_agent_client,
        peer_review_agent_multi_choice_client,
    ]
    
    for client in clients:
        try:
            # Try multiple approaches to close the underlying HTTP client
            if hasattr(client, '_client'):
                # If there's an underlying client object
                inner_client = client._client
                if hasattr(inner_client, 'close'):
                    if asyncio.iscoroutinefunction(inner_client.close):
                        await inner_client.close()
                    else:
                        inner_client.close()
                elif hasattr(inner_client, '__aexit__'):
                    await inner_client.__aexit__(None, None, None)
            
            # Try to close the client itself
            if hasattr(client, 'close'):
                if asyncio.iscoroutinefunction(client.close):
                    await client.close()
                else:
                    client.close()
            elif hasattr(client, '__aexit__'):
                await client.__aexit__(None, None, None)
                
        except Exception as e:
            # Don't fail on cleanup errors, just log them
            print(f"[Cleanup] Warning: Error closing client: {e}")
    
    # Give a small delay to ensure all connections are closed
    await asyncio.sleep(0.5)
    print("[Cleanup] All agent clients closed successfully")
