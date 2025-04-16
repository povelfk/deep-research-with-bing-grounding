from typing import List, Dict, Set, Tuple

def collect_responses_and_citations(subtopic_result: Dict) -> Tuple[List[str], Set[Tuple[str, str]]]:
    """
    Collects all agent text responses and unique citations from a subtopic's query results.

    Args:
        subtopic_result: A dictionary representing the results for a single subtopic,
                         expected to contain a 'queries' key with a list of query results.

    Returns:
        A tuple containing:
        - A list of all agent response strings for the subtopic.
        - A set of unique (title, url) tuples representing the citations.
    """
    all_agent_responses: List[str] = []
    unique_citations: Set[Tuple[str, str]] = set()

    for query_result in subtopic_result.get("queries", []):
        agent_response = query_result.get("agent_response")
        if agent_response:
            all_agent_responses.append(agent_response)

        for result_item in query_result.get("results", []):
            title = result_item.get("title")
            url = result_item.get("url")
            if title and url:
                unique_citations.add( (title, url) )

    return all_agent_responses, unique_citations