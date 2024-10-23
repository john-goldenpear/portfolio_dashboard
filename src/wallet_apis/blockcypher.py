import requests
from typing import Dict, Any
import logging
from config import BLOCKCYPHER_TOKEN

BASE_URL = "https://api.blockcypher.com/v1"

def make_blockcypher_request(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make a request to the BlockCypher API.

    Args:
        endpoint (str): The API endpoint to call.
        params (Dict[str, Any], optional): Additional parameters for the API call.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    """
    url = f"{BASE_URL}/{endpoint}"
    params = params or {}
    params['token'] = BLOCKCYPHER_TOKEN

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an exception for bad responses
    return response.json()

def fetch_blockcypher_user_balance(address: str, symbol: str) -> Dict[str, Any]:
    """
    Fetch the balance of a given cryptocurrency address using the BlockCypher API.

    Args:
        address (str): Cryptocurrency address.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        Dict[str, Any]: The balance data of the cryptocurrency address.
    """
    try:
        endpoint = f"{symbol}/main/addrs/{address}/balance"
        return make_blockcypher_request(endpoint)
    except Exception as e:
        logging.error(f"Error fetching balance for {address}: {e}")
        return {}

def fetch_blockcypher_transactions(address: str, symbol: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Fetch transactions for a given cryptocurrency address using the BlockCypher API.

    Args:
        address (str): Cryptocurrency address.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').
        params (Dict[str, Any], optional): Additional query parameters for the API call.

    Returns:
        Dict[str, Any]: The transaction data for the cryptocurrency address.
    """
    try:
        endpoint = f"{symbol}/main/addrs/{address}/full"
        return make_blockcypher_request(endpoint, params)
    except Exception as e:
        logging.error(f"Error fetching transactions for {address}: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        # Example Dogecoin address
        test_doge_address = "ADNbM5fBujCRBW1vqezNeAWmnsLp19ki3n"
        
        # Fetch balance
        doge_balance = fetch_blockcypher_user_balance(test_doge_address, 'doge')
        logging.info(f"Dogecoin balance for {test_doge_address}: {doge_balance}")

        # Fetch transactions
        doge_transactions = fetch_blockcypher_transactions(test_doge_address, 'doge', {'limit': 50})
        logging.info(f"Dogecoin transactions for {test_doge_address}: {len(doge_transactions.get('txs', []))} transactions fetched")

        # Example Bitcoin address
        test_btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        
        # Fetch balance
        btc_balance = fetch_blockcypher_user_balance(test_btc_address, 'btc')
        logging.info(f"Bitcoin balance for {test_btc_address}: {btc_balance}")

        # Fetch transactions
        btc_transactions = fetch_blockcypher_transactions(test_btc_address, 'btc', {'limit': 50})
        logging.info(f"Bitcoin transactions for {test_btc_address}: {len(btc_transactions.get('txs', []))} transactions fetched")

    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")