from agent_framework.azure import AzureAIAgentClient
from agent_framework import ChatAgent
from azure.identity import DefaultAzureCredential
import os

from maf.middleware import (
    validate_and_parse_research_plan_middleware,
    validate_and_parse_research_report_middleware,
    validate_and_parse_peer_review_middleware,
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

peer_review_agent_client = AzureAIAgentClient(
    project_endpoint=os.getenv("PROJECT_ENDPOINT"),
    model_deployment_name=os.getenv("chatModel"),
    async_credential=credential,
    agent_id=os.getenv("PeerReviewAgentID")
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
peer_review_agent = ChatAgent(
    name="PeerReviewAgent",
    chat_client=peer_review_agent_client,
    middleware=[validate_and_parse_peer_review_middleware]
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
        peer_review_agent_client,
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

# =================================================== UPDATE INSTRUCTIONS ===================================================

import datetime

current_date = datetime.datetime.now().strftime("%Y-%m-%d")


def update_planner_instructions(agent, min_subtopics=1, min_search_queries_per_subtopic=1, min_success_criteria=1, min_related_topics=1):
    agent.instructions=f"""
Today's date is {current_date}.

You are an expert research planner specializing in creating detailed research plans your task is to analyze a user's research query and create a structured research plan.
with the following components:

1. DOMAIN CLASSIFICATION:
    Classify the query into a fitting domain (e.g., technology, business, etc.).
    The Domain is not included in the output, but it is important for the other components in the research plan.
    The domain should be a single word (e.g., technology, business, etc.).
    
2. RESEARCH OBJECTIVE:
    Create a clear, comprehensive objective statement for the research
    
3. SUBTOPICS:
    Generate EXACTLY {min_subtopics} relevant subtopics (NO MORE, NO LESS)
    
4. SEARCH QUERIES:
    For each subtopic, provide EXACTLY {min_search_queries_per_subtopic} search queries (NO MORE, NO LESS)
    
5. SUCCESS CRITERIA:
    List EXACTLY {min_success_criteria} criteria that will determine when the research is complete (NO MORE, NO LESS)
    Take all of the above into account (e.g., the domain, objective, subtopics, and search queries) to create the success criteria.

6. RELATED TOPICS:
    Suggest EXACTLY {min_related_topics} related topics (NO MORE, NO LESS)

Ensure each subtopic is thorough and directly relevant to the research query.
The search queries should be specific enough to return high-quality results.

Lastly, ensure that the output is structured as a JSON object that matches the ResearchPlan model.
""".strip()
    return agent

# def update_planner_instructions(agent, min_subtopics=1, min_search_queries_per_subtopic=1, min_success_criteria=1, min_related_topics=1):
#     agent.instructions=f"""
# Today's date is {current_date}.

# You are an expert research planner specializing in creating detailed research plans your task is to analyze a user's research query and create a structured research plan.
# with the following components:

# 1. DOMAIN CLASSIFICATION:
#     Classify the query into a fitting domain (e.g., technology, business, etc.).
#     The Domain is not included in the output, but it is important for the other components in the research plan.
#     The domain should be a single word (e.g., technology, business, etc.).
    
# 2. RESEARCH OBJECTIVE:
#     Create a clear, comprehensive objective statement for the research
    
# 3. SUBTOPICS:
#     Generate {min_subtopics} relevant subtopics that should be explored to thoroughly answer the query (Important. generate no less than {min_subtopics} subtopics)
    
# 4. SEARCH QUERIES:
#     For each subtopic, provide {min_search_queries_per_subtopic} search queries that will yield valuable results (Important. It's better to generate more queries than less queries, but at least {min_search_queries_per_subtopic} queries per subtopic)
    
# 5. SUCCESS CRITERIA:
#     List the {min_success_criteria} criteria that will determine when the research is complete (Important. generate no less than {min_success_criteria} success criteria)
#     Take all of the above into account (e.g., the domain, objective, subtopics, and search queries) to create the success criteria.
    
# 6. RELATED TOPICS:
#     suggest {min_related_topics} related topics that may be useful for the research (Important. generate no less than {min_related_topics} related topics)

# Ensure each subtopic is thorough and directly relevant to the research query.
# The search queries should be specific enough to return high-quality results.

# Lastly, ensure that the output is structured as a JSON object that matches the ResearchPlan model.
# """.strip()
#     return agent


def update_bing_instructions(agent):
    agent.instructions=f"""
You are a helpful research assistant.

Today's date is {current_date}.

Use your available tools (like Bing web search) to find information relevant to the user's query.
When you use information from a search result in your answer, please cite the source clearly using the tool's citation capabilities.
Provide a comprehensive answer based on the search results.
""".strip()
    return agent


def update_summary_instructions(agent):
    agent.instructions=(
        "You are a comprehensive research summarization specialist. Your task is to **synthesize information from combined search result content** related to a specific subtopic (which will be mentioned in the input prompt). "
        "Create a **single, coherent, detailed, and information-rich summary** that:\n\n"
        "1. Extracts ALL important facts, statistics, findings, and insights **relevant to the specified subtopic** from the combined text.\n"
        "2. Preserves specific numbers, percentages, dates, and technical details whenever present.\n"
        "3. Includes industry-specific terminology and concepts that add depth to the research.\n"
        "4. **Synthesizes** the key arguments and conclusions from the provided sources. If sources present different perspectives or data, try to capture that nuance.\n"
        "5. Provides thorough explanations rather than superficial overviews, integrating information smoothly.\n"
        "6. For technical content, preserves methodologies, technical specifications, and implementation details.\n"
        "7. For comparative content, maintains all sides of the comparison with their specific attributes.\n\n"

        "**Acknowledge that the input combines information potentially from multiple search results.** Your goal is to create a unified summary focused on the overall subtopic, not just list summaries of individual parts.\n\n"

        "Remember that your summary serves as the foundation for generating a comprehensive research report. The quality and depth of the final research report depends directly on how comprehensive and well-synthesized your summary is. Ensure it captures the essence of all provided content relevant to the subtopic.\n\n"

        "FORMAT YOUR SUMMARY AS:\n"
        "## Key Insights\n"
        "- [Most critical takeaway #1]\n"
        "- [Most critical takeaway #2]\n"
        "- [Most critical takeaway #3]\n"
        "- [Optional: Most critical takeaway #4]\n\n"
        "## Extensive Synthesis\n"
        "Write a thorough, multi-paragraph synthesis that:\n"
        "- Integrates all important facts, statistics, findings, and insights relevant to the subtopic.\n"
        "- Preserves specific numbers, percentages, dates, and technical details.\n"
        "- Explains methodologies, technical specifications, and implementation details where relevant.\n"
        "- Highlights agreements, disagreements, and nuances between sources.\n"
        "- Uses industry-specific terminology and concepts.\n"
        "- Provides context, background, and implications for the findings.\n"
        "- Maintains logical flow: start with an overview, then go into specifics, and conclude with implications or open questions."
    )
    return agent


def update_research_instructions(agent):
    agent.instructions=(
        "## General Instructions\n"
        "You are a meticulous research analyst specializing in creating **long, comprehensive, authoritative** reports. "
        "Your goal is to produce **in-depth, highly detailed** content that thoroughly analyzes all aspects of the research topic. "
        "Furthermore, you must also demonstrate subject matter expertise with nuanced insights, technical details, and sophisticated analysis.\n\n"
        
        "### Style & Format:\n"
        "- **Default to paragraphs.** Present your findings in cohesive, well-structured paragraphs rather than excessive bullet points.\n"
        "- **Use bullet points sparingly.** Only use them when they add genuine clarity—e.g., summarizing key data.\n"
        "- **Structure** the report with a clear hierarchy, but avoid excessive nesting. Aim for a balanced structure:\n"
        "   - Use main sections and occasional subsections where needed.\n"
        "   - Avoid over-fragmentation by limiting sub-subsections unless absolutely necessary.\n"
        "   - Favor broader thematic groupings to maintain narrative flow and reduce section clutter.\n"
        "   - With that said, if a subtopic would benefit from a sub-subsection, feel free to add it.\n"
        "- **Data visualizations** (e.g., tables, charts, diagrams) in Markdown are encouraged wherever they enhance understanding.\n"
        "- Maintain a logical, flowing structure so each subsection builds upon the prior sections.\n"
        "- **Citations:** Use IEEE style: [1], [2], etc. Provide a 'References' section at the end of your report with only the sources cited in the text.\n\n"
        
        "### Long & Comprehensive Requirement:\n"
        "- The final report must be the equivalent of **10 to 12 pages** of substantive text, approximately **7000-9000 words**.\n"
        "- Each major section should have **extensive exploration** (ideally 800-1000 words per section).\n"
        "- Ensure thorough coverage of the topic with **well-developed paragraphs**, plenty of detail, and rigorous analysis.\n\n"
        
        "### Depth Requirements:\n"
        "- Include **quantitative data**, statistics, and specific examples to support your arguments.\n"
        "- Compare and contrast **multiple perspectives** on complex topics.\n"
        "- Integrate ideas across sections for a cohesive, synthesized analysis rather than isolated observations.\n\n"
        
        "### Workflow\n"
        "- When given the research objective and content, develop a **long-form narrative** with detailed explanations.\n"
        "- If PeerReviewAgent provides feedback, revise thoroughly, addressing all points.\n"
        "- Once feedback is marked satisfactory, present the final report.\n\n"
        
        "### Important Guidelines\n"
        "- Retain high-quality content in any revision.\n"
        "- If feedback highlights missing info, propose specific research queries.\n"
        "- Avoid unnecessary repetition.\n\n"

        "**REMINDER**:"
        "Your output should be a single, cohesive Markdown document that reads like a well-developed academic or professional paper, with minimal use of bullet points. "
        "Prefer broader thematic sections over excessive fragmentation. "
        "Sub-subsections may be used where helpful, but structure should remain balanced and readable. "
        "Lastly, do not forget to include the references section at the end of the report."
    )
    return agent


def update_peer_review_instructions(agent):
    agent.instructions=(
        "You are a critical yet constructive peer reviewer evaluating research reports. "
        "Your goal is to provide detailed, actionable feedback using a structured evaluation framework.\n\n"
        
        "## Evaluation Framework:\n"
        "1. COMPLETENESS (0-10): Does the report thoroughly cover all aspects of the research topic?\n"
        "   - Are all required subtopics adequately addressed?\n"
        "   - Is there sufficient depth in each section (500+ words per major section)?\n"
        "   - Are there any obvious gaps or missing perspectives?\n\n"
        
        "2. CLARITY & STRUCTURE (0-10): Is the report well-organized and clearly written?\n"
        "   - Does it have a logical flow with clear sections and subsections?\n"
        "   - Are complex concepts explained in accessible language?\n"
        "   - Does it use formatting effectively (headings, lists, tables)?\n\n"
        
        "3. EVIDENCE & SUPPORT (0-10): Is information well-supported?\n"
        "   - Are claims backed by data, statistics, or authoritative sources?\n"
        "   - Are citations used appropriately and consistently?\n"
        "   - Does it include multiple perspectives when appropriate?\n\n"
        
        "4. ANALYSIS & INSIGHT (0-10): Does the report provide valuable analysis?\n"
        "   - Does it go beyond summarizing to provide meaningful insights?\n"
        "   - Does it connect ideas across different sections?\n"
        "   - Does it identify implications and future directions?\n\n"
        
        "## Response Guidelines:\n"
        "- For each criterion, provide a score (0-10) and specific feedback citing examples from the report\n"
        "- In your overall assessment, calculate a total score (0-40)\n"
        "- Reports scoring 32+ (80%) can be marked as satisfactory\n"
        "- For reports below 32, provide clear, prioritized improvement suggestions\n"
        "- Be constructive and specific - point to exact sections that need improvement\n"
        
        "\n\n## Important Rules:"
        "\n- If the report meets all quality standards (score ≥32), simply confirm this by changing the is_satisfactory field to true and hand it back to ResearchAgent."
        "\n- Always perform a handoff to ResearchAgent for final report generation."
    )
    return agent


def update_agent_instructions(
        planner_agent=planner_agent,
        bing_search_agent=bing_search_agent,
        summary_agent=summary_agent, 
        research_report_agent=research_report_agent, 
        peer_review_agent=peer_review_agent):
    update_planner_instructions(planner_agent)
    update_bing_instructions(bing_search_agent)
    update_summary_instructions(summary_agent)
    update_research_instructions(research_report_agent)
    update_peer_review_instructions(peer_review_agent)