def preprocess_research_data(plan, mapped_chunks):
    """
    Enhances raw research data with guidance for comprehensive reports while allowing agent to determine structure.
    
    This function takes the research plan and summarized search results as input, then creates a structured
    input format for the ResearchAgent to use when generating the final research report. It provides
    high-level guidance without prescribing rigid section formats, allowing the AI to organize content
    based on the natural relationships in the data.
    
    Args:
        plan: The ResearchPlan object containing objectives, tasks, and success criteria
        mapped_chunks: A list of dictionaries containing summarized search results organized by subtopic
        
    Returns:
        dict: A structured input for the ResearchAgent with all necessary content and guidance
              for generating a comprehensive research report
    """
    
    # Extract core data from plan - create a clean list of subtopics for easier reference
    subtopics_list = [task.subtopic for task in plan.final_output.research_tasks]
    
    # Create guidance for data visualizations without dictating specific sections
    # These suggestions encourage the agent to include visuals that enhance understanding
    visualization_suggestions = [
        "Timeline of major developments",
        "Comparison table of competing technologies/approaches",
        "Hierarchical breakdown of components/elements",
        "Impact assessment matrix across different industries",
        "Statistical charts showing adoption rates or performance metrics"
    ]
    
    # Create the enhanced input for the research agent - excluding predefined sections
    # This structure provides content and guidance while preserving creative flexibility
    research_input = {
        "objective": plan.final_output.objective,               # The main research goal
        "aggregated_summaries": mapped_chunks,                  # Organized research content by subtopic
        "success_criteria": plan.final_output.success_criteria, # Metrics to ensure research completeness
        "subtopics": subtopics_list,                            # List of all research subtopics
        "data_visualization_opportunities": visualization_suggestions, # Ideas for visual elements
        
        # Guidance on overall document organization (flexible, not template-based)
        "structural_guidance": (
            "Analyze the research content and determine the most logical and effective structure for the report. "
            "Favor broad thematic sections OVER overly fragmented structures. "
            "Use subsections only where helpful, and limit sub-subsections to a MINIMUM."
            "Sub-subsections should only be used in cases where they genuinely improve clarity. Ensure all subtopics are thoroughly covered in a coherent, well-integrated narrative."
        ),
        # Guidance on expected depth and length
        "depth_requirements": (
            "Create an in-depth, comprehensive, and authoritative report with substantial detail in each major section. "
            "The final report should be equivalent to 8-10 pages (approximately 4000-5000 words), with a focus on deep analysis, "
            "paragraph-based structure, and integrated argumentation."
        ),
    }
    
    return research_input