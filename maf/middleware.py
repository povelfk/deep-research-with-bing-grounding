import time

from agent_framework import (
    agent_middleware,
    function_middleware
)


from common.data_models import ResearchPlan, ComprehensiveResearchReport, PeerReviewFeedback

@function_middleware
async def logging_function_middleware(context, next):
    """Function middleware that logs function calls."""
    function_name = context.function.name
    print(f"[LoggingFunctionMiddleware] About to call function: {function_name}.")

    start_time = time.time()
    await next(context)
    duration = time.time() - start_time
    
    print(f"[LoggingFunctionMiddleware] Function {function_name} completed in {duration:.5f}s.")

@agent_middleware
async def simple_logging_agent_middleware(context, next):
    """Simple agent middleware that logs execution."""
    agent_name = context.agent.name if hasattr(context.agent, 'name') else 'Unknown'
    print(f"[AgentMiddleware] 🚀 Agent {agent_name} starting...")
    
    start_time = time.time()
    await next(context)
    duration = time.time() - start_time

    print(f"[AgentMiddleware] ✅ Agent {agent_name} completed in {duration:.2f}s")


@agent_middleware
async def validate_and_parse_research_plan_middleware(context, next):
    """Agent middleware that validates and parses ResearchPlan output into a Pydantic object."""
    agent_name = context.agent.name if hasattr(context.agent, 'name') else 'Unknown'
    print(f"[ResearchPlanMiddleware] Agent {agent_name} starting...")

    start_time = time.time()
    await next(context)
    duration = time.time() - start_time

    # Handle both streaming (context.result) and non-streaming (context.response)
    response_text = None
    if hasattr(context, 'result') and context.result and hasattr(context.result, 'text'):
        response_text = context.result.text
    elif hasattr(context, 'response') and context.response and hasattr(context.response, 'text'):
        response_text = context.response.text
    
    if response_text:
        try:
            # Parse JSON string into ResearchPlan Pydantic object
            research_plan = ResearchPlan.model_validate_json(response_text)
            
            # Store the parsed object in the context for later use
            context.parsed_output = research_plan
            
            print(f"[ResearchPlanMiddleware] ✓ Valid ResearchPlan with {len(research_plan.research_tasks)} tasks")
            print(f"[ResearchPlanMiddleware] ⏱️  Completed in {duration:.2f}s")
        except Exception as e:
            print(f"[ResearchPlanMiddleware] ✗ Validation failed: {e}")
            raise ValueError(f"Agent output does not match ResearchPlan schema: {e}")


@agent_middleware
async def validate_and_parse_research_report_middleware(context, next):
    """Agent middleware that validates and parses ComprehensiveResearchReport output into a Pydantic object."""
    agent_name = context.agent.name if hasattr(context.agent, 'name') else 'Unknown'
    print(f"[ResearchReportMiddleware] Agent {agent_name} starting...")

    start_time = time.time()
    await next(context)
    duration = time.time() - start_time

    # Handle both streaming (context.result) and non-streaming (context.response)
    response_text = None
    if hasattr(context, 'result') and context.result and hasattr(context.result, 'text'):
        response_text = context.result.text
    elif hasattr(context, 'response') and context.response and hasattr(context.response, 'text'):
        response_text = context.response.text
    
    if response_text:
        try:
            # Parse JSON string into ComprehensiveResearchReport Pydantic object
            report = ComprehensiveResearchReport.model_validate_json(response_text)
            
            # Store the parsed object
            context.parsed_output = report
            
            print(f"[ResearchReportMiddleware] ✓ Valid ComprehensiveResearchReport")
            print(f"[ResearchReportMiddleware] ⏱️  Completed in {duration:.2f}s")
        except Exception as e:
            print(f"[ResearchReportMiddleware] ✗ Validation failed: {e}")
            raise ValueError(f"Agent output does not match ComprehensiveResearchReport schema: {e}")


@agent_middleware
async def validate_and_parse_peer_review_middleware(context, next):
    """Agent middleware that validates and parses PeerReviewFeedback output into a Pydantic object."""
    agent_name = context.agent.name if hasattr(context.agent, 'name') else 'Unknown'
    print(f"[PeerReviewMiddleware] Agent {agent_name} starting...")

    start_time = time.time()
    await next(context)
    duration = time.time() - start_time

    # Handle both streaming (context.result) and non-streaming (context.response)
    response_text = None
    if hasattr(context, 'result') and context.result and hasattr(context.result, 'text'):
        response_text = context.result.text
    elif hasattr(context, 'response') and context.response and hasattr(context.response, 'text'):
        response_text = context.response.text
    
    if response_text:
        try:
            # Parse JSON string into PeerReviewFeedback Pydantic object
            feedback = PeerReviewFeedback.model_validate_json(response_text)
            
            # Store the parsed object
            context.parsed_output = feedback
            
            satisfactory_status = "✓ Satisfactory" if feedback.is_satisfactory else "⚠️  Needs revision"
            print(f"[PeerReviewMiddleware] ✓ Valid PeerReviewFeedback - {satisfactory_status}")
            print(f"[PeerReviewMiddleware] ⏱️  Completed in {duration:.2f}s")
        except Exception as e:
            print(f"[PeerReviewMiddleware] ✗ Validation failed: {e}")
            raise ValueError(f"Agent output does not match PeerReviewFeedback schema: {e}")