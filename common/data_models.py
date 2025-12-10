from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class ResearchTask(BaseModel):
    """A single research task with subtopic and queries."""
    model_config = ConfigDict(extra="forbid")  # Generates additionalProperties: false
    
    id: str = Field(..., description="Unique identifier for the task")
    subtopic: str = Field(..., description="Subtopic to research")
    search_queries: List[str] = Field(..., description="List of search queries to explore this subtopic")
    completed: bool = Field(..., description="Status of task completion")

class ResearchPlan(BaseModel):
    """Complete research plan with objective, tasks, and success criteria."""
    model_config = ConfigDict(extra="forbid")  # Generates additionalProperties: false
    
    query: str = Field(..., description="The original user query that prompted this research")
    objective: str = Field(..., description="The overall research objective, clearly defined")
    success_criteria: List[str] = Field(..., description="Criteria to determine when the research is sufficiently complete.")
    related_topics: List[str] = Field(..., description="List of related topics that may be useful for the research.")
    research_tasks: List[ResearchTask] = Field(..., description="List of specific research tasks to complete. Each task focuses on a subtopic.")

class Citation(BaseModel):
    """A citation with title and URL."""
    model_config = ConfigDict(extra="forbid")  # Generates additionalProperties: false
    
    title: str
    url: str

class ComprehensiveResearchReport(BaseModel):
    """Complete research report with citations and identified gaps."""
    model_config = ConfigDict(extra="forbid")  # Generates additionalProperties: false
    
    objective: str = Field(..., description="The original research objective")
    success_criteria: List[str] = Field(..., description="Criteria to determine when the research is sufficiently complete.")
    research_report: str = Field(..., description=(
        "Comprehensive research report in markdown. "
        "It should be structured with meaningful headings and subsections, but emphasize **fully-developed paragraphs**. "
        "It should be long and detailed, and it should fully addresses the objectives, "
        "and the various subtopics required to achieve the success criteria. "
        "Use bullet points or lists **only** when they genuinely improve clarity (e.g., summarizing key data). "
        "Tables and other data visualizations are encouraged. "
        "The research report should always be long and detailed.\n\n" 
        "For citations, please use the IEEE (Institute of Electrical and Electronics Engineers). "
        "How it works:\n\n"
        "   1. In the text, use numbered citations in brackets [1].\n"
        "   2. At the end of the report, provide a list of citations in the format "
        "(the list should ONLY contain the sources used in the free text of the research report. "
        "Do NOT list sources which are not cited in the free text of the research report.):\n\n"
        "       [1] Title of the source, URL."
    ))
    citations: List[Citation] = Field(..., description=(
        "List of citations (title and URL), corresponding to references actually used in research_report. "
        "Do not add references that are not cited within the text."
    ))
    identified_gaps: List[str] = Field(..., description="Identified information gaps. Use empty list if none.")
    additional_queries: List[str] = Field(..., description="Suggestions for additional research. Use empty list if none.")

class PeerReviewFeedback(BaseModel):
    """Feedback model for peer review (legacy version)."""
    model_config = ConfigDict(extra="forbid")  # Generates additionalProperties: false
    
    overall_feedback: Optional[str] = Field(default=None, description="General feedback on the report.")
    strengths: Optional[List[str]] = Field(default=None, description="Aspects of the report that are well done.")
    suggested_improvements: Optional[List[str]] = Field(default=None, description="Specific suggestions to improve clarity, completeness, accuracy, or structure.")
    additional_queries: Optional[List[str]] = Field(default=None, description="Additional research queries that could strengthen the report.")
    is_satisfactory: bool = Field(..., description="Indicates if the report meets all quality standards and no further revisions are needed.")
    provided_report: Optional[ComprehensiveResearchReport] = Field(default=None, description="The report that **was** reviewed. Should only be provided if the report needs to be sent back to the Research Agent.")

class NextAction(str, Enum):
    """Enum defining which agent should handle the next step based on peer review feedback."""
    COMPLETE = "complete"  # Report is satisfactory, no further action needed
    REVISE_REPORT = "revise_report"  # Route back to research_report_agent for revision
    GATHER_MORE_DATA = "gather_more_data"  # Route back to search_executor for additional research

class PeerReviewFeedbackMultiChoice(BaseModel):
    """Enhanced peer review feedback model with intelligent routing to specific agents."""
    model_config = ConfigDict(extra="forbid")  # Generates additionalProperties: false
    
    overall_feedback: str = Field(..., description="General feedback on the report.")
    strengths: List[str] = Field(..., description="Aspects of the report that are well done.")
    suggested_improvements: List[str] = Field(..., description="Specific suggestions to improve clarity, completeness, accuracy, or structure. Use empty list if none.")
    additional_queries: List[str] = Field(..., description="Additional research queries that could strengthen the report. Use empty list if none.")
    is_satisfactory: bool = Field(..., description="Indicates if the report meets all quality standards and no further revisions are needed.")
    next_action: NextAction = Field(...)  # OpenAI schema: $ref cannot have description
    next_action_details: str = Field(..., description=(
        "Specific details about what needs to be addressed:\n"
        "- For REVISE_REPORT: Explain what aspects need improvement (e.g., 'Add more analysis in the methodology section')\n"
        "- For GATHER_MORE_DATA: Specify what topics need more research (e.g., 'Need more recent statistics on AI adoption rates')\n"
        "- For COMPLETE: Can be empty string or summary of why report is satisfactory\n"
    ))