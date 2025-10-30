import dotenv
dotenv.load_dotenv(".env", override=True)

import asyncio
from rich.console import Console
from rich.markdown import Markdown

from agent_framework import WorkflowBuilder, Case, Default
from maf.update_agent_instructions import update_agent_instructions

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

# Multi-choice routing system implemented using switch-case pattern
# The peer review agent now intelligently routes to specific agents based on NextAction enum:
# - COMPLETE: Output final report and end workflow
# - REVISE_REPORT: Route back to research_report_executor (reuses existing executor)
# - GATHER_MORE_DATA: Route back to search_executor (reuses existing executor)
#
# ITERATION LIMIT: The workflow enforces a maximum of 3 revision/data gathering cycles
# to prevent infinite loops. After 3 iterations, the workflow will force completion.

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
        # Switch-case routing based on NextAction enum
        .add_switch_case_edge_group(
            to_routing_decision,
            [
                Case(condition=get_next_action(NextAction.COMPLETE), target=handle_complete),
                Case(condition=get_next_action(NextAction.REVISE_REPORT), target=research_report_executor),
                Case(condition=get_next_action(NextAction.GATHER_MORE_DATA), target=search_executor),
                Default(target=handle_routing_error),
            ]
        )
        # Note: No duplicate edges needed! 
        # - research_report_executor always goes to peer_review (already defined above)
        # - search_executor always goes to summary (already defined above)
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