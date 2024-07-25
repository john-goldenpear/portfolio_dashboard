import requests
import logging
from typing import Dict, List, Optional
from apis.utils import fetch_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants
CRYPTOCOMPARE_API_URL = 'https://min-api.cryptocompare.com/data/price'
CRYPTOCOMPARE_API_KEY = 'YOUR_API_KEY'  # Replace with your CryptoCompare API key

def fetch_cryptocompare_price(symbol: str, currency: str = 'USD') -> Optional[float]:
    """
    Fetch the current price of a cryptocurrency symbol in a given currency.

    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC', 'ETH').
        currency (str): The currency to fetch the price in (default is 'USD').

    Returns:
        Optional[float]: The current price of the cryptocurrency, or None if an error occurs.
    """
    params = {
        'fsym': symbol,
        'tsyms': currency,
        'api_key': CRYPTOCOMPARE_API_KEY
    }
    data = fetch_with_retries(CRYPTOCOMPARE_API_URL, {}, params)
    return data.get(currency, None)

def fetch_multiple_prices(symbols: List[str], currency: str = 'USD') -> Dict[str, Optional[float]]:
    """
    Fetch the current prices for multiple cryptocurrency symbols in a given currency.

    Args:
        symbols (List[str]): A list of cryptocurrency symbols (e.g., ['BTC', 'ETH']).
        currency (str): The currency to fetch the prices in (default is 'USD').

    Returns:
        Dict[str, Optional[float]]: A dictionary with cryptocurrency symbols as keys and their current prices as values.
    """
    prices = {}
    unique_symbols = set(symbols)
    for symbol in unique_symbols:
        price = fetch_cryptocompare_price(symbol, currency)
        prices[symbol] = price
    return prices

# Example usage
if __name__ == "__main__":
    symbols = ['BTC', 'ETH', 'SOL']
    prices = fetch_multiple_prices(symbols)
    for symbol, price in prices.items():
        logging.info(f"The current price of {symbol} is {price} USD")