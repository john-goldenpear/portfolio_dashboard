import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def fetch_bitcoin_balance(address: str) -> float:
    """
    Fetch the Bitcoin balance for a given wallet address using the Blockchain.com API.

    Args:
        address (str): Bitcoin wallet address.

    Returns:
        float: Bitcoin balance in BTC.
    """
    try:
        url = f'https://blockchain.info/q/addressbalance/{address}'
        response = requests.get(url)
        response.raise_for_status()
        balance_satoshi = int(response.text)
        balance_btc = balance_satoshi / 1e8  # Convert satoshi to BTC
        return balance_btc
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"Error occurred: {err}")
    return 0.0

# Example usage
if __name__ == "__main__":
    # Replace with your Bitcoin wallet address for testing
    test_address = '35hK24tcLEWcgNA4JxpvbkNkoAcDGqQPsP'
    balance = fetch_bitcoin_balance(test_address)
    print(f"Balance for address {test_address}: {balance} BTC")