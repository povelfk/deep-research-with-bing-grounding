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

## Notebooks & Workflows

This repository provides three notebooks and one Python workflow for different research implementations:

- **01_deep_research_with_bing_search.ipynb**: Demonstrates the core workflow using BingSearchAgent to retrieve and summarize web content. This is suitable for most research tasks where summarized search results are sufficient.

- **02_deep_research_with_bing_search_scraping.ipynb**: Extends the workflow by introducing a ScraperAgent (WebScraperAgent) that visits URLs returned by BingSearchAgent, extracts and cleans the main content, and then passes this richer data to the summarization and reporting agents. Use this notebook when you need deeper, more contextually relevant information from web pages beyond what is available in search result snippets.

- **03_deep_research_with_azure_ai_agents_only.ipynb**: Features a **pure Azure AI Agents implementation** with custom agent-to-agent handoffs and iterative loops between ResearchAgent and PeerReviewAgent. Unlike the other notebooks that use a hybrid approach, this notebook demonstrates how to build the entire research workflow using **Azure AI Agents exclusively**, including automated peer review cycles that continue until quality standards are met through a custom `loop_agents` function.

- **04_deep_research_with_agent_framework.py**: Deep Research workflow using **Microsoft Agent Framework** with switch-case routing, shared state management and structured multi-choice decision making. Peer review feedback automatically routes to completion, report revision, or additional data gathering.

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
- **Microsoft Agent Framework**: Workflow orchestration with switch-case routing (workflow 04)
- **Azure AI Agents**: Exclusive agent orchestration platform (notebook 03)
- **OpenAI Agents SDK + Azure AI Agents**: Hybrid orchestration approach (notebooks 01 & 02, with Azure AI Agents used specifically for Bing Search integration)
- **Azure AI Projects Service**: Infrastructure for Bing Search integration
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

Choose one of the three notebooks or the Python workflow:

**Notebooks (Interactive):**
1. Open one of the three notebooks in a Jupyter environment:
   - Use `01_deep_research_with_bing_search.ipynb` for standard research workflows using the hybrid OpenAI Agents SDK + Azure AI Agents approach.
   - Use `02_deep_research_with_bing_search_scraping.ipynb` for enhanced workflows that scrape and analyze the full content of web pages for deeper insights using the hybrid approach.
   - Use `03_deep_research_with_azure_ai_agents_only.ipynb` for pure Azure AI Agents implementation with custom agent orchestration and automated peer review loops.
2. Follow the cells in sequence to execute the full research workflow.
3. Modify the `user_query` variable to research different topics.

**Python Workflow:**
1. Run `python 04_deep_research_with_agent_framework.py` for execution with Agent Framework orchestration.
2. Edit the `user_query` variable in the file to research different topics.

## Project Structure

- `01_deep_research_with_bing_search.ipynb`: Main notebook with the standard workflow (hybrid OpenAI Agents SDK + Azure AI Agents approach)
- `02_deep_research_with_bing_search_scraping.ipynb`: Enhanced workflow with web scraping for deeper content extraction (hybrid approach)
- `03_deep_research_with_azure_ai_agents_only.ipynb`: Pure Azure AI Agents implementation with custom agent orchestration and automated peer review loops
- `04_deep_research_with_agent_framework.py`: Workflow with Microsoft Agent Framework, switch-case routing, and iteration limits
- `common/`: Shared utility modules
  - `create_azure_ai_agents.py`: Functions for creating and configuring Azure AI Agents
  - `data_models.py`: Data models and structures used across the project
  - `helper.py`: Helper functions for visualization and workflow display
  - `update_instructions.py`: Utilities for updating agent instructions and configurations
  - `utils_ai_agents.py`: Azure AI Agents utilities for agent orchestration
  - `utils_research.py`: Research data processing functions
  - `utils_scraping.py`: Web scraping utilities
  - `utils_search.py`: Search result parsing utilities
  - `utils_summary.py`: Summarization utilities
- `maf/`: Agent Framework modules (workflow 04)
  - `agents.py`: Agent definitions with Azure AI clients
  - `nodes.py`: Workflow executors for search, summary, report generation, and routing
  - `middleware.py`: Validation and parsing for agent responses
  - `update_agent_instructions.py`: Agent instruction management
- `requirements.txt`: Project dependencies

## Agent Architecture

The workflow combines these specialized agents:

- **PlannerAgent**: Creates comprehensive research plans with subtopics and queries
- **BingSearchAgent**: Retrieves relevant search results from the web
- **WebScraperAgent**: Extracts, cleans, and filters relevant content from web pages (scraping notebook only)
- **SummaryAgent**: Extracts key insights from retrieved or scraped content
- **ResearchAgent**: Compiles findings into structured research reports
- **PeerReviewAgent**: Provides quality feedback in a continuous improvement loop
- **PeerReviewAgentMultiChoice** (workflow 04): Enhanced peer review with intelligent routing decisions that automatically directs workflow to completion, report revision, or additional data gathering based on structured feedback analysis