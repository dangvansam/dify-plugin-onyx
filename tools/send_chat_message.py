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

class SendChatMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        logger.info(f"Received event in SendChatMessageTool with parameters: {tool_parameters}")
        api_base = self.runtime.credentials.get("onyx_api_base", "").rstrip("/")

        api_key = self.runtime.credentials.get("onyx_api_key")
        
        if not api_base or not api_key:
            yield self.create_text_message("Error: Onyx API Base URL and API Key are required in provider credentials.")
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        message = tool_parameters.get("message", "")
        if not message.strip():
            yield self.create_text_message("Error: message cannot be empty.")
            return

        chat_session_id = tool_parameters.get("chat_session_id")

        payload = {
            "message": message,
            "stream": False
        }
        if chat_session_id:
            payload["chat_session_id"] = chat_session_id

        try:
            url = f"{api_base}/chat/send-chat-message"
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            answer = data.get("answer", "")
            if not answer:
                answer = str(data)
                
            yield self.create_text_message(answer)
            
            # Yield metadata as a json message
            metadata = {
                "message_id": data.get("message_id"),
                "chat_session_id": data.get("chat_session_id"),
                "answer_citationless": data.get("answer_citationless"),
                "pre_answer_reasoning": data.get("pre_answer_reasoning"),
                "error_msg": data.get("error_msg")
            }
            yield self.create_json_message(metadata)
        except Exception as e:
            yield self.create_text_message(f"Error sending chat message: {str(e)}")
