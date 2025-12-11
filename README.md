# Deep Research with Bing Search

This project demonstrates an agentic research workflow that leverages Azure AI services to conduct comprehensive web-based research on any topic.

> **Note:** This project supports both **Azure AI Agents v1** and **v2** SDKs. Notebooks 01-04 use the v1 SDK, while notebook 05 uses the latest v2 SDK.

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

This repository provides four notebooks and one Python workflow for different research implementations:

- **01_deep_research_with_bing_search.ipynb**: Demonstrates the core workflow using BingSearchAgent to retrieve and summarize web content. This is suitable for most research tasks where summarized search results are sufficient.

- **02_deep_research_with_bing_search_scraping.ipynb**: Extends the workflow by introducing a ScraperAgent (WebScraperAgent) that visits URLs returned by BingSearchAgent, extracts and cleans the main content, and then passes this richer data to the summarization and reporting agents. Use this notebook when you need deeper, more contextually relevant information from web pages beyond what is available in search result snippets.

- **03_deep_research_with_azure_ai_agents_only.ipynb**: Features a **pure Azure AI Agents implementation** with custom agent-to-agent handoffs and iterative loops between ResearchAgent and PeerReviewAgent. Unlike the other notebooks that use a hybrid approach, this notebook demonstrates how to build the entire research workflow using **Azure AI Agents exclusively**, including automated peer review cycles that continue until quality standards are met through a custom `loop_agents` function.

- **04_deep_research_with_agent_framework.ipynb**: Deep Research workflow using **Microsoft Agent Framework** with switch-case routing, shared state management and structured multi-choice decision making. Peer review feedback automatically routes to completion, report revision, or additional data gathering. Uses Azure AI Agents v1 SDK.

- **05_deep_research_with_agent_framework_v2.ipynb**: same workflow as notebook 04, but using the new **Azure AI Agents v2 SDK**.

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
- **Microsoft Agent Framework**: Workflow orchestration with switch-case routing (notebooks 04 & 05)
- **Azure AI Agents v1 SDK**: Agent orchestration platform (notebooks 01-04)
- **Azure AI Agents v2 SDK**: Latest agent orchestration with improved response handling (notebook 05)
- **OpenAI Agents SDK + Azure AI Agents**: Hybrid orchestration approach (notebooks 01 & 02, with Azure AI Agents used specifically for Bing Search integration)
- **Azure AI Projects Service**: Infrastructure for Bing Search integration
- **Jupyter Notebooks**: Interactive development environment
- **Python-based Web Scraping (Trafilatura, requests, custom logic)**: Used by the WebScraperAgent to extract, clean, and filter main content from web pages

## Getting Started

### Prerequisites

- Azure subscription with access to:
  - **Azure OpenAI** with a deployed model (e.g., `gpt-5`) - The scripts create agents but do **not** deploy models
  - **Azure AI Foundry** project with a Bing Grounding tool connection already configured - The scripts do **not** create the Grounding with Bing Search resource.
- Azure AI Projects connection
- Python 3.8+

### Installation

1. Clone this repository
2. Install dependencies for your chosen notebook:
   ```bash
   # For notebook 01
   pip install -r requirements/01_deep_research_with_bing_search_requirements.txt
   
   # For notebook 02
   pip install -r requirements/02_deep_research_with_bing_search_scraping_requirements.txt
   
   # For notebook 03
   pip install -r requirements/03_deep_research_with_azure_ai_agents_only_requirements.txt
   
   # For notebook 04
   pip install -r requirements/04_deep_research_with_agent_framework_requirements.txt
   
   # For notebook 05
   pip install -r requirements/05_deep_research_with_agent_framework_requirements.txt
   ```
3. Configure environment variables in a `.env` file. Required variables differ by notebook:
   - **Notebooks 01 & 02** (OpenAI Agents SDK + Azure AI Agents): Create agents inline except for Bing Search
   - **Notebook 03** (Azure AI Agents only): Requires pre-created agents via `00_create_agents.py`
   - **Workflow 04** (Agent Framework): Requires pre-created agents via `00_create_agents.py`
   
   See the first cell of each notebook for specific environment variable requirements.

### Running the Project

Choose one of the notebooks or the Python workflow:

**Notebooks (Interactive):**
1. Open one of the notebooks in a Jupyter environment:
   - Use `01_deep_research_with_bing_search.ipynb` for standard research workflows using the hybrid OpenAI Agents SDK + Azure AI Agents approach.
   - Use `02_deep_research_with_bing_search_scraping.ipynb` for enhanced workflows that scrape and analyze the full content of web pages for deeper insights using the hybrid approach.
   - Use `03_deep_research_with_azure_ai_agents_only.ipynb` for pure Azure AI Agents implementation with custom agent orchestration and automated peer review loops.
   - Use `04_deep_research_with_agent_framework.ipynb` for Agent Framework orchestration with v1 SDK.
   - Use `05_deep_research_with_agent_framework_v2.ipynb` for the latest v2 SDK with Agent Framework.
2. Follow the cells in sequence to execute the full research workflow.
3. Modify the `user_query` variable to research different topics.

## Project Structure

- `01_deep_research_with_bing_search.ipynb`: Main notebook with the standard workflow (hybrid OpenAI Agents SDK + Azure AI Agents approach)
- `02_deep_research_with_bing_search_scraping.ipynb`: Enhanced workflow with web scraping for deeper content extraction (hybrid approach)
- `03_deep_research_with_azure_ai_agents_only.ipynb`: Pure Azure AI Agents implementation with custom agent orchestration and automated peer review loops
- `04_deep_research_with_agent_framework.ipynb`: Workflow with Microsoft Agent Framework, switch-case routing, and iteration limits (v1 SDK)
- `05_deep_research_with_agent_framework_v2.ipynb`: **Latest** workflow with Agent Framework and Azure AI Agents v2 SDK, featuring parallel search and full citation extraction
- `common/`: Shared utility modules
  - `create_azure_ai_agents.py`: Functions for creating and configuring Azure AI Agents (v1 SDK)
  - `create_azure_ai_agents_v2.py`: Functions for creating and configuring Azure AI Agents (v2 SDK)
  - `data_models.py`: Data models and structures used across the project
  - `helper.py`: Helper functions for visualization and workflow display
  - `update_instructions.py`: Utilities for updating agent instructions and configurations
  - `utils_ai_agents.py`: Azure AI Agents utilities for agent orchestration
  - `utils_research.py`: Research data processing functions
  - `utils_scraping.py`: Web scraping utilities
  - `utils_search.py`: Search result parsing utilities
  - `utils_summary.py`: Summarization utilities
- `maf/`: Agent Framework modules
  - `agents.py`: Agent definitions with Azure AI clients (v1 SDK)
  - `agents_v2.py`: Agent definitions with Azure AI clients (v2 SDK)
  - `nodes.py`: Workflow executors for search, summary, report generation, and routing (v1 SDK)
  - `nodes_v2.py`: Workflow executors with parallel search and citation extraction (v2 SDK)
  - `middleware.py`: Validation and parsing for agent responses
  - `update_agent_instructions.py`: Agent instruction management
  - `create_peer_review_agent_multi_choice.py`: Peer review agent with multi-choice decision making
  - `helper.py`: Visualization and workflow display utilities for Agent Framework
- `requirements/`: Notebook-specific dependencies
  - `01_deep_research_with_bing_search_requirements.txt`: Dependencies for notebook 01
  - `02_deep_research_with_bing_search_scraping_requirements.txt`: Dependencies for notebook 02
  - `03_deep_research_with_azure_ai_agents_only_requirements.txt`: Dependencies for notebook 03
  - `04_deep_research_with_agent_framework_requirements.txt`: Dependencies for notebook 04
  - `05_deep_research_with_agent_framework_requirements.txt`: Dependencies for notebook 05

## Agent Architecture

The workflow combines these specialized agents:

- **PlannerAgent**: Creates comprehensive research plans with subtopics and queries
- **BingSearchAgent**: Retrieves relevant search results from the web
- **WebScraperAgent**: Extracts, cleans, and filters relevant content from web pages (scraping notebook only)
- **SummaryAgent**: Extracts key insights from retrieved or scraped content
- **ResearchAgent**: Compiles findings into structured research reports
- **PeerReviewAgent**: Provides quality feedback in a continuous improvement loop
- **PeerReviewAgentMultiChoice** (notebook 04 & 05): Enhanced peer review with intelligent routing decisions that automatically directs workflow to completion, report revision, or additional data gathering based on structured feedback analysis