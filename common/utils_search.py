import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from azure.ai.projects.models import MessageRole

# SearchResultItem: Represents a single search result from the Bing Search API
# Each item contains details about one search result including title, summary content, and source information
class SearchResultItem(BaseModel):
    title: str = Field(..., description="Title of the search result")
    full_text: str = Field(..., description="The complete content retrieved from the search result")
    url: str = Field(..., description="URL of the search result")
    source: Optional[str] = Field("", description="Name of the source, if available")
    published_date: Optional[str] = Field("", description="Publication date of the result (if applicable)")

# SearchResults: Contains all search results for a specific subtopic and query
# Groups multiple search result items under the relevant subtopic and query
class SearchResults(BaseModel):
    subtopic: str = Field(..., description="The research subtopic for which the results apply")
    query: str = Field(..., description="The search query used to fetch these results")
    results: List[SearchResultItem] = Field(..., description="List of search result items for this subtopic")

def parse_search_results(text_response):
    """
    Parses JSON search results from the Bing Search Agent's text response.
    
    This function handles extracting valid JSON from potentially messy text responses,
    then validates and converts that JSON into a strongly-typed SearchResults object.
    
    Args:
        text_response (str): The raw text response from the Bing Search Agent
        
    Returns:
        SearchResults: A validated object containing the structured search results
                       If parsing fails, returns a SearchResults object with empty results
    """
    try:
        # Extract JSON if the response contains additional text around the JSON
        json_match = re.search(r'({[\s\S]*})', text_response)
        json_str = json_match.group(1) if json_match else text_response
        
        # Parse and validate the JSON against our Pydantic model schema
        return SearchResults.model_validate_json(json_str)
        
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Error parsing search results: {e}")
        # Return fallback results with empty data to avoid breaking the workflow
        return SearchResults(
            subtopic="Unknown",
            query="Unknown",
            results=[]
        )

def extract_agent_response_and_urls(project_client, thread_id, query):
    """
    Extracts the agent's text response and cited URLs from the last agent message in a thread.
    """
    extracted_urls = []
    agent_response_text = ""

    messages = project_client.agents.list_messages(thread_id=thread_id)
    last_agent_message = messages.get_last_message_by_role(role=MessageRole.AGENT)

    if last_agent_message:
        if last_agent_message.text_messages:
            agent_response_text = "\n".join([tm.text.value for tm in last_agent_message.text_messages])
        if last_agent_message.url_citation_annotations:
            for annotation in last_agent_message.url_citation_annotations:
                if hasattr(annotation, 'url_citation') and annotation.url_citation:
                    extracted_urls.append({
                        "title": annotation.url_citation.title or "No Title",
                        "url": annotation.url_citation.url
                    })
                else:
                    print(f"Warning: Annotation found without valid url_citation for query '{query}'")
    return agent_response_text, extracted_urls