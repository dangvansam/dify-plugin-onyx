from collections.abc import Generator
from typing import Any
import requests
import logging

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.config.logger_format import plugin_logger_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

class CreateChatSessionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        logger.info(f"Received event in CreateChatSessionTool with parameters: {tool_parameters}")
        api_base = self.runtime.credentials.get("onyx_api_base", "").rstrip("/")

        api_key = self.runtime.credentials.get("onyx_api_key")
        
        if not api_base or not api_key:
            yield self.create_text_message("Error: Onyx API Base URL and API Key are required in provider credentials.")
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        persona_id = tool_parameters.get("persona_id", 0)
        description = tool_parameters.get("description")
        project_id = tool_parameters.get("project_id")

        payload = {"persona_id": persona_id}
        if description is not None:
            payload["description"] = description
        if project_id is not None:
            payload["project_id"] = project_id

        try:
            url = f"{api_base}/chat/create-chat-session"
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            session_id = data.get("chat_session_id", "Unknown")
            
            yield self.create_text_message(f"Successfully created session: {session_id}")
        except Exception as e:
            yield self.create_text_message(f"Error creating chat session: {str(e)}")
