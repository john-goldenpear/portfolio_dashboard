import requests
import logging
from typing import Dict, Any, Optional

from src.apis.utils import fetch_with_retries

# Configure logging
logging.basicConfig(level=logging.INFO)

DYDXV4_BASE_URL = 'https://indexer.dydx.trade/v4'
DYDXV4_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from the dydx V4 Indexer API.

    Args:
        endpoint (str): The API endpoint to request.
        params (Dict[str, Any], optional): Query parameters to include in the request.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{DYDXV4_BASE_URL}/{endpoint}"
    return fetch_with_retries(url, headers=DYDXV4_HEADERS, params=params)

def fetch_dydxv4_address_info(address: str) -> Dict[str, Any]:
    """
    Fetch dydx v4 account info for an Ethereum address from the dydx v4 indexer API.

    Args:
        address (str): The Ethereum address to fetch information for.

    Returns:
        Dict[str, Any]: The JSON response containing the information.
    """
    return fetch_data(f'addresses/{address}')

def fetch_dydxv4_user_assets(address: str, subaccount_number: int = 0) -> Dict[str, Any]:
    """
    Fetch asset positions from the dYdX V4 Indexer API.

    Args:
        address (str): The address to filter trades.
        subaccount_number (int, optional): The subaccount number to filter trades. Defaults to 0.

    Returns:
        Dict[str, Any]: The JSON response containing the asset positions.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount_number
    }
    return fetch_data('assetPositions', params)

def fetch_dydxv4_user_trades(address: str, subaccount_number: int = 0, market: Optional[str] = None, market_type: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Fetch trades from the dYdX V4 Indexer API.

    Args:
        address (str): The address to filter trades.
        subaccount_number (int, optional): The subaccount number to filter trades. Defaults to 0.
        market (str, optional): The market identifier.
        market_type (str, optional): The market type ('PERPETUAL' or 'SPOT').
        limit (int, optional): The limit on the number of trades to fetch.

    Returns:
        Dict[str, Any]: The JSON response containing the trades.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount_number,
        'market': market,
        'marketType': market_type,
        'limit': limit
    }
    return fetch_data('fills', params)

def fetch_dydxv4_user_rewards(address: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Fetch trading rewards from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        limit (int, optional): The limit on the number of trading reward records to fetch.

    Returns:
        Dict[str, Any]: The JSON response containing the trading rewards.
    """
    params = {
        'limit': limit
    }
    return fetch_data(f'historicalBlockTradingRewards/{address}', params)

def fetch_dydxv4_user_transfers(address: str, subaccount: int = 0, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Fetch withdrawals and deposits for an address and subaccount from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        subaccount (int, optional): The subaccount number to pull transfers. Defaults to 0.
        limit (int, optional): The limit on the number of records to fetch.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount,
        'limit': limit
    }
    return fetch_data('transfers', params)

def fetch_dydxv4_user_pnl(address: str, subaccount: int = 0, limit: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch historical PnL for an address and subaccount from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        subaccount (int, optional): The subaccount number to pull PnL. Defaults to 0.
        limit (int, optional): The limit on the number of PnL records to fetch.
        start_date (str, optional): The date for which PnL records prior to this date are ignored.
        end_date (str, optional): The date for which PnL records after this date are ignored.

    Returns:
        Dict[str, Any]: The JSON response containing the PnL.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount,
        'limit': limit,
        'createdBeforeOrAt': start_date,
        'createdOnOrAfter': end_date
    }
    return fetch_data('historical-pnl', params)

def fetch_dydxv4_perpetual_positions(address: str, subaccount_number: int = 0, market: Optional[str] = None, limit: Optional[int] = None, created_before_or_at: Optional[str] = None, created_on_or_after: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch perpetual positions from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        subaccount_number (int, optional): The subaccount number. Defaults to 0.
        market (str, optional): The market identifier.
        limit (int, optional): The limit on the number of positions to fetch.
        created_before_or_at (str, optional): Fetch positions created before or at this timestamp.
        created_on_or_after (str, optional): Fetch positions created on or after this timestamp.

    Returns:
        Dict[str, Any]: The JSON response containing the perpetual positions.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount_number,
        'market': market,
        'limit': limit,
        'createdBeforeOrAt': created_before_or_at,
        'createdOnOrAfter': created_on_or_after
    }
    return fetch_data('perpetualPositions', params)

# Example usage
if __name__ == "__main__":
    try:
        address = 'dydx1apl362xyztk6kg6kujnlashx8zsjlkcxnv4uud'  # Replace with your actual address

        # Fetch and print address information
        address_info = fetch_dydxv4_address_info(address)
        print('Address Information:', address_info)

        # Fetch and print asset positions
        assets = fetch_dydxv4_user_assets(address)
        print('Asset Positions:', assets)

        # Fetch and print recent trades
        trades = fetch_dydxv4_user_trades(address, subaccount_number=0, market=None, limit=10)
        print('Trades:', trades)

        # Fetch and print trading rewards
        rewards = fetch_dydxv4_user_rewards(address, limit=10)
        print('Trading Rewards:', rewards)

        # Fetch and print transfers
        transfers = fetch_dydxv4_user_transfers(address, subaccount=0, limit=10)
        print('Transfers:', transfers)

        # Fetch and print historical pnl
        pnl = fetch_dydxv4_user_pnl(address, subaccount=0, limit=10, start_date='2024-01-01T00:00:00Z', end_date='2024-12-31T23:59:59Z')
        print('Historical PnL:', pnl)

        # Fetch and print perpetual positions
        perpetual_positions = fetch_dydxv4_perpetual_positions(address, subaccount_number=0, market=None, limit=10)
        print('Perpetual Positions:', perpetual_positions)

    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")