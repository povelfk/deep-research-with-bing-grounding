import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

# SearchResultItem: Represents a single search result from the Bing Search API
# Each item contains details about one search result including title, summary content, and source information
class SearchResultItem(BaseModel):
    title: str = Field(..., description="Title of the search result")
    snippet: Optional[str] = Field(None, description="Short summary of the content")
    url: str = Field(..., description="URL of the search result")
    source: Optional[str] = Field(None, description="Name of the source, if available")
    published_date: Optional[str] = Field(None, description="Publication date of the result (if applicable)")

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