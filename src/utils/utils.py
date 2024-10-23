import requests
import logging
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_with_retries(url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None, method: str = 'GET', retries: int = 5) -> Dict[str, Any]:
    """
    Fetch data from a given URL with automatic retries on failure.

    Args:
        url (str): The URL to fetch data from.
        headers (Dict[str, str]): The headers to include in the request.
        params (Optional[Dict[str, Any]], optional): Query parameters or payload for the request. Defaults to None.
        method (str, optional): The HTTP method to use ('GET' or 'POST'). Defaults to 'GET'.
        retries (int, optional): The number of retry attempts on failure. Defaults to 5.

    Returns:
        Dict[str, Any]: The JSON response from the request.

    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code and max retries are reached.
        requests.exceptions.RetryError: If the request fails after the specified number of retries.
    """
    attempt = 0
    while attempt < retries:
        try:
            if method == 'POST':
                response = requests.post(url, headers=headers, json=params)
            else:
                response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.status_code == 429:
                delay = 5 * (attempt + 1)
                logging.warning(f"Rate limited: {response.text}. Retrying in {delay} seconds...")
                time.sleep(delay)
                attempt += 1
            else:
                logging.error(f"HTTP error occurred: {e}, Response: {response.text}")
                raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise
    raise requests.exceptions.RetryError(f"Failed to fetch data after {retries} attempts")