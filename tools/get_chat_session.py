import json
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

class GetChatSessionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        logger.info(f"Received event in GetChatSessionTool with parameters: {tool_parameters}")
        api_base = self.runtime.credentials.get("onyx_api_base", "").rstrip("/")

        api_key = self.runtime.credentials.get("onyx_api_key")
        
        if not api_base or not api_key:
            yield self.create_text_message("Error: Onyx API Base URL and API Key are required in provider credentials.")
            return

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        session_id = tool_parameters.get("session_id", "")
        if not session_id.strip():
            yield self.create_text_message("Error: session_id cannot be empty.")
            return

        try:
            url = f"{api_base}/chat/get-chat-session/{session_id}"
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            yield self.create_text_message(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            yield self.create_text_message(f"Error fetching chat session: {str(e)}")
