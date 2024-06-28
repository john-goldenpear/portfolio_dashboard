import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_blockcypher_user_balance(address: str, symbol: str) -> dict:
    """
    Fetch the balance of a given cryptocurrency address using the appropriate API.

    Args:
        address (str): Cryptocurrency address.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        dict: The balance data of the cryptocurrency address.
    """
    try:
        logging.info(f"Fetching balance for {symbol} address: {address}")

        url = f"https://api.blockcypher.com/v1/{symbol}/main/addrs/{address}/balance"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return data

    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request error: {e}")
        return {}
    except KeyError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return {}

def fetch_blockcypher_transactions(address: str, symbol: str) -> list:
    """
    Fetch the transactions of a given cryptocurrency address using the appropriate API.

    Args:
        address (str): Cryptocurrency address.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        list: A list of transactions for the cryptocurrency address.
    """
    try:
        logging.info(f"Fetching transactions for {symbol} address: {address}")
        
        url = f"https://api.blockcypher.com/v1/{symbol}/main/addrs/{address}/full"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return data.get('txs', [])

    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request error: {e}")
        return []
    except KeyError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return []

# Example usage
if __name__ == "__main__":
    test_doge_address = "ADNbM5fBujCRBW1vqezNeAWmnsLp19ki3n"
    doge_balance = fetch_blockcypher_user_balance(test_doge_address, 'doge')
    doge_transactions = fetch_blockcypher_transactions(test_doge_address, 'doge')
    print(f"Dogecoin balance for {test_doge_address}: {doge_balance}")
    print(f"Dogecoin transactions for {test_doge_address}:")
    for tx in doge_transactions:
        print(tx)

    test_btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    btc_balance = fetch_blockcypher_user_balance(test_btc_address, 'btc')
    btc_transactions = fetch_blockcypher_transactions(test_btc_address, 'btc')
    print(f"Bitcoin balance for {test_btc_address}: {btc_balance}")
    print(f"Bitcoin transactions for {test_btc_address}:")
    for tx in btc_transactions:
        print(tx)
