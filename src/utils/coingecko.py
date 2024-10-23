import requests
import logging
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime
from src.utils.utils import fetch_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants locally within the module
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3'
COINGECKO_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from the CoinGecko API.

    Args:
        endpoint (str): The API endpoint to request.
        params (Optional[Dict[str, Any]]): Query parameters to include in the request.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{COINGECKO_API_URL}/{endpoint}"
    return fetch_with_retries(url, COINGECKO_HEADERS, params)

def fetch_coingecko_token_info(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch all token information from CoinGecko API.

    Args:
        token_address (str): Token address.

    Returns:
        Optional[Dict[str, Any]]: The JSON response containing the token information, or None if an error occurs.
    """
    endpoint = f'coins/solana/contract/{token_address}'
    try:
        return fetch_data(endpoint)
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error fetching data for token {token_address}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error fetching data for token {token_address}: {e}")
    return None

def fetch_coingecko_token_symbol_and_price(token_address: str) -> Optional[Dict[str, Any]]:
    """
    Fetch token symbol and price from CoinGecko API using token info.

    Args:
        token_address (str): Token address.

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing the token symbol and price, or None if an error occurs.
    """
    token_info = fetch_coingecko_token_info(token_address)
    if token_info:
        try:
            symbol = token_info['symbol'].upper()
            price = token_info['market_data']['current_price']['usd']
            return {'symbol': symbol, 'price': price}
        except KeyError as e:
            logging.error(f"Key error: {e} in response {token_info}")
    return None

def fetch_coingecko_price(coingecko_id: str) -> Optional[float]:
    """
    Fetch the price of a token from CoinGecko using its ID.

    Args:
        coingecko_id (str): The CoinGecko ID of the token.

    Returns:
        Optional[float]: The current price of the token in USD, or None if an error occurs.
    """
    endpoint = f'coins/{coingecko_id}'
    try:
        token_info = fetch_data(endpoint)
        if token_info:
            return token_info['market_data']['current_price']['usd']
    except KeyError as e:
        logging.error(f"Key error: {e} in response {token_info}")
    return None

def fetch_historical_data(coingecko_id: str, days: int = 180) -> pd.Series:
    """
    Fetch historical daily price data for a cryptocurrency from CoinGecko.

    Args:
        coingecko_id (str): The CoinGecko ID of the cryptocurrency.
        days (int): The number of days of historical data to fetch.

    Returns:
        pd.Series: A pandas Series with dates as index and closing prices as values.
    """
    endpoint = f'coins/{coingecko_id}/market_chart'
    params = {'vs_currency': 'usd', 'days': days}
    try:
        data = fetch_data(endpoint, params)
        if 'prices' in data:
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('date', inplace=True)
            return df['price']
    except Exception as e:
        logging.error(f"Error fetching historical data for {coingecko_id}: {e}")
    return pd.Series(dtype=float)

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    token_addresses = ['So11111111111111111111111111111111111111112', '4k3Dyjzvzp8eGN8wxD3YdbJQH7qENNE6jn7W9VpujwJ4']
    token_symbols = ['bitcoin', 'ethereum']
    
    try:
        # Fetch and print token info from CoinGecko
        for address in token_addresses:
            token_symbol_and_price = fetch_coingecko_token_symbol_and_price(address)
            if token_symbol_and_price:
                logging.info(f"Token Address: {address}")
                logging.info(f"Symbol: {token_symbol_and_price['symbol']}")
                logging.info(f"Price (USD): {token_symbol_and_price['price']}")
            else:
                logging.info(f"Token information for {address} not found.")

        # Fetch and print token prices from CoinGecko
        for symbol in token_symbols:
            price = fetch_coingecko_price(symbol)
            if price is not None:
                logging.info(f"The current price of {symbol.upper()} is ${price}")
            else:
                logging.info(f"Price for {symbol.upper()} not found.")

        # Fetch and print historical prices from CoinGecko
        for symbol in token_symbols:
            historical_prices = fetch_historical_data(symbol, days=180)
            logging.info(f"Fetched historical prices for {symbol}: {historical_prices.head()}")
    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")