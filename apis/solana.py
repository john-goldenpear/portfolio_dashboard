import requests
import logging
import time

# Define constants locally within the module
SOLANA_EXPLORER_BASE_URL = 'https://api.mainnet-beta.solana.com'
SOLANA_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(method: str, params: list = None, retries: int = 10) -> dict:
    """
    Fetch data from the Solana Explorer API with retries on failure.

    Args:
        method (str): The RPC method to request.
        params (list, optional): Parameters to include in the request.
        retries (int, optional): Number of retries in case of failure. Defaults to 5.

    Returns:
        dict: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or []
    }
    print(f"Fetching data with payload: {payload}")  # Debug statement
    attempt = 0
    while attempt < retries:
        try:
            response = requests.post(SOLANA_EXPLORER_BASE_URL, headers=SOLANA_HEADERS, json=payload)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                delay = 5 * (attempt + 1)
                logging.warning(f"Rate limited: {response.text}. Retrying in {delay} seconds...")
                time.sleep(delay)
                attempt += 1
            else:
                logging.error(f"HTTP error occurred: {e}")
                logging.error(f"Response: {response.text}")
                raise
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise
    raise requests.exceptions.RetryError(f"Failed to fetch data after {retries} attempts")

def fetch_solana_user_balance(wallet_address: str) -> dict:
    """
    Fetch balance of a Solana wallet.

    Args:
        wallet_address (str): The Solana wallet address.

    Returns:
        dict: The JSON response containing the balance.
    """
    return fetch_data('getBalance', [wallet_address])

def fetch_solana_user_token_balances(wallet_address: str) -> list:
    """
    Fetch token accounts of a Solana wallet.

    Args:
        wallet_address (str): The Solana wallet address.

    Returns:
        list: The list of token accounts.
    """
    params = [
        wallet_address,
        {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"encoding": "jsonParsed"}
    ]
    response = fetch_data('getTokenAccountsByOwner', params)
    return response['result']['value']

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    wallet_address = '9QgXqrgdbVU8KcpfskqJpAXKzbaYQJecgMAruSWoXDkM'
    
    try:
        # Fetch and print Solana balance
        balance = fetch_solana_user_balance(wallet_address)
        print('Solana Balance:', balance)

        # Fetch and print Solana token accounts
        token_accounts = fetch_solana_user_token_balances(wallet_address)
        print('Solana Token Accounts:', token_accounts)

    except Exception as e:
        print(f"An error occurred during the example usage: {e}")