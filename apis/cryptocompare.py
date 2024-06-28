import requests
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants
CRYPTOCOMPARE_API_URL = 'https://min-api.cryptocompare.com/data/price'
CRYPTOCOMPARE_API_KEY = 'YOUR_API_KEY'  # Replace with your CryptoCompare API key

def fetch_cryptocompare_price(symbol: str, currency: str = 'USD') -> float:
    """
    Fetch the current price of a cryptocurrency symbol in a given currency.

    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC', 'ETH').
        currency (str): The currency to fetch the price in (default is 'USD').

    Returns:
        float: The current price of the cryptocurrency.
    """
    try:
        params = {
            'fsym': symbol,
            'tsyms': currency,
            'api_key': CRYPTOCOMPARE_API_KEY
        }
        response = requests.get(CRYPTOCOMPARE_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get(currency, None)
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request error: {e}")
        return None
    except KeyError as e:
        logging.error(f"Failed to parse JSON response: {e}")
        return None

def fetch_multiple_prices(symbols: List[str], currency: str = 'USD') -> Dict[str, float]:
    """
    Fetch the current prices for multiple cryptocurrency symbols in a given currency.

    Args:
        symbols (List[str]): A list of cryptocurrency symbols (e.g., ['BTC', 'ETH']).
        currency (str): The currency to fetch the prices in (default is 'USD').

    Returns:
        Dict[str, float]: A dictionary with cryptocurrency symbols as keys and their current prices as values.
    """
    prices = {}
    unique_symbols = set(symbols)
    for symbol in unique_symbols:
        price = fetch_cryptocompare_price(symbol, currency)
        if price is not None:
            prices[symbol] = price
    return prices

# Example usage
if __name__ == "__main__":
    symbols = ['BTC', 'ETH', 'SOL']
    prices = fetch_multiple_prices(symbols)
    for symbol, price in prices.items():
        print(f"The current price of {symbol} is {price} USD")