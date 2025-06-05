from azure.ai.agents.models import MessageRole

def add_user_message_to_thread(project_client, thread_id, text):
    """
    Adds a message to a thread with the specified role and text.
    """
    project_client.agents.messages.create(
        thread_id=thread_id,
        role=MessageRole.USER,
        content=text,
    )

def get_last_message_by_role(project_client, thread_id, role):
    """
    Retrieves the last message from an agent in a specified thread.
    """
    return project_client.agents.messages.get_last_message_by_role(
        thread_id=thread_id,
        role=MessageRole.AGENT
    ).content[0]['text']['value']


def invoke_agent(project_client, thread, agent):
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    # print(f"run status: {run.status}")

    # get the last message from the planner agent
    last_agent_output = get_last_message_by_role(project_client, thread.id, MessageRole.AGENT)
    return last_agent_output, thread