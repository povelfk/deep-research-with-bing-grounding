#################################################################### IMPORTANT ##################################################################
# Before running this file, make sure to run 00_create_agents.py to create the agents in Azure AI Foundry and copy their IDs to your .env file  #
#################################################################################################################################################

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to enable relative imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import dotenv
dotenv.load_dotenv(str(parent_dir / ".env"), override=True)

from agent_framework import WorkflowBuilder, Case, Default
from common.data_models import NextAction
from maf.helper import save_report
from maf.update_agent_instructions import update_agent_instructions
from maf.agents import planner_agent, peer_review_agent_multi_choice, cleanup_all_agents
from maf.nodes import (
    search_executor,
    summary_executor,
    research_report_executor,
    to_routing_decision,
    get_next_action,
    handle_complete,
    handle_routing_error,
)

async def main():
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

    try:
        user_query="What are the differences between classical machine learning, deep learning and generative AI?"
        events = await workflow.run(user_query)
        outputs = events.get_outputs()
        final_report = outputs[0]   
        save_report(final_report)
    except Exception as e:
        print(f"Error during workflow execution: {e}")
        raise
    finally:
        print("\n[Main] Cleaning up agent clients...")
        await cleanup_all_agents()

if __name__ == "__main__":
    asyncio.run(main())