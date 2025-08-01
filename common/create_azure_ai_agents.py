from azure.ai.agents.models import BingGroundingTool
import datetime
import os

def create_research_plan_agent(project_client):
    """
    Create an agent that generates detailed research plans based on user queries.
    """
    from azure.ai.agents.models import ResponseFormatJsonSchema
    from common.data_models import ResearchPlan

    # Create the response format object
    response_format = ResponseFormatJsonSchema(
        name="ResearchPlan",
        schema=ResearchPlan.model_json_schema()
    )
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    planner_agent = project_client.agents.create_agent(
        name="ResearchPlanAgent",
        description="An agent that creates detailed research plans based on user queries.",
        model=os.getenv("chatModel"),
        temperature=0.5,
        response_format={
            "type": "json_schema",
            "json_schema": response_format
        },
        instructions=f"""
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
    Generate relevant subtopics that should be explored to thoroughly answer the query (Important. generate no less than 5 subtopics)
    
4. SEARCH QUERIES:
    For each subtopic, provide search queries that will yield valuable results (Important. It's better to generate more queries than less queries, but at least 3 queries per subtopic)
    
5. SUCCESS CRITERIA:
    List the criteria that will determine when the research is complete (Important. generate no less than 4 success criteria)
    Take all of the above into account (e.g., the domain, objective, subtopics, and search queries) to create the success criteria.
    
6. RELATED TOPICS:
    suggest related topics that may be useful for the research (Important. generate no less than 3 related topics)

Ensure each subtopic is thorough and directly relevant to the research query.
The search queries should be specific enough to return high-quality results.

Lastly, ensure that the output is structured as a JSON object that matches the ResearchPlan model.
""".strip(),
    )
    return planner_agent


def create_bing_search_agent(project_client):
    """
    Create an agent that uses Bing for web searches.
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    bing_connection = project_client.connections.get(
        name=os.getenv("BING_CONNECTION_NAME")
    )
    bing_tool = BingGroundingTool(connection_id=bing_connection.id)

    bing_search_agent = project_client.agents.create_agent(
        name="BingSearchAgent",
        description="Agent to perform web searches using Bing.",
        model=os.getenv("chatModel"),
        temperature=0.5,
        tools=bing_tool.definitions,
        instructions=f"""
    You are a helpful research assistant.

    Today's date is {current_date}.

    Use your available tools (like Bing web search) to find information relevant to the user's query.
    When you use information from a search result in your answer, please cite the source clearly using the tool's citation capabilities.
    Provide a comprehensive answer based on the search results.
        """.strip()
    )
    return bing_search_agent


def create_summary_agent(project_client):
    """
    Create an agent that summarizes web search results.
    """
        
    summary_agent = project_client.agents.create_agent(
        name="SummaryAgent",
        description="An agent that summarizes research reports.",
        model=os.getenv("chatModel"),
        temperature=1.0,
        instructions=(
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
    )
    return summary_agent

def create_research_report_agent(project_client):
    """
    Create an agent that generates comprehensive research reports.
    """
    from azure.ai.agents.models import ResponseFormatJsonSchema
    from common.data_models import ComprehensiveResearchReport

    # Create the response format object
    response_format = ResponseFormatJsonSchema(
        name="ResearchPlan",
        schema=ComprehensiveResearchReport.model_json_schema()
    )

    report_agent = project_client.agents.create_agent(
        name="ResearchReportAgent",
        description="An agent that generates comprehensive research reports.",
        model=os.getenv("chatModel"),
        temperature=0.3,
        response_format={
            "type": "json_schema",
            "json_schema": response_format
        },
        instructions=(
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
    )
    return report_agent

def create_peer_review_agent(project_client):
    """
    Create an agent that performs peer review on research reports.
    """
    from azure.ai.agents.models import ResponseFormatJsonSchema
    from common.data_models import PeerReviewFeedback

    response_format = ResponseFormatJsonSchema(
        name="ResearchPlan",
        schema=PeerReviewFeedback.model_json_schema()
    )

    peer_review_agent = project_client.agents.create_agent(
        name="PeerReviewAgent",
        description="An agent that provides peer review feedback on research reports.",
        model=os.getenv("chatModel"),
        temperature=0.5,
        response_format={
            "type": "json_schema",
            "json_schema": response_format
        },
        instructions=(
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
    )
    return peer_review_agent