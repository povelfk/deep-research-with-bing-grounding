import time

from agent_framework import (
    agent_middleware,
    function_middleware
)


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
    print(f"[AgentLoggingMiddleware] 🚀 {agent_name} starting...")
    
    start_time = time.time()
    await next(context)
    duration = time.time() - start_time

    print(f"[AgentLoggingMiddleware] ✅ Agent {agent_name} completed in {duration:.2f}s")

################################ LEGACY VALIDATION MIDDLEWARES ################################

# @agent_middleware
# async def validate_and_parse_research_plan_middleware(context, next):
#     """Agent middleware that validates and parses ResearchPlan output into a Pydantic object."""

#     await next(context)

#     # Handle both streaming (context.result) and non-streaming (context.response)
#     if hasattr(context, 'result') and context.result and hasattr(context.result, 'text'):
#         research_plan = context.result.value
#     elif hasattr(context, 'response') and context.response and hasattr(context.response, 'text'):
#         research_plan = context.response.value
    
#     if research_plan:
#         try:
#             # Store the parsed object
#             context.parsed_output = research_plan
#             print(f"[ResearchPlanValidationMiddleware] ✅ Valid ResearchPlan with {len(research_plan.research_tasks)} tasks")
#         except Exception as e:
#             print(f"[ResearchPlanValidationMiddleware] ❌ Validation failed: {e}")
#             raise ValueError(f"Agent output does not match ResearchPlan schema: {e}")


# @agent_middleware
# async def validate_and_parse_research_report_middleware(context, next):
#     """Agent middleware that validates and parses ComprehensiveResearchReport output into a Pydantic object."""
#     await next(context)

#     # Handle both streaming (context.result) and non-streaming (context.response)
#     if hasattr(context, 'result') and context.result and hasattr(context.result, 'text'):
#         report = context.result.value
#     elif hasattr(context, 'response') and context.response and hasattr(context.response, 'text'):
#         report = context.response.value
    
#     if report:
#         try:           
#             # Store the parsed object
#             context.parsed_output = report
#             print(f"[ResearchReportValidationMiddleware] ✅ Valid ComprehensiveResearchReport")
#         except Exception as e:
#             print(f"[ResearchReportValidationMiddleware] ❌ Validation failed: {e}")
#             raise ValueError(f"Agent output does not match ComprehensiveResearchReport schema: {e}")


# @agent_middleware
# async def validate_and_parse_peer_review_multi_choice_middleware(context, next):
#     """Agent middleware that validates and parses PeerReviewFeedbackMultiChoice output into a Pydantic object."""

#     await next(context)

#     # Handle both streaming (context.result) and non-streaming (context.response)
#     if hasattr(context, 'result') and context.result and hasattr(context.result, 'text'):
#         feedback = context.result.value
#     elif hasattr(context, 'response') and context.response and hasattr(context.response, 'text'):
#         feedback = context.response.value

#     if feedback:
#         try:          
#             # Store the parsed object
#             context.parsed_output = feedback
#             satisfactory_status = "Satisfactory" if feedback.is_satisfactory else "Needs revision"
#             print(f"[PeerReviewMultiChoiceValidationMiddleware] ✅ Valid PeerReviewFeedbackMultiChoice - {satisfactory_status}")
#             print(f"[PeerReviewMultiChoiceValidationMiddleware] ✅ Next action: {feedback.next_action.value}")
#         except Exception as e:
#             print(f"[PeerReviewMultiChoiceValidationMiddleware] ❌ Validation failed: {e}")
#             raise ValueError(f"Agent output does not match PeerReviewFeedbackMultiChoice schema: {e}")
        
################################ LEGACY VALIDATION MIDDLEWARES ################################
