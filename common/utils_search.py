from azure.ai.projects.models import MessageRole

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