import logging
from typing import Dict, Any
from src.utils.utils import fetch_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_relayer_positions(wallet_address: str) -> Dict[str, Any]:
    """
    Fetch relayer positions for a given wallet address.

    Args:
        wallet_address (str): The wallet address to fetch relayer positions for.

    Returns:
        Dict[str, Any]: The relayer positions data.
    """
    url = f"https://stats.mydefi.wtf/cache/wallet_{wallet_address}.json"
    return fetch_with_retries(url, {})

# Example usage
if __name__ == "__main__":
    try:
        wallet_address = '0x4a4e392290A382C9d2754E5Dca8581eA1893db5D'
        positions = fetch_relayer_positions(wallet_address)
        logging.info(f"Relayer positions for {wallet_address}: {positions}")
    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")