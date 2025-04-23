# Deep Research with Bing Search

This project demonstrates an agentic research workflow that leverages Azure AI services to conduct comprehensive web-based research on any topic.

## Project Overview

The system uses specialized AI agents orchestrated together to transform a user query into a comprehensive research report through these steps:

1. **User Query** → User submits research topic or question
2. **Planning** → PlannerAgent develops structured research plan with objectives and subtopics
3. **Information Retrieval** → BingSearchAgent executes targeted web searches for each area
4. **Web Content Scraping** (optional, see below) → ScraperAgent extracts, cleans, and filters relevant content from web pages
5. **Analysis** → SummaryAgent processes results, extracting key insights while preserving technical details
6. **Synthesis** → ResearchAgent creates well-structured report with proper citations
7. **Quality Control** → PeerReviewAgent evaluates report for completeness, clarity, and evidence
8. **Revision** → If needed, research report undergoes improvement cycles based on feedback
9. **Delivery** → Final comprehensive, high-quality report delivered to user

## Notebooks Overview

This repository provides two main notebooks for different research workflows:

- **deep_research_with_bing_search.ipynb**: Demonstrates the core workflow using BingSearchAgent to retrieve and summarize web content. This is suitable for most research tasks where summarized search results are sufficient.

- **deep_research_with_bing_search_scraping.ipynb**: Extends the workflow by introducing a ScraperAgent (WebScraperAgent) that visits URLs returned by BingSearchAgent, extracts and cleans the main content, and then passes this richer data to the summarization and reporting agents. Use this notebook when you need deeper, more contextually relevant information from web pages beyond what is available in search result snippets.

## Features

- **Comprehensive Research Planning**: Break down complex topics into structured subtopics
- **Web Information Retrieval**: Leverage Bing Search for up-to-date information
- **Web Content Scraping**: Extract, clean, and filter main content from web pages for deeper analysis (scraping notebook only)
- **Intelligent Content Analysis**: Extract key insights while preserving technical details
- **Collaborative Agent Workflow**: Multiple specialized agents work together
- **Quality-Focused Peer Review**: Ensure research meets predefined quality standards
- **Iterative Improvement**: Continuous feedback loop until quality thresholds are met
- **Proper Citation Management**: IEEE-style citations for academic rigor

## Technology Stack

- **Azure OpenAI**: Core reasoning capability for all agents
- **Azure AI Agentss Service**: Infrastructure for Bing Search integration
- **OpenAI Agents SDK**: Agent orchestration framework
- **Jupyter Notebooks**: Interactive development environment
- **Python-based Web Scraping (Trafilatura, requests, custom logic)**: Used by the WebScraperAgent to extract, clean, and filter main content from web pages

## Getting Started

### Prerequisites

- Azure subscription with access to Azure OpenAI + Bing Resource
- Azure AI Projects connection
- Python 3.8+

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in a `.env` file:
   ```
   AOAI_ENDPOINT=your_azure_openai_endpoint
   AOAI_KEY=your_azure_openai_key
   PROJECT_CONNECTION_STRING=your_project_connection_string
   BING_CONNECTION_NAME=your_bing_connection_name
   bingSearchAgentID=your_bing_search_agent_id
   ```

### Running the Project

1. Open and run either `deep_research_with_bing_search.ipynb` or `deep_research_with_bing_search_scraping.ipynb` in a Jupyter environment:
   - Use `deep_research_with_bing_search.ipynb` for standard research workflows using only Bing search results.
   - Use `deep_research_with_bing_search_scraping.ipynb` for enhanced workflows that scrape and analyze the full content of web pages for deeper insights.
2. Follow the cells in sequence to execute the full research workflow.
3. Modify the `user_query` variable to research different topics.

## Project Structure

- `deep_research_with_bing_search.ipynb`: Main notebook with the standard workflow (Bing search only)
- `deep_research_with_bing_search_scraping.ipynb`: Enhanced workflow with web scraping for deeper content extraction
- `common/`: Shared utility modules
  - `helper.py`: Helper functions for visualization and workflow display
  - `utils_search.py`: Search result parsing utilities
  - `utils_research.py`: Research data processing functions
  - `utils_scraping.py`: Web scraping utilities
  - `utils_summary.py`: Summarization utilities
- `requirements.txt`: Project dependencies

## Agent Architecture

The workflow combines these specialized agents:

- **PlannerAgent**: Creates comprehensive research plans with subtopics and queries
- **BingSearchAgent**: Retrieves relevant search results from the web
- **WebScraperAgent**: Extracts, cleans, and filters relevant content from web pages (scraping notebook only)
- **SummaryAgent**: Extracts key insights from retrieved or scraped content
- **ResearchAgent**: Compiles findings into structured research reports
- **PeerReviewAgent**: Provides quality feedback in a continuous improvement loop