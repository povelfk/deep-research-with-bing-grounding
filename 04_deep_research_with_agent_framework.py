import dotenv
dotenv.load_dotenv(".env", override=True)

import asyncio
from rich.console import Console
from rich.markdown import Markdown

from agent_framework import WorkflowBuilder, Case, Default
from maf.update_agent_instructions import update_agent_instructions
from common.create_azure_ai_agents import create_agents, get_project_client
from maf.create_peer_review_agent_multi_choice import create_peer_review_agent_multi_choice

from maf.nodes import (
    search_executor,
    summary_executor,
    research_report_executor,
    to_routing_decision,
    get_next_action,
    handle_complete,
    handle_routing_error,
)
from maf.agents import planner_agent, peer_review_agent_multi_choice, cleanup_all_agents
from common.data_models import NextAction


async def main():
    ### IMPORTANT ###
    # Before running this file, make sure to run 00_create_agents.py to create the agents in Azure AI Foundry and copy their IDs to your .env file
    update_agent_instructions()
    workflow = (
        WorkflowBuilder()
        .set_start_executor(planner_agent)
        .add_edge(planner_agent, search_executor)
        .add_edge(search_executor, summary_executor)
        .add_edge(summary_executor, research_report_executor)
        .add_edge(research_report_executor, peer_review_agent_multi_choice)
        .add_edge(peer_review_agent_multi_choice, to_routing_decision)
        .add_switch_case_edge_group(
            to_routing_decision,
            [
                Case(condition=get_next_action(NextAction.COMPLETE), target=handle_complete),
                Case(condition=get_next_action(NextAction.REVISE_REPORT), target=research_report_executor),
                Case(condition=get_next_action(NextAction.GATHER_MORE_DATA), target=search_executor),
                Default(target=handle_routing_error),
            ]
        )
        .build()
    )

    user_query="What are the differences between classical machine learning, deep learning and generative AI?"

    try:
        events = await workflow.run(user_query)
        final_report = events.get_outputs()[0]

        # Render Markdown in terminal
        console = Console()
        console.print(Markdown(final_report))
    except Exception as e:
        print(f"Error during workflow execution: {e}")
        raise
    finally:
        # Always cleanup agent clients after workflow completes, even if an error occurs
        print("\n[Main] Cleaning up agent clients...")
        await cleanup_all_agents()

if __name__ == "__main__":

    asyncio.run(main())