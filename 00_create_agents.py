import os
import dotenv
dotenv.load_dotenv(".env", override=True)

from common.create_azure_ai_agents import get_project_client, create_agents
from maf.create_peer_review_agent_multi_choice import create_peer_review_agent_multi_choice

def main():
    project_client = get_project_client(os.getenv("PROJECT_ENDPOINT"))
    create_agents(project_client) # creates all agents except the peer review agent
    create_peer_review_agent_multi_choice(project_client) # creates the multi condition peer review agent

if __name__ == '__main__':
    main()