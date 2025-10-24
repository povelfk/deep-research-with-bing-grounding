from agent_framework import (
    executor,
    WorkflowContext,
    AgentExecutorResponse,
    AgentExecutorRequest,
    ChatMessage,
    Role,
    WorkflowBuilder,
    ChatAgent,
)
import asyncio
import json
from typing import Any, Callable

from dataclasses import dataclass

from common.data_models import (
    ResearchPlan,
    ComprehensiveResearchReport,
    PeerReviewFeedback,
)
from common.utils_research import preprocess_research_data

from maf.agents import (
    bing_search_agent,
    summary_agent,
    research_report_agent,
    peer_review_agent,
) 


async def retry_with_backoff(
    func: Callable,
    *args: Any,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    **kwargs: Any
) -> Any:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        *args, **kwargs: Arguments to pass to func
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                print(f"[Retry] Attempt {attempt + 1}/{max_retries + 1} failed: {type(e).__name__}. Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                print(f"[Retry] All {max_retries + 1} attempts failed.")
    
    raise last_exception


@executor(id="parallel_search_executor")
async def parallel_search_executor(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[list],
) -> WorkflowContext[list]:
    """Run all Bing searches concurrently based on the planner output."""

    plan_text = response.agent_run_response.text
    research_plan = ResearchPlan.model_validate_json(plan_text)

    await ctx.shared_state.set("research_plan", research_plan)
    total_queries = sum(len(task.search_queries) for task in research_plan.research_tasks)
    print(
        "[ParallelSearchExecutor] Stored research plan in shared state "
        f"({len(research_plan.research_tasks)} tasks, {total_queries} queries)"
    )

    async def search_single_query(subtopic: str, query: str) -> dict:
        prompt = (
            f"Research the following query: {query}\n"
            f"This is related to subtopic: {subtopic}\n"
            "Please provide the information and cite your sources using the available tools."
        )

        # Wrap the agent call with retry logic
        agent_response = await retry_with_backoff(
            bing_search_agent.run,
            prompt,
            max_retries=3,
            initial_delay=2.0
        )
        agent_text = agent_response.text if hasattr(agent_response, "text") else str(agent_response)

        return {
            "query": query,
            "agent_response": agent_text,
            "results": [],  # Populate with citation extraction if desired
        }

    # Old approach: Create flat list of all tasks, then restructure results
    # tasks = [
    #     search_single_query(task.subtopic, query)
    #     for task in research_plan.research_tasks
    #     for query in task.search_queries
    # ]
    # all_results = await asyncio.gather(*tasks, return_exceptions=True)
    #
    # search_results = []
    # idx = 0
    # for task in research_plan.research_tasks:
    #     subtopic_payload = {"subtopic": task.subtopic, "queries": []}
    #     for query in task.search_queries:
    #         result = all_results[idx]
    #         if isinstance(result, Exception):
    #             print(f"Error for query '{query}': {result}")
    #             subtopic_payload["queries"].append(
    #                 {"query": query, "results": [], "error": str(result)}
    #             )
    #         else:
    #             subtopic_payload["queries"].append(result)
    #         idx += 1
    #     search_results.append(subtopic_payload)

    # Better approach: Run ALL queries in parallel, then restructure with clear mapping
    # Step 1: Create ALL coroutines at once (fully parallel execution)
    all_task_coroutines = []
    task_query_mapping = []  # Track which results belong to which task
    
    for task in research_plan.research_tasks:
        task_start_idx = len(all_task_coroutines)
        for query in task.search_queries:
            all_task_coroutines.append(search_single_query(task.subtopic, query))
        task_end_idx = len(all_task_coroutines)
        task_query_mapping.append((task, task_start_idx, task_end_idx))
    
    # Step 2: Execute ALL searches in parallel
    all_results = await asyncio.gather(*all_task_coroutines, return_exceptions=True)
    
    # Step 3: Restructure results back into task/subtopic hierarchy
    search_results = []
    for task, start_idx, end_idx in task_query_mapping:
        subtopic_payload = {"subtopic": task.subtopic, "queries": []}
        
        for query, result in zip(task.search_queries, all_results[start_idx:end_idx]):
            if isinstance(result, Exception):
                print(f"Error for query '{query}': {result}")
                subtopic_payload["queries"].append({
                    "query": query, 
                    "results": [], 
                    "error": str(result)
                })
            else:
                subtopic_payload["queries"].append(result)
        
        search_results.append(subtopic_payload)

    total_searches = sum(len(subtopic["queries"]) for subtopic in search_results)
    print(f"[ParallelSearchExecutor] Completed {total_searches} searches")
    await ctx.send_message(search_results)
    return ctx


@executor(id="parallel_summary_executor")
async def parallel_summary_executor(
    search_results: list,
    ctx: WorkflowContext[list],
) -> WorkflowContext[list]:
    """Summarize each subtopic concurrently."""

    print(f"[ParallelSummaryExecutor] Summarizing {len(search_results)} subtopics...")

    async def summarize_subtopic(subtopic_result: dict) -> dict:
        responses = [
            query_data["agent_response"]
            for query_data in subtopic_result.get("queries", [])
            if query_data.get("agent_response")
        ]
        content = "\n\n---\n\n".join(responses)

        if not content:
            return {
                "subtopic": subtopic_result.get("subtopic", "Unknown"),
                "summary": "No content found.",
                "citations": [],
            }

        prompt = (
            f"Summarize the following information related to the subtopic "
            f"'{subtopic_result.get('subtopic', 'Unknown')}':\n\n{content}"
        )
        
        # Wrap the agent call with retry logic
        summary_response = await retry_with_backoff(
            summary_agent.run,
            prompt,
            max_retries=3,
            initial_delay=2.0
        )
        summary_text = (
            summary_response.text if hasattr(summary_response, "text") else str(summary_response)
        )

        return {
            "subtopic": subtopic_result.get("subtopic"),
            "summary": summary_text.strip(),
            "citations": [],  # Add citation handling if needed
        }

    mapped_chunks = await asyncio.gather(
        *(summarize_subtopic(result) for result in search_results)
    )

    print(f"[ParallelSummaryExecutor] Completed {len(mapped_chunks)} summaries")
    await ctx.send_message(mapped_chunks)
    return ctx


@executor(id="prepare_research_input")
async def prepare_research_input(
    mapped_chunks: list,
    ctx: WorkflowContext[AgentExecutorRequest],
) -> WorkflowContext[AgentExecutorRequest]:
    """Turn summaries + plan into a prompt for the report agent."""

    research_plan = await ctx.shared_state.get("research_plan")
    if research_plan is None:
        raise ValueError("Research plan not found in shared state")

    research_input = preprocess_research_data(research_plan, mapped_chunks)
    research_input_prompt = json.dumps(research_input, indent=2)

    research_query = (
        "Create an exceptionally comprehensive, **paragraph-focused** and detailed research report "
        "using the following content. **Minimize bullet points** and ensure the final text resembles "
        "a cohesive, academic-style paper:\n\n"
        f"{research_input_prompt}\n\n"
        "As a final reminder, don't forget to include the citation list at the end of the report."
    )

    request = AgentExecutorRequest(
        messages=[ChatMessage(Role.USER, text=research_query)],
        should_respond=True,
    )
    await ctx.send_message(request)
    return ctx


@executor(id="peer_review_loop")
async def peer_review_loop(
    report_response: AgentExecutorResponse,
    ctx: WorkflowContext,
) -> None:
    """Iteratively improve the report until peer review approves."""

    max_iterations = 10

    for iteration in range(1, max_iterations + 1):
        report_text = report_response.agent_run_response.text
        report = ComprehensiveResearchReport.model_validate_json(report_text)

        review_prompt = (
            "A research agent has produced a research report. Please review it:\n\n"
            f"{report_text}"
        )
        review_response = await retry_with_backoff(
            peer_review_agent.run,
            review_prompt,
            max_retries=3,
            initial_delay=2.0
        )
        feedback = PeerReviewFeedback.model_validate_json(review_response.text)

        if feedback.is_satisfactory:
            print(f"[PeerReviewLoop] Report approved after {iteration} iteration(s)")
            await ctx.yield_output(report.research_report)
            return

        print(f"[PeerReviewLoop] Iteration {iteration}: Revising based on feedback")
        revision_prompt = (
            "Peer review feedback:\n"
            f"{review_response.text}\n\n"
            "Please revise the research report."
        )
        revised_response = await retry_with_backoff(
            research_report_agent.run,
            revision_prompt,
            max_retries=3,
            initial_delay=2.0
        )

        @dataclass
        class _TempAgentExecutorResponse:
            agent_run_response: object
            executor_id: str = "research_report_agent"
            full_conversation: list | None = None

        report_response = _TempAgentExecutorResponse(agent_run_response=revised_response)

    print("[PeerReviewLoop] Max iterations reached")
    await ctx.yield_output(report.research_report if report else report_text)