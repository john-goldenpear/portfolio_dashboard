import logging
from typing import Dict, Any
from src.apis.utils import fetch_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_blockcypher_user_balance(address: str, symbol: str) -> Dict[str, Any]:
    """
    Fetch the balance of a given cryptocurrency address using the appropriate API.

    Args:
        address (str): Cryptocurrency address.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        Dict[str, Any]: The balance data of the cryptocurrency address.
    """
    url = f"https://api.blockcypher.com/v1/{symbol}/main/addrs/{address}/balance"
    return fetch_with_retries(url, {})

def fetch_blockcypher_transactions(address: str, symbol: str) -> Dict[str, Any]:
    """
    Fetch the transactions of a given cryptocurrency address using the appropriate API.

    Args:
        address (str): Cryptocurrency address.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        Dict[str, Any]: A list of transactions for the cryptocurrency address.
    """
    url = f"https://api.blockcypher.com/v1/{symbol}/main/addrs/{address}/full"
    return fetch_with_retries(url, {}).get('txs', [])

# Example usage
if __name__ == "__main__":
    try:
        test_doge_address = "ADNbM5fBujCRBW1vqezNeAWmnsLp19ki3n"
        doge_balance = fetch_blockcypher_user_balance(test_doge_address, 'doge')
        doge_transactions = fetch_blockcypher_transactions(test_doge_address, 'doge')
        logging.info(f"Dogecoin balance for {test_doge_address}: {doge_balance}")
        logging.info(f"Dogecoin transactions for {test_doge_address}: {doge_transactions}")

        test_btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        btc_balance = fetch_blockcypher_user_balance(test_btc_address, 'btc')
        btc_transactions = fetch_blockcypher_transactions(test_btc_address, 'btc')
        logging.info(f"Bitcoin balance for {test_btc_address}: {btc_balance}")
        logging.info(f"Bitcoin transactions for {test_btc_address}: {btc_transactions}")
    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")