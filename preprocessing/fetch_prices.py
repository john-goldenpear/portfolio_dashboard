import logging
import time
from apis.cryptocompare import fetch_cryptocompare_price
from apis.coingecko import fetch_coingecko_price

from config import ASSETS_DICT

def get_coingecko_id(symbol: str) -> str:
    """
    Get the CoinGecko ID for a given symbol using the assets dictionary.

    Args:
        symbol (str): The symbol to lookup.

    Returns:
        str: The corresponding CoinGecko ID.
    """
    asset_info = ASSETS_DICT.get(symbol)
    if asset_info:
        return asset_info['coingecko_id']
    return None

def fetch_price(symbol: str) -> float:
    """
    Fetch the price of a given symbol. Try CryptoCompare first, then CoinGecko.

    Args:
        symbol (str): The symbol for which to fetch the price.

    Returns:
        float: The price of the symbol.
    """
    price = fetch_cryptocompare_price(symbol)
    if price is None:
        logging.info(f"Trying fallback for {symbol}")
        time.sleep(1)  # To prevent hitting rate limits
        coingecko_id = get_coingecko_id(symbol)
        if coingecko_id:
            price = fetch_coingecko_price(coingecko_id)
    return price

def fetch_multiple_prices(symbols: list) -> dict:
    """
    Fetch prices for multiple symbols.

    Args:
        symbols (list): A list of symbols for which to fetch prices.

    Returns:
        dict: A dictionary of symbols and their corresponding prices.
    """
    prices = {}
    for symbol in symbols:
        price = fetch_price(symbol)
        if price is not None:
            prices[symbol] = price
    return prices