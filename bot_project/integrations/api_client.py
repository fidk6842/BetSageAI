# integrations/api_client.py
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger('OddsBot')

async def make_request(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 15.0
) -> Optional[Dict]:
    """
    Makes an async HTTP GET request to the specified URL.
    
    Args:
        url: The URL to make the request to
        headers: Optional headers to include in the request
        params: Optional query parameters
        timeout: Request timeout in seconds
    
    Returns:
        JSON response data or None if request fails
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
            return None
            
        except httpx.RequestError as e:
            logger.error(f"Request error for URL {url}: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error making request to {url}: {str(e)}")
            return None