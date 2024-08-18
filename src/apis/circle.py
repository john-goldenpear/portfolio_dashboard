import logging
from typing import Dict, Any, Optional
from apis.utils import fetch_with_retries
from config import CIRCLE_API_KEY

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

def fetch_circle_user_deposits() -> Dict[str, Any]:
    """
    Fetch deposits from the Circle API.

    Returns:
        Dict[str, Any]: The JSON response containing the deposits.
    """
    return fetch_data('deposits')

def fetch_circle_user_transfers() -> Dict[str, Any]:
    """
    Fetch transfers from the Circle API.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    return fetch_data('transfers')

def fetch_circle_user_redemptions() -> Dict[str, Any]:
    """
    Fetch redemptions (payouts) from the Circle API.

    Returns:
        Dict[str, Any]: The JSON response containing the redemptions.
    """
    return fetch_data('payouts')

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
        logging.info('Circle Balances:', balances)

        # Fetch and print Circle deposits
        deposits = fetch_circle_user_deposits()
        logging.info('Circle Deposits:', deposits)

        # Fetch and print Circle transfers
        transfers = fetch_circle_user_transfers()
        logging.info('Circle Transfers:', transfers)

        # Fetch and print Circle redemptions (payouts)
        redemptions = fetch_circle_user_redemptions()
        logging.info('Circle Redemptions:', redemptions)

        # Fetch and print Circle wallets
        wallets = fetch_circle_user_wallets()
        logging.info('Circle Wallets:', wallets)

    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")