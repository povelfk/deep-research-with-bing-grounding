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
                unique_citations.add((title, url))

    return all_agent_responses, unique_citations


def collect_contents_and_citations(subtopic_result, scraped_content_by_url):
    """
    For a given subtopic, collect all available scraped content and citation information.

    Args:
        subtopic_result: A dictionary representing a subtopic, containing queries and their results.
        scraped_content_by_url: A dictionary mapping URLs to their scraped main content.

    Returns:
        contents: A list of tuples (content, title, url) for all successfully scraped webpages in this subtopic.
        citations: A list of dictionaries with 'title' and 'url' for citation/reference purposes.
    """
    contents = []
    citations = []
    for query_result in subtopic_result["queries"]:
        for search_result_item in query_result["results"]:
            url = search_result_item["url"]
            content = scraped_content_by_url.get(url)
            if not content:
                continue
            contents.append((content, search_result_item["title"], url))
            citations.append({
                "title": search_result_item["title"],
                "url": url
            })
    return contents, citations

async def summarize_content(contents, summary_agent, Runner, per_webpage):
    """
    Summarize the provided contents either per webpage or as a combined subtopic summary.

    Args:
        contents: A list of (content, title, url) tuples to be summarized.
        summary_agent: The agent to use for generating summaries.
        Runner: The runner object responsible for executing the agent.
        per_webpage: Boolean flag. If True, summarize each webpage individually.
                     If False, summarize all content together as one subtopic.

    Returns:
        If per_webpage is True: a list of summary strings, one for each content item.
        If per_webpage is False: a single summary string for the entire subtopic.
    """
    if per_webpage:
        summaries = []
        for content, title, url in contents:
            summary_response = await Runner().run(
                starting_agent=summary_agent,
                input=f"Summarize the following content:\n{content}"
            )
            summaries.append(summary_response.final_output)
        return summaries
    else:
        if not contents:
            return "No content found to summarize for this subtopic."
        content_to_summarize = "\n\n---\n\n".join([c[0] for c in contents])
        summary_prompt = f"Summarize the following information:\n\n{content_to_summarize}"
        summary_response = await Runner().run(
            starting_agent=summary_agent,
            input=summary_prompt
        )
        return summary_response.final_output