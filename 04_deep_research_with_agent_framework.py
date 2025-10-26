import dotenv
dotenv.load_dotenv(".env", override=True)

import asyncio
from rich.console import Console
from rich.markdown import Markdown

from agent_framework import WorkflowBuilder
from maf.update_agent_instructions import update_agent_instructions

from maf.nodes import (
    search_executor,
    summary_executor,
    # prepare_research_input,
    research_report_agent,
    research_report_executor,
    # peer_review_loop,
    get_verdict,
    output_final_report
)
from maf.agents import planner_agent, peer_review_agent, cleanup_all_agents


async def main():
    update_agent_instructions()
    workflow = (
        WorkflowBuilder()
        .set_start_executor(planner_agent)
        .add_edge(planner_agent, search_executor)
        .add_edge(search_executor, summary_executor)
        .add_edge(summary_executor, research_report_executor)
        .add_edge(research_report_executor, peer_review_agent)
        .add_edge(peer_review_agent, output_final_report, condition=get_verdict(True)) # If satisfactory (True), output the final report and end
        .add_edge(peer_review_agent, research_report_executor, condition=get_verdict(False)) # If not satisfactory (False), loop back to research_report_agent
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