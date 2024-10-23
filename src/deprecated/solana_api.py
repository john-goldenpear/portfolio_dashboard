import logging
from typing import List, Dict, Any
from src.utils.utils import fetch_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants locally within the module
SOLANA_EXPLORER_BASE_URL = 'https://api.mainnet-beta.solana.com'
SOLANA_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(method: str, params: List[Any] = None) -> Dict[str, Any]:
    """
    Fetch data from the Solana Explorer API.

    Args:
        method (str): The RPC method to request.
        params (List[Any], optional): Parameters to include in the request.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = SOLANA_EXPLORER_BASE_URL
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or []
    }
    return fetch_with_retries(url, SOLANA_HEADERS, payload, method='POST')

def fetch_solana_user_balance(wallet_address: str) -> Dict[str, Any]:
    """
    Fetch the balance of a Solana wallet.

    Args:
        wallet_address (str): The Solana wallet address.

    Returns:
        Dict[str, Any]: The JSON response containing the balance.
    """
    return fetch_data('getBalance', [wallet_address])

def fetch_solana_user_token_balances(wallet_address: str) -> List[Dict[str, Any]]:
    """
    Fetch token accounts of a Solana wallet.

    Args:
        wallet_address (str): The Solana wallet address.

    Returns:
        List[Dict[str, Any]]: The list of token accounts.
    """
    params = [
        wallet_address,
        {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {"encoding": "jsonParsed"}
    ]
    response = fetch_data('getTokenAccountsByOwner', params)
    return response.get('result', {}).get('value', [])

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    try:
        wallet_address = '9QgXqrgdbVU8KcpfskqJpAXKzbaYQJecgMAruSWoXDkM'
        
        # Fetch and print Solana balance
        balance = fetch_solana_user_balance(wallet_address)
        logging.info(f'Solana Balance: {balance}')

        # Fetch and print Solana token accounts
        token_accounts = fetch_solana_user_token_balances(wallet_address)
        logging.info(f'Solana Token Accounts: {token_accounts}')

    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")