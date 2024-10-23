import logging
import time
from typing import Dict, List, Optional
from src.utils.cryptocompare import fetch_cryptocompare_price
from src.utils.coingecko import fetch_coingecko_price
from config import ASSETS_DICT

logging.basicConfig(level=logging.INFO)

def get_coingecko_id(symbol: str) -> Optional[str]:
    """
    Get the CoinGecko ID for a given symbol using the assets dictionary.

    Args:
        symbol (str): The symbol to lookup.

    Returns:
        Optional[str]: The corresponding CoinGecko ID or None if not found.
    """
    asset_info = ASSETS_DICT.get(symbol)
    if asset_info:
        return asset_info['coingecko_id']
    return None

def fetch_price(symbol: str) -> Optional[float]:
    """
    Fetch the price of a given symbol. Try CryptoCompare first, then CoinGecko.

    Args:
        symbol (str): The symbol for which to fetch the price.

    Returns:
        Optional[float]: The price of the symbol or None if not found.
    """
    price = fetch_cryptocompare_price(symbol)
    if price is None:
        logging.info(f"Trying fallback for {symbol}")
        time.sleep(1)  # To prevent hitting rate limits
        coingecko_id = get_coingecko_id(symbol)
        if coingecko_id:
            price = fetch_coingecko_price(coingecko_id)
    return price

def fetch_multiple_prices(symbols: List[str]) -> Dict[str, Optional[float]]:
    """
    Fetch prices for multiple symbols.

    Args:
        symbols (List[str]): A list of symbols for which to fetch prices.

    Returns:
        Dict[str, Optional[float]]: A dictionary of symbols and their corresponding prices.
    """
    prices = {}
    for symbol in symbols:
        price = fetch_price(symbol)
        if price is not None:
            prices[symbol] = price
    return prices

# Example usage
if __name__ == "__main__":
    symbols = ['BTC', 'ETH', 'SOL']
    prices = fetch_multiple_prices(symbols)
    logging.info(f"Fetched Prices: {prices}")