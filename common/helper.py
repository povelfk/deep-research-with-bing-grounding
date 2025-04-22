from graphviz import Digraph

def pretty_print_agent_workflow(response):
    """
    Creates a readable visualization of an agent workflow from a response object.
    
    This function generates a structured, human-readable console output that displays
    the entire collaboration workflow between multiple agents, showing:
    - Agent transitions and handoffs
    - Tool calls and their outputs
    - Messages exchanged between agents
    - The final output of the workflow
    
    Each step in the workflow is visualized with appropriate indentation and emoji
    indicators to make the process easy to follow.
    
    Args:
        response: Response object from an OpenAI Agents SDK workflow containing
                 the complete history of agent interactions, tool calls, and outputs
    """
    # Check if there's any workflow data to display
    if not hasattr(response, 'new_items') or not response.new_items:
        print("No workflow items to display")
        return

    # Print workflow header with truncated input for context
    print(f"🔍 AGENT WORKFLOW: '{response.input[:1000]}'\n")
    current_agent = None
    indent = 0
    
    # Process each workflow item in chronological order
    for item in response.new_items:
        item_type = item.type
        
        # Handle agent transitions - display clear visual indicators when a new agent takes over
        if hasattr(item, 'agent') and item.agent.name != current_agent:
            current_agent = item.agent.name
            print(f"\n{'=' * 80}")
            print(f"👤 AGENT: {current_agent}")
            print(f"{'-' * 80}")
            indent = 2  # Increase indentation for actions under this agent
        
        prefix = " " * indent  # Create consistent indentation for readability
        
        # Process different item types with appropriate formatting and emoji indicators
        if item_type == 'tool_call_item':
            # Tool calls - show the tool name and arguments
            tool_name = item.raw_item.name
            try:
                args = item.raw_item.arguments
                print(f"{prefix}🔧 TOOL CALL: {tool_name}({args})")
            except AttributeError:
                print(f"{prefix}🔧 TOOL CALL: {tool_name}")
                
        elif item_type == 'tool_call_output_item':
            # Tool outputs - show truncated results to avoid overwhelming output
            output_text = item.output
            # Truncate long outputs for readability
            if len(output_text) > 100:
                output_text = output_text[:97] + "..."
            print(f"{prefix}📤 TOOL OUTPUT: {output_text}")
            
        elif item_type == 'handoff_call_item':
            # Handoff requests - when one agent delegates to another
            print(f"{prefix}🔄 HANDOFF REQUESTED")
            
        elif item_type == 'handoff_output_item':
            # Completed handoffs - show the transition between agents
            source = item.source_agent.name
            target = item.target_agent.name
            print(f"{prefix}➡️ HANDOFF: {source} -> {target}")
            
        elif item_type == 'message_output_item':
            # Message outputs - natural language responses from agents
            message = item.raw_item.content[0].text
            # Truncate long messages for readability
            if len(message) > 100:
                message_preview = message[:97] + "..."
            else:
                message_preview = message
            print(f"{prefix}💬 OUTPUT: {message_preview}")

    # Display the final output section
    print("\n" + "=" * 80)
    print("🏁 FINAL OUTPUT:")
    print("-" * 80)

    # Handle different types of final outputs (research reports or other formats)
    if hasattr(response.final_output, "research_report"):
        final_text = response.final_output.research_report
    else:
        final_text = str(response.final_output)

    # Truncate long reports for display purposes
    # Only showing the beginning to keep the visualization concise
    print(final_text[:200] + "..." if len(final_text) > 200 else final_text)
    # print(response.final_output)

from graphviz import Digraph

def create_research_workflow_diagram(
    output_filename='research_workflow_diagram', 
    format='png'
):
    """
    Creates and renders the research workflow diagram using Graphviz.

    Args:
        output_filename (str): The base filename for the rendered diagram (no extension).
        format (str): The file format for rendering (e.g., 'png', 'pdf', 'svg').

    Returns:
        Digraph: The created Graphviz Digraph object.
    """
    dot = Digraph(comment='Research Workflow', format=format)

    # Graph attributes
    dot.attr(
        rankdir='LR',
        splines='curved',
        fontname='Helvetica',
        fontsize='14',
        bgcolor='white',
        ranksep='1.2',   # Increased spacing between ranks
        nodesep='0.8'    # Increased spacing between nodes
    )
    dot.attr(
        'graph',
        ratio='compress',
        size='22,10'  # Tweak to taste; adjusts bounding box
    )

    # Node attributes
    dot.attr(
        'node',
        shape='box',
        style='rounded,filled',
        color='#4472C4',
        fillcolor='#E9EEF6',
        fontname='Helvetica',
        fontsize='12',
        fontcolor='#333333'
    )

    # Nodes
    dot.node('user', 'User Query\nInput', shape='ellipse', fillcolor='#D6E9F8')
    dot.node('planner', 'PlannerAgent\nResearch Planning', fillcolor='#CCE5FF')
    dot.node('search', 'BingSearchAgent\nWeb Information Retrieval', fillcolor='#FFEECC')
    dot.node('summary', 'SummaryAgent\nContent Analysis & Summarization', fillcolor='#E6FFE6')
    dot.node('research', 'ResearchAgent\nReport Generation', fillcolor='#E0EAFF')
    dot.node('review', 'PeerReviewAgent\nQuality Evaluation', fillcolor='#FFE6E6')
    dot.node('decision', 'Meets Quality\nStandards?', shape='diamond', fillcolor='#FFF2CC')
    dot.node('report', 'Final Research\nReport', shape='ellipse', fillcolor='#D5F5D5')

    # Main workflow edges
    dot.edge('user', 'planner', label='Query')
    dot.edge('planner', 'search', label='Plan')
    dot.edge('search', 'summary', label='Results')
    dot.edge('summary', 'research', label='Summaries')
    dot.edge('research', 'review', label='Draft')
    dot.edge('review', 'decision', label='Evaluation')
    dot.edge('decision', 'report', label='Yes')

    # Iterative improvement loop
    dot.edge(
        'research', 'decision',
        label='No',
        color='#FF9999',
        constraint='false',
        style='curved',
        dir='back'  # Reverse arrow direction visually
    )

    # Feedback loop cluster
    with dot.subgraph(name='cluster_0') as c:
        c.attr(
            label='Iterative Improvement Loop',
            style='rounded,dashed',
            color='#FF9999',
            penwidth='1.5',
            fontcolor='#666666',
            fontsize='12'
        )
        c.node('research')
        c.node('review')
        c.node('decision')

    # Return the digraph object in case you want to display or manipulate it further
    return dot

def create_research_workflow_diagram_scraper(
    output_filename='research_workflow_diagram_scraper', 
    format='png'
):
    """
    Creates and renders the research workflow diagram using Graphviz.

    Args:
        output_filename (str): The base filename for the rendered diagram (no extension).
        format (str): The file format for rendering (e.g., 'png', 'pdf', 'svg').

    Returns:
        Digraph: The created Graphviz Digraph object.
    """
    dot = Digraph(comment='Research Workflow', format=format)

    # Graph attributes
    dot.attr(
        rankdir='LR',
        splines='curved',
        fontname='Helvetica',
        fontsize='14',
        bgcolor='white',
        ranksep='1.2',   # Increased spacing between ranks
        nodesep='0.8'    # Increased spacing between nodes
    )
    dot.attr(
        'graph',
        ratio='compress',
        size='22,10'  # Tweak to taste; adjusts bounding box
    )

    # Node attributes
    dot.attr(
        'node',
        shape='box',
        style='rounded,filled',
        color='#4472C4',
        fillcolor='#E9EEF6',
        fontname='Helvetica',
        fontsize='12',
        fontcolor='#333333'
    )

    # Nodes
    dot.node('user', 'User Query\nInput', shape='ellipse', fillcolor='#D6E9F8')
    dot.node('planner', 'PlannerAgent\nResearch Planning', fillcolor='#CCE5FF')
    dot.node('search', 'BingSearchAgent\nWeb Information Retrieval', fillcolor='#FFEECC')
    dot.node('scraper', 'ScraperAgent\nData Extraction', fillcolor='#FFF5CC')
    dot.node('summary', 'SummaryAgent\nContent Analysis & Summarization', fillcolor='#E6FFE6')
    dot.node('research', 'ResearchAgent\nReport Generation', fillcolor='#E0EAFF')
    dot.node('review', 'PeerReviewAgent\nQuality Evaluation', fillcolor='#FFE6E6')
    dot.node('decision', 'Meets Quality\nStandards?', shape='diamond', fillcolor='#FFF2CC')
    dot.node('report', 'Final Research\nReport', shape='ellipse', fillcolor='#D5F5D5')

    # Main workflow edges
    dot.edge('user', 'planner', label='Query')
    dot.edge('planner', 'search', label='Plan')
    dot.edge('search', 'scraper', label='Results')
    dot.edge('scraper', 'summary', label='Cleaned Data')
    # dot.edge('search', 'summary', label='Results')
    dot.edge('summary', 'research', label='Summaries')
    dot.edge('research', 'review', label='Draft')
    dot.edge('review', 'decision', label='Evaluation')
    dot.edge('decision', 'report', label='Yes')

    # Iterative improvement loop
    dot.edge(
        'research', 'decision',
        label='No',
        color='#FF9999',
        constraint='false',
        style='curved',
        dir='back'  # Reverse arrow direction visually
    )

    # Feedback loop cluster
    with dot.subgraph(name='cluster_0') as c:
        c.attr(
            label='Iterative Improvement Loop',
            style='rounded,dashed',
            color='#FF9999',
            penwidth='1.5',
            fontcolor='#666666',
            fontsize='12'
        )
        c.node('research')
        c.node('review')
        c.node('decision')

    # Return the digraph object in case you want to display or manipulate it further
    return dot