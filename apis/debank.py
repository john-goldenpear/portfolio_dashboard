import requests
import time
from config import DEBANK_API_KEY

# Define constants locally within the module
DEBANK_BASE_URL = 'https://pro-openapi.debank.com/v1/'
DEBANK_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(endpoint, params=None):
    """
    Fetch data from the DeBank API.

    Args:
        endpoint (str): The API endpoint to request.
        params (dict, optional): Query parameters to include in the request.

    Returns:
        dict: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{DEBANK_BASE_URL}{endpoint}"
    headers = {
        **DEBANK_HEADERS,
        'AccessKey': DEBANK_API_KEY
    }
    print(f"Fetching data from {url} with params {params}")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response: {response.text}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def fetch_debank_user_balances_protocol(user_id):
    """
    Fetch all complex protocols for a user from DeBank API.

    Args:
        user_id (str): The user's ID.

    Returns:
        dict: The JSON response containing the user's protocols.
    """
    endpoint = f"user/all_complex_protocol_list?id={user_id}"
    return fetch_data(endpoint)

def fetch_debank_user_balances_tokens(user_id):
    """
    Fetch all tokens for a user from DeBank API.

    Args:
        user_id (str): The user's wallet address.

    Returns:
        dict: The JSON response containing the user's tokens.
    """
    endpoint = f"user/all_token_list?id={user_id}"
    return fetch_data(endpoint)

def fetch_debank_user_transactions_one_page(user_id, end_time, page_count=20, chain_ids=None):
    """
    Fetch the transaction history for a user on all supported chains from DeBank API.

    Args:
        user_id (str): The user's address.
        end_time (int): Timestamp to return transactions earlier than this time.
        page_count (int): Number of entries to return (maximum 20).
        chain_ids (list of str, optional): List of chain IDs to filter the transactions.

    Returns:
        dict: The JSON response containing the user's transaction history.
    """
    endpoint = "user/all_history_list"
    params = {
        'id': user_id,
        'start_time': end_time,
        'page_count': page_count,
        'chain_ids': ','.join(chain_ids) if chain_ids else None
    }
    # Remove keys with None values
    params = {k: v for k, v in params.items() if v is not None}
    response = fetch_data(endpoint, params)
    return response.get('history_list', [])

def fetch_debank_user_transactions(user_id, end_time=int(time.time()), start_time=0, page_count=20, chain_ids=None):
    """
    Fetch all transactions for a user between start_time and end_time. 
    Defaults to entire transaction history

    Args:
        user_id (str): The user's address.
        end_time (int, optional): Timestamp to stop fetching transactions; returns transactions later than this time. Defaults to the time that the function is run
        start_time (int, optional): Timestamp to start fetching transactions; returns transactions earlier than this time; Defaults to beginning of time
        page_count (int, optional): Number of entries per page (maximum 20). Default is 20.
        chain_ids (list of str, optional): List of chain IDs to filter the transactions.

    Returns:
        list: A list of all transactions within the specified time range.
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

    return [tx for tx in all_transactions]

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    user_id = '0x2aF2A6f692231e394b48B701AFCe9f5CC2081AB4'

    # Example usage of fetch_protocols function
    protocols = fetch_debank_user_balances_tokens(user_id)
    print('User Protocol Data:', protocols)

    # Example usage of fetch_tokens function
    tokens = fetch_debank_user_balances_tokens(user_id)
    print('User Token Data:', tokens)

    # Example usage of fetch_transactions_latest function
    transactions_latest = fetch_debank_user_transactions_one_page(user_id, end_time=1717417366, page_count=10, chain_ids=['eth', 'bsc'])
    print('Latest Transactions (up to 20 txs):', transactions_latest)

    # Example usage of fetch_transactions function
    start_time = 1712233366  # Example start timestamp (e.g., April 4, 2024)
    end_time = 1717417366    # Example end timestamp (e.g., June 3, 2024)
    transactions = fetch_debank_user_transactions(user_id, end_time, start_time, page_count=20, chain_ids=['eth', 'bsc'])
    print('All User Transactions from April 4, 2024 to June 3, 2024 on eth and bsc chains:', transactions)