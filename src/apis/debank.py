import requests
import logging
import time
from typing import Dict, Any, List, Optional
from src.apis.utils import fetch_with_retries
from config import DEBANK_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants locally within the module
DEBANK_BASE_URL = 'https://pro-openapi.debank.com/v1/'
DEBANK_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'AccessKey': DEBANK_API_KEY
}

def fetch_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from the DeBank API.

    Args:
        endpoint (str): The API endpoint to request.
        params (Optional[Dict[str, Any]]): Query parameters to include in the request.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{DEBANK_BASE_URL}{endpoint}"
    return fetch_with_retries(url, DEBANK_HEADERS, params)

def fetch_debank_user_balances_protocol(user_id: str) -> Dict[str, Any]:
    """
    Fetch all complex protocols for a user from DeBank API.

    Args:
        user_id (str): The user's ID.

    Returns:
        Dict[str, Any]: The JSON response containing the user's protocols.
    """
    endpoint = f"user/all_complex_protocol_list?id={user_id}"
    return fetch_data(endpoint)

def fetch_debank_user_balances_tokens(user_id: str) -> Dict[str, Any]:
    """
    Fetch all tokens for a user from DeBank API.

    Args:
        user_id (str): The user's wallet address.

    Returns:
        Dict[str, Any]: The JSON response containing the user's tokens.
    """
    endpoint = f"user/all_token_list?id={user_id}"
    return fetch_data(endpoint)

def fetch_debank_user_transactions_one_page(user_id: str, end_time: int, page_count: int = 20, chain_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Fetch the transaction history for a user on all supported chains from DeBank API.

    Args:
        user_id (str): The user's address.
        end_time (int): Timestamp to return transactions earlier than this time.
        page_count (int): Number of entries to return (maximum 20).
        chain_ids (Optional[List[str]]): List of chain IDs to filter the transactions.

    Returns:
        List[Dict[str, Any]]: A list of transactions for the cryptocurrency address.
    """
    endpoint = "user/all_history_list"
    params = {
        'id': user_id,
        'start_time': end_time,
        'page_count': page_count,
        'chain_ids': ','.join(chain_ids) if chain_ids else None
    }
    return fetch_data(endpoint, params).get('history_list', [])

def fetch_debank_user_transactions(user_id: str, end_time: int = int(time.time()), start_time: int = 0, page_count: int = 20, chain_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Fetch all transactions for a user between start_time and end_time. 
    Defaults to entire transaction history.

    Args:
        user_id (str): The user's address.
        end_time (int, optional): Timestamp to stop fetching transactions; returns transactions later than this time. Defaults to the time that the function is run.
        start_time (int, optional): Timestamp to start fetching transactions; returns transactions earlier than this time; Defaults to beginning of time.
        page_count (int, optional): Number of entries per page (maximum 20). Default is 20.
        chain_ids (Optional[List[str]]): List of chain IDs to filter the transactions.

    Returns:
        List[Dict[str, Any]]: A list of all transactions within the specified time range.
    """
    all_transactions = []
    current_end_time = end_time

    while True:
        transactions = fetch_debank_user_transactions_one_page(user_id, current_end_time, page_count, chain_ids)
        if not transactions:
            break
        all_transactions.extend(transactions)
        # Update the start_time for the next batch of transactions
        # Assuming the transactions are returned in descending order by timestamp
        last_transaction_time = int(transactions[-1]['time_at'])
        if last_transaction_time < start_time:
            break
        current_end_time = last_transaction_time

        # Sleep to avoid hitting API rate limits (adjust as needed)
        time.sleep(1)

    return all_transactions

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    user_id = '0x4a4e392290a382c9d2754e5dca8581ea1893db5d'

    try:
        # Example usage of fetch_protocols function
        protocols = fetch_debank_user_balances_protocol(user_id)
        logging.info('User Protocol Data:', protocols)

        # Example usage of fetch_tokens function
        tokens = fetch_debank_user_balances_tokens(user_id)
        logging.info('User Token Data:', tokens)

        # Example usage of fetch_transactions_latest function
        transactions_latest = fetch_debank_user_transactions_one_page(user_id, end_time=1721926341, page_count=10)
        logging.info('Latest Transactions (up to 20 txs):', transactions_latest)

        # Example usage of fetch_transactions function
        start_time = 1712233366  # Example start timestamp (e.g., April 4, 2024)
        end_time = 1717417366    # Example end timestamp (e.g., June 3, 2024)
        transactions = fetch_debank_user_transactions(user_id, end_time, start_time, page_count=20, chain_ids=['eth', 'bsc'])
        logging.info('All User Transactions from April 4, 2024 to June 3, 2024 on eth and bsc chains:', transactions)
    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")