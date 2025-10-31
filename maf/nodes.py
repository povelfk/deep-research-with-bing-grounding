from agent_framework import (
    executor,
    WorkflowContext,
    AgentExecutorResponse
)
import asyncio
import json
import os
from typing import Any, Callable, Union
from dataclasses import dataclass

from common.data_models import (
    ResearchPlan,
    ComprehensiveResearchReport,
    PeerReviewFeedback,
    PeerReviewFeedbackMultiChoice,
    NextAction,
)
from common.utils_research import preprocess_research_data
from common.utils_search import extract_agent_response_and_urls_async
from common.utils_summary import collect_responses_and_citations
from common.create_azure_ai_agents import get_async_project_client

from maf.agents import (
    summary_agent,
    research_report_agent,
    bing_search_agent_client,  # Import the raw client
)

# Forward declaration for type hints
@dataclass
class RoutingDecision:
    """Typed payload used for switch-case routing based on peer review feedback."""
    next_action: NextAction
    feedback: PeerReviewFeedbackMultiChoice 


async def retry_with_backoff(
    func: Callable,
    *args: Any,
    max_retries: int = 2,
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
    input_data: Union[AgentExecutorResponse, RoutingDecision],
    ctx: WorkflowContext[list],
) -> WorkflowContext[list]:
    """
    Run Bing searches based on input from either:
    1. planner_agent (AgentExecutorResponse with ResearchPlan)
    2. to_routing_decision (RoutingDecision with additional queries for gap filling)
    """
    
    # Determine input type and extract search queries
    if isinstance(input_data, AgentExecutorResponse):
        # Initial run: Parse research plan from planner
        print("[SearchExecutor] Initial search execution from planner")
        plan_text = input_data.agent_run_response.text
        research_plan = ResearchPlan.model_validate_json(plan_text)
        
        await ctx.shared_state.set("research_plan", research_plan)
        total_queries = sum(len(task.search_queries) for task in research_plan.research_tasks)
        print(
            "[SearchExecutor] Stored research plan in shared state "
            f"({len(research_plan.research_tasks)} tasks, {total_queries} queries)"
        )
        
        # Build search tasks from research plan
        search_tasks = []
        for task in research_plan.research_tasks:
            for query in task.search_queries:
                search_tasks.append((task.subtopic, query))
                
    elif hasattr(input_data, 'next_action') and hasattr(input_data, 'feedback'):
        # Feedback loop: Extract additional queries from routing decision
        print("[SearchExecutor] Additional search execution from feedback loop")
        decision = input_data
        feedback = decision.feedback
        
        additional_queries = feedback.additional_queries or []
        if not additional_queries and feedback.next_action_details:
            # Fallback: use next_action_details as a single query
            additional_queries = [feedback.next_action_details]
        
        print(f"[SearchExecutor] Executing {len(additional_queries)} additional queries")
        
        # Build search tasks for additional queries
        search_tasks = [("Additional Research", query) for query in additional_queries]
        
    else:
        raise TypeError(f"Unexpected input type: {type(input_data)}")

    async def search_single_query(subtopic: str, query: str) -> dict:
        prompt = (
            f"Research the following query: {query}\n"
            f"This is related to subtopic: {subtopic}\n"
            "Please provide the information and cite your sources using the available tools."
        )

        # Use the async Azure AI Agent client for true parallel execution
        # This is necessary because ChatAgent doesn't expose thread metadata
        project_client = get_async_project_client(os.getenv("PROJECT_ENDPOINT"))
        thread = None
        
        try:
            # Create thread and get agent response
            thread = await project_client.agents.threads.create()
            await project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            # Run the agent (using the raw client's agent_id)
            run = await project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=bing_search_agent_client.agent_id
            )
            
            # Extract response text and citations from thread (async version)
            agent_text, citations = await extract_agent_response_and_urls_async(project_client, thread.id, query)
            
            # Convert citations to the expected format
            citation_results = [{"title": c["title"], "url": c["url"]} for c in citations]
            
            print(f"[SearchExecutor] Extracted {len(citation_results)} citations for query: {query[:50]}...")
            
            return {
                "query": query,
                "agent_response": agent_text,
                "results": citation_results,
            }
            
        except Exception as e:
            print(f"[SearchExecutor] Error for query '{query}': {e}")
            return {
                "query": query,
                "agent_response": "",
                "results": [],
                "error": str(e)
            }
        finally:
            # Clean up thread and close client
            if thread:
                try:
                    await project_client.agents.threads.delete(thread_id=thread.id)
                except Exception:
                    pass
            # Close the async client to free resources
            try:
                await project_client.close()
            except Exception:
                pass

    # Execute all searches in parallel
    all_results = await asyncio.gather(
        *(search_single_query(subtopic, query) for subtopic, query in search_tasks),
        return_exceptions=True
    )
    
    # Group results by subtopic
    subtopic_groups = {}
    for (subtopic, query), result in zip(search_tasks, all_results):
        if subtopic not in subtopic_groups:
            subtopic_groups[subtopic] = {"subtopic": subtopic, "queries": []}
        
        if isinstance(result, Exception):
            print(f"Error for query '{query}': {result}")
            subtopic_groups[subtopic]["queries"].append({
                "query": query, 
                "results": [], 
                "error": str(result)
            })
        else:
            subtopic_groups[subtopic]["queries"].append(result)
    
    search_results = list(subtopic_groups.values())
    total_searches = sum(len(subtopic["queries"]) for subtopic in search_results)
    print(f"[SearchExecutor] Completed {total_searches} searches")
    
    # for testing purposes
    # await ctx.yield_output(search_results)

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
        # Use the same utility function as the notebook for consistency
        all_responses, unique_citations = collect_responses_and_citations(subtopic_result)
        content = "\n\n---\n\n".join(all_responses)
        
        # Convert set of tuples to list of dicts
        citations_list = [{"title": title, "url": url} for (title, url) in unique_citations]

        if not content:
            return {
                "subtopic": subtopic_result.get("subtopic", "Unknown"),
                "summary": "No content found.",
                "citations": citations_list,
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
            "citations": citations_list,
        }

    mapped_chunks = await asyncio.gather(
        *(summarize_subtopic(result) for result in search_results)
    )

    print(f"[SummaryExecutor] Completed {len(mapped_chunks)} summaries")
    await ctx.send_message(mapped_chunks)
    return ctx


@executor(id="research_report_executor")
async def research_report_executor(
    input_data: Union[list, RoutingDecision],
    ctx: WorkflowContext[AgentExecutorResponse],
) -> WorkflowContext[AgentExecutorResponse]:
    """
    Execute research report agent for initial generation or revision.
    Handles input from:
    1. summary_executor (list of mapped_chunks for initial generation)
    2. to_routing_decision (RoutingDecision with feedback for revision)
    """
    
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
        
    elif hasattr(input_data, 'next_action') and hasattr(input_data, 'feedback'):
        # Revision: input_data is RoutingDecision with peer review feedback
        print("[ResearchReportExecutor] Report revision based on peer review feedback")
        
        decision = input_data
        feedback = decision.feedback
        
        # Construct detailed revision prompt
        revision_prompt_parts = ["Peer review feedback:\n"]
        
        if feedback.overall_feedback:
            revision_prompt_parts.append(f"Overall: {feedback.overall_feedback}\n")
        
        if feedback.suggested_improvements:
            revision_prompt_parts.append(f"Suggested improvements:\n")
            for improvement in feedback.suggested_improvements:
                revision_prompt_parts.append(f"  - {improvement}\n")
        
        if feedback.next_action_details:
            revision_prompt_parts.append(f"\nSpecific details to address: {feedback.next_action_details}\n")
        
        revision_prompt_parts.append("\nPlease revise the research report based on the feedback provided.")
        
        research_query = "".join(revision_prompt_parts)
        
    else:
        raise TypeError(f"Unexpected input type: {type(input_data)}")

    # Run the research report agent
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


# ============================================================================================================
# NEW: Multi-choice routing system using switch-case pattern
# ============================================================================================================

@executor(id="to_routing_decision")
async def to_routing_decision(
    response: AgentExecutorResponse,
    ctx: WorkflowContext[RoutingDecision],
) -> None:
    """Transform peer review response into a typed routing decision for switch-case evaluation."""
    
    # Get current iteration count (handle KeyError if not set)
    try:
        iteration_count = await ctx.shared_state.get("iteration_count")
    except KeyError:
        iteration_count = 0
    
    max_iterations = 2  # Maximum number of revision/data gathering cycles
    
    try:
        response_text = response.agent_run_response.text
        feedback = PeerReviewFeedbackMultiChoice.model_validate_json(response_text)
        
        # Check if we've exceeded max iterations
        if iteration_count >= max_iterations and feedback.next_action != NextAction.COMPLETE:
            print(f"[RoutingDecision] ⚠️  Max iterations ({max_iterations}) reached. Forcing completion.")
            # Override the decision to complete
            decision = RoutingDecision(
                next_action=NextAction.COMPLETE,
                feedback=feedback
            )
        else:
            # Create typed routing decision
            decision = RoutingDecision(
                next_action=feedback.next_action,
                feedback=feedback
            )
            
            # Increment iteration count if routing back for revision or more data
            if feedback.next_action in [NextAction.REVISE_REPORT, NextAction.GATHER_MORE_DATA]:
                iteration_count += 1
                await ctx.shared_state.set("iteration_count", iteration_count)
                print(f"[RoutingDecision] Iteration {iteration_count}/{max_iterations}")
        
        print(f"[RoutingDecision] Next action: {decision.next_action.value}")
        print(f"[RoutingDecision] Is satisfactory: {feedback.is_satisfactory}")
        if feedback.next_action_details:
            print(f"[RoutingDecision] Details: {feedback.next_action_details[:100]}...")
        
        await ctx.send_message(decision)
        
    except Exception as e:
        print(f"[RoutingDecision] Error parsing feedback: {e}")
        # Check iteration limit before defaulting to revision
        if iteration_count >= max_iterations:
            print(f"[RoutingDecision] Max iterations reached, forcing completion despite error")
            await ctx.send_message(RoutingDecision(
                next_action=NextAction.COMPLETE,
                feedback=None
            ))
        else:
            # Send a default error routing decision
            await ctx.send_message(RoutingDecision(
                next_action=NextAction.REVISE_REPORT,
                feedback=None
            ))
            iteration_count += 1
            await ctx.shared_state.set("iteration_count", iteration_count)


def get_next_action(expected_action: NextAction):
    """Factory that returns a predicate matching a specific NextAction value."""
    
    def condition(message: Any) -> bool:
        # Only match when the message is a RoutingDecision with the expected action
        if isinstance(message, RoutingDecision):
            match = message.next_action == expected_action
            print(f"[get_next_action] Checking {message.next_action.value} == {expected_action.value}: {match}")
            return match
        return False
    
    return condition


@executor(id="handle_complete")
async def handle_complete(
    decision: RoutingDecision,
    ctx: WorkflowContext,
) -> None:
    """Handle the COMPLETE routing case - extract and output final report."""
    
    if decision.next_action != NextAction.COMPLETE:
        raise RuntimeError(f"This executor should only handle COMPLETE actions, got {decision.next_action.value}")
    
    try:
        # Get the latest report from shared state
        latest_report = await ctx.shared_state.get("latest_research_report")
        
        if latest_report:
            print("[HandleComplete] Report satisfactory - outputting final report")
            await ctx.yield_output(latest_report)
        else:
            print("[HandleComplete] Error: Could not find latest research report in shared state")
            await ctx.yield_output("Error: Report not found")
            
    except Exception as e:
        print(f"[HandleComplete] Error: {e}")
        await ctx.yield_output(f"Error: {e}")


@executor(id="handle_routing_error")
async def handle_routing_error(
    decision: RoutingDecision,
    ctx: WorkflowContext,
) -> None:
    """Default handler for unexpected routing cases."""
    
    print(f"[HandleRoutingError] Unexpected routing decision: {decision.next_action.value}")
    error_msg = (
        f"Workflow error: Unexpected routing decision '{decision.next_action.value}'. "
        f"This case is not properly handled in the workflow."
    )
    await ctx.yield_output(error_msg)