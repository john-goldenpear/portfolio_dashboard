import requests
import logging
from typing import Dict, List, Optional
import pandas as pd
from src.utils.utils import fetch_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants
CRYPTOCOMPARE_API_URL = 'https://min-api.cryptocompare.com/data'
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
    url = f"{CRYPTOCOMPARE_API_URL}/price"
    params = {
        'fsym': symbol,
        'tsyms': currency,
        'api_key': CRYPTOCOMPARE_API_KEY
    }
    data = fetch_with_retries(url, {}, params)
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

def fetch_historical_data(symbol: str, currency: str = 'USD', limit: int = 180) -> pd.Series:
    """
    Fetch historical daily price data for a cryptocurrency symbol from CryptoCompare.

    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC', 'ETH').
        currency (str): The currency to fetch the price in (default is 'USD').
        limit (int): The number of days of historical data to fetch.

    Returns:
        pd.Series: A pandas Series with dates as index and prices as values.
    """
    url = f"{CRYPTOCOMPARE_API_URL}/v2/histoday"
    params = {
        'fsym': symbol,
        'tsym': currency,
        'limit': limit,
        'api_key': CRYPTOCOMPARE_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get('Response') == 'Success':
        df = pd.DataFrame(data['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df['close']
    else:
        logging.error(f"Error fetching historical data for {symbol}: {data.get('Message')}")
        return pd.Series(dtype=float)

# Example usage
if __name__ == "__main__":
    # Fetch current prices
    symbols = ['BTC', 'ETH', 'SOL']
    prices = fetch_multiple_prices(symbols)
    for symbol, price in prices.items():
        logging.info(f"The current price of {symbol} is {price} USD")

    # Fetch historical prices
    symbol = 'EIGEN'
    historical_prices = fetch_historical_data(symbol)
    logging.info(f"Fetched historical prices for {symbol}: {historical_prices.head()}")
    print(historical_prices.index)
