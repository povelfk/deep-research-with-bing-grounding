from agent_framework import (
    executor,
    WorkflowContext,
    AgentExecutorResponse,
    AgentExecutorRequest,
    AgentRunResponse,
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
    research_report_agent
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


@executor(id="search_executor")
async def search_executor(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[list],
) -> WorkflowContext[list]:
    """Run all Bing searches concurrently based on the planner output."""

    plan_text = response.agent_run_response.text
    research_plan = ResearchPlan.model_validate_json(plan_text)

    await ctx.shared_state.set("research_plan", research_plan)
    total_queries = sum(len(task.search_queries) for task in research_plan.research_tasks)
    print(
        "[SearchExecutor] Stored research plan in shared state "
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
    print(f"[SearchExecutor] Completed {total_searches} searches")
    await ctx.send_message(search_results)
    return ctx


@executor(id="summary_executor")
async def summary_executor(
    search_results: list,
    ctx: WorkflowContext[list],
) -> WorkflowContext[list]:
    """Summarize each subtopic concurrently."""

    print(f"[SummaryExecutor] Summarizing {len(search_results)} subtopics...")

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

    print(f"[SummaryExecutor] Completed {len(mapped_chunks)} summaries")
    await ctx.send_message(mapped_chunks)
    return ctx


@executor(id="research_report_executor")
async def research_report_executor(
    input_data: list | AgentExecutorResponse,
    ctx: WorkflowContext[AgentExecutorResponse],
) -> WorkflowContext[AgentExecutorResponse]:
    """Execute research report agent for initial generation or revision, and store result in shared state."""
    
    # Determine if this is initial generation or revision
    if isinstance(input_data, list):
        # Initial generation: input_data is mapped_chunks
        print("[ResearchReportExecutor] Initial report generation")
        
        research_plan = await ctx.shared_state.get("research_plan")
        if research_plan is None:
            raise ValueError("Research plan not found in shared state")

        research_input = preprocess_research_data(research_plan, input_data)
        research_input_prompt = json.dumps(research_input, indent=2)

        research_query = (
            "Create an exceptionally comprehensive, **paragraph-focused** and detailed research report "
            "using the following content. **Minimize bullet points** and ensure the final text resembles "
            "a cohesive, academic-style paper:\n\n"
            f"{research_input_prompt}\n\n"
            "As a final reminder, don't forget to include the citation list at the end of the report."
        )
        
    elif isinstance(input_data, AgentExecutorResponse):
        # Revision: input_data is peer review feedback
        print("[ResearchReportExecutor] Report revision based on peer review")
        
        try:
            feedback_text = input_data.agent_run_response.text
            feedback = PeerReviewFeedback.model_validate_json(feedback_text)
        except Exception as e:
            print(f"[ResearchReportExecutor] Warning: Could not parse feedback: {e}")
            feedback_text = input_data.agent_run_response.text
        
        research_query = (
            "Peer review feedback:\n"
            f"{feedback_text}\n\n"
            "Please revise the research report based on the feedback provided."
        )
    else:
        raise TypeError(f"Unexpected input type: {type(input_data)}")

    # Run the research report agent (pass the query string, not the request object)
    agent_response = await research_report_agent.run(research_query)
    
    # Parse and store the report in shared state
    try:
        report_text = agent_response.text if hasattr(agent_response, 'text') else str(agent_response)
        report = ComprehensiveResearchReport.model_validate_json(report_text)
        
        # Store in shared state for later retrieval
        await ctx.shared_state.set("latest_research_report", report.research_report)
        print("[ResearchReportExecutor] Stored latest report in shared state")
        
    except Exception as e:
        print(f"[ResearchReportExecutor] Warning: Could not parse/store report: {e}")
    
    # Create response and send message
    response = AgentExecutorResponse(
        agent_run_response=agent_response,
        executor_id="research_report_executor"
    )
    await ctx.send_message(response)
    return ctx


def get_verdict(expected_result: bool):
    def condition(message: Any) -> bool:
        response_test = None

        # Case 1: AgentExecutorResponse (from @executor-wrapped agents)
        if isinstance(message, AgentExecutorResponse):
            response_text = message.agent_run_response.text
        # Case 2: Direct response object with .text attribute (from ChatAgent)
        elif hasattr(message, 'text'):
            response_text = message.text
        # Case 3: Result object (from streaming)
        elif hasattr(message, 'result') and hasattr(message.result, 'text'):
            response_text = message.result.text
        # Case 4: Response attribute
        elif hasattr(message, 'response') and hasattr(message.response, 'text'):
            response_text = message.response.text
        else:
            # If we can't extract text, allow the edge to pass to avoid workflow deadlock
            print(f"[get_verdict] Warning: Could not extract text from message type {type(message)}")
            return True
        try:
            feedback = PeerReviewFeedback.model_validate_json(response_text)
            result = feedback.is_satisfactory == expected_result
            print(f"[get_verdict] is_satisfactory={feedback.is_satisfactory}, expected={expected_result}, match={result}")
            return result
        except Exception:
            return False
        
    return condition


@executor(id="output_final_report")
async def output_final_report(
    review_response: AgentExecutorResponse,
    ctx: WorkflowContext,
) -> None:
    """Extract and output the final research report from shared state."""
    
    try:
        # Get the latest report from shared state
        latest_report = await ctx.shared_state.get("latest_research_report")
        
        if latest_report:
            print("[OutputFinalReport] Extracting final report from shared state")
            await ctx.yield_output(latest_report)
        else:
            print("[OutputFinalReport] Error: Could not find latest research report in shared state")
            await ctx.yield_output("Error: Report not found")
            
    except Exception as e:
        print(f"[OutputFinalReport] Error: {e}")
        await ctx.yield_output(f"Error: {e}")
