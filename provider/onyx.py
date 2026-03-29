from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class OnyxProvider(ToolProvider):
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_base = credentials.get("onyx_api_base", "").rstrip("/")
            api_key = credentials.get("onyx_api_key")
            
            if not api_base or not api_key:
                raise ValueError("Both 'Onyx API Base URL' and 'Onyx API Key' are required.")
                
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            # Perform a lightweight validation request (e.g. GET /tool)
            response = requests.get(f"{api_base}/tool", headers=headers, timeout=10)
            if response.status_code in [401, 403]:
                raise ValueError("Invalid Onyx API Key or unauthenticated.")
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Failed to connect to Onyx API: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
