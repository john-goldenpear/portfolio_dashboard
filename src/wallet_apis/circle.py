import logging
from typing import Dict, Any, Optional
from src.utils.utils import fetch_with_retries
from config import CIRCLE_API_KEY
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants locally within the module
CIRCLE_BASE_URL = 'https://api.circle.com/v1/businessAccount/'
CIRCLE_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + CIRCLE_API_KEY
}

def fetch_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from the Circle API.

    Args:
        endpoint (str): The API endpoint to request.
        params (Optional[Dict[str, Any]]): Query parameters to include in the request.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{CIRCLE_BASE_URL}{endpoint}"
    return fetch_with_retries(url, CIRCLE_HEADERS, params)

def fetch_circle_user_balance() -> Dict[str, Any]:
    """
    Fetch balances from the Circle API.

    Returns:
        Dict[str, Any]: The JSON response containing the balances.
    """
    return fetch_data('balances')

def fetch_circle_user_deposits(start_date: datetime, end_date: datetime, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch deposits from the Circle API within a date range.

    Args:
        start_date (datetime): Start date for fetching deposits.
        end_date (datetime): End date for fetching deposits.
        params (Optional[Dict[str, Any]]): Additional query parameters for the API request.

    Returns:
        Dict[str, Any]: The JSON response containing the deposits.
    """
    params = params or {}
    params.update({
        'from': start_date.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'to': end_date.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    })
    return fetch_data('deposits', params)

def fetch_circle_user_transfers(start_date: datetime, end_date: datetime, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch transfers from the Circle API within a date range.

    Args:
        start_date (datetime): Start date for fetching transfers.
        end_date (datetime): End date for fetching transfers.
        params (Optional[Dict[str, Any]]): Additional query parameters for the API request.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    params = params or {}
    params.update({
        'from': start_date.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'to': end_date.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    })
    return fetch_data('transfers', params)

def fetch_circle_user_redemptions(start_date: datetime, end_date: datetime, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch redemptions (payouts) from the Circle API within a date range.

    Args:
        start_date (datetime): Start date for fetching redemptions.
        end_date (datetime): End date for fetching redemptions.
        params (Optional[Dict[str, Any]]): Additional query parameters for the API request.

    Returns:
        Dict[str, Any]: The JSON response containing the redemptions.
    """
    params = params or {}
    params.update({
        'from': start_date.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'to': end_date.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    })
    return fetch_data('payouts', params)

def fetch_circle_user_wallets() -> Dict[str, Any]:
    """
    Fetch wallets from the Circle API.

    Returns:
        Dict[str, Any]: The JSON response containing the wallets.
    """
    return fetch_data('wallets/addresses/deposit')

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    try:
        # Fetch and print Circle balance
        balances = fetch_circle_user_balance()
        logging.info('Circle Balances: %s', balances)

        # Use datetime objects for start and end dates
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 12, 31, tzinfo=timezone.utc)

        # Fetch and print Circle deposits
        deposits = fetch_circle_user_deposits(start_date, end_date)
        logging.info('Circle Deposits: %s', deposits)

        # Fetch and print Circle transfers
        transfers = fetch_circle_user_transfers(start_date, end_date)
        logging.info('Circle Transfers: %s', transfers)

        # Fetch and print Circle redemptions (payouts)
        redemptions = fetch_circle_user_redemptions(start_date, end_date)
        logging.info('Circle Redemptions: %s', redemptions)

        # Fetch and print Circle wallets
        wallets = fetch_circle_user_wallets()
        logging.info('Circle Wallets: %s', wallets)

    except Exception as e:
        logging.error("An error occurred during the example usage: %s", e)