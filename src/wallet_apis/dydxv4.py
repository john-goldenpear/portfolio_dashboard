import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import concurrent.futures
import requests

from src.utils.utils import fetch_with_retries

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

def fetch_dydxv4_user_fills(
    address: str,
    subaccount_number: int = 0,
    market: Optional[str] = None,
    market_type: Optional[str] = None,
    limit: Optional[int] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Fetch fills (trades) for a specific user from the dYdX V4 Indexer API.

    Args:
        address (str): The address to filter fills.
        subaccount_number (int, optional): The subaccount number to filter fills. Defaults to 0.
        market (str, optional): The market to filter fills (e.g., 'ETH-USD').
        market_type (str, optional): The market type to filter fills ('PERPETUAL' or 'SPOT').
        limit (int, optional): The maximum number of fills to fetch.
        end_date (datetime, optional): End date to fetch fills created before or at.

    Returns:
        Dict[str, Any]: The JSON response containing the fills.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount_number,
    }

    if market:
        params['market'] = market
        params['marketType'] = 'PERPETUAL'  # Always set marketType when market is provided
    if market_type:
        params['marketType'] = market_type
    if limit:
        params['limit'] = limit
    
    if end_date:
        params['createdBeforeOrAt'] = end_date.isoformat()

    return fetch_data('fills', params)

def fetch_dydxv4_user_fills_with_start_date(
    address: str,
    subaccount_number: int = 0,
    market: Optional[str] = None,
    market_type: Optional[str] = None,
    limit: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Fetch and filter fills (trades) for a specific user from the dYdX V4 Indexer API.

    Args:
        address (str): The address to filter fills.
        subaccount_number (int, optional): The subaccount number to filter fills. Defaults to 0.
        market (str, optional): The market to filter fills (e.g., 'ETH-USD').
        market_type (str, optional): The market type to filter fills ('PERPETUAL' or 'SPOT').
        limit (int, optional): The maximum number of fills to fetch.
        start_date (datetime, optional): Start date to filter fills created on or after.
        end_date (datetime, optional): End date to fetch fills created before or at.

    Returns:
        List[Dict[str, Any]]: A list of fills filtered by the given criteria.
    """
    fills_response = fetch_dydxv4_user_fills(
        address, subaccount_number, market, market_type, limit, end_date
    )

    fills = fills_response.get('fills', [])

    if start_date:
        fills = [
            fill for fill in fills
            if datetime.fromisoformat(fill['createdAt'].replace('Z', '+00:00')) >= start_date
        ]

    return fills

def fetch_dydxv4_user_rewards(
    address: str,
    limit: Optional[int] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Fetch trading rewards for an address from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        limit (int, optional): The limit on the number of records to fetch.
        end_date (datetime, optional): End date to fetch rewards starting before or at.

    Returns:
        Dict[str, Any]: The JSON response containing the trading rewards.
    """
    params = {}
    if limit is not None:
        params['limit'] = limit
    if end_date:
        params['startingBeforeOrAt'] = end_date.isoformat()

    return fetch_data(f'historicalBlockTradingRewards/{address}', params)

def fetch_dydxv4_user_rewards_with_start_date(
    address: str,
    limit: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Fetch and filter trading rewards for an address from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        limit (int, optional): The limit on the number of records to fetch.
        start_date (datetime, optional): Start date to filter rewards created on or after.
        end_date (datetime, optional): End date to fetch rewards starting before or at.

    Returns:
        List[Dict[str, Any]]: A list of rewards filtered by the given criteria.
    """
    rewards_response = fetch_dydxv4_user_rewards(address, limit, end_date)
    rewards = rewards_response.get('rewards', [])

    if start_date:
        rewards = [
            reward for reward in rewards
            if datetime.fromisoformat(reward['createdAt'].replace('Z', '+00:00')) >= start_date
        ]

    return rewards

def fetch_dydxv4_user_transfers(
    address: str,
    subaccount: int = 0,
    limit: Optional[int] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Fetch withdrawals and deposits for an address and subaccount from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        subaccount (int, optional): The subaccount number to pull transfers. Defaults to 0.
        limit (int, optional): The limit on the number of records to fetch.
        end_date (datetime, optional): End date to fetch transfers created before or at.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount,
        'limit': limit
    }

    if end_date:
        params['createdBeforeOrAt'] = end_date.isoformat()

    return fetch_data('transfers', params)

def fetch_dydxv4_user_transfers_with_date_range(
    address: str,
    subaccount: int = 0,
    limit: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Fetch and filter withdrawals and deposits for an address and subaccount from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        subaccount (int, optional): The subaccount number to pull transfers. Defaults to 0.
        limit (int, optional): The limit on the number of records to fetch.
        start_date (datetime, optional): Start date to filter transfers created on or after.
        end_date (datetime, optional): End date to fetch transfers created before or at.

    Returns:
        List[Dict[str, Any]]: A list of transfers filtered by the given criteria.
    """
    transfers_response = fetch_dydxv4_user_transfers(address, subaccount, limit, end_date)
    transfers = transfers_response.get('transfers', [])

    if start_date:
        transfers = [
            transfer for transfer in transfers
            if datetime.fromisoformat(transfer['createdAt'].replace('Z', '+00:00')) >= start_date
        ]

    return transfers

def fetch_dydxv4_oracle_price(ticker: str) -> str:
    """
    Fetch the oracle price for a given ticker from dYdX v4.

    Args:
        ticker (str): The ticker symbol (e.g., 'ETH-USD').

    Returns:
        str: The oracle price as a string.

    Raises:
        Exception: If there's an error fetching the data or the ticker is not found.
    """
    url = f"{DYDXV4_BASE_URL}/perpetualMarkets"
    response = requests.get(url, headers=DYDXV4_HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        markets = data.get('markets', {})
        if ticker in markets:
            return markets[ticker].get('oraclePrice', '0')
        else:
            raise Exception(f"Market data not found for ticker: {ticker}")
    else:
        raise Exception(f"Failed to fetch oracle price for {ticker}. Status code: {response.status_code}")

# Example usage
if __name__ == "__main__":
    try:
        address = 'dydx13wst4xmaj77x7e6zmpd8p0ynek0ds95ffuss8n'  # Replace with your actual address

        # Fetch address info
        address_info = fetch_dydxv4_address_info(address)
        print('Address Info:', address_info)

        # Fetch oracle price
        price = fetch_dydxv4_oracle_price('SOL-USD')

        # Fetch user assets
        assets = fetch_dydxv4_user_assets(address)
        print('User Assets:', assets)

        # Fetch user PnL
        pnl = fetch_dydxv4_user_pnl(address, start_date='2023-01-01', end_date='2023-12-31')
        print('User PnL:', pnl)

        # Fetch perpetual positions
        positions = fetch_dydxv4_perpetual_positions(address)
        print('Perpetual Positions:', positions)

        # Fetch user fills with date range
        fills = fetch_dydxv4_user_fills_with_start_date(
            address,
            market='ETH-USD',
            limit=10,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
        )
        print('User Fills:', fills)

        # Fetch user rewards with date range
        rewards = fetch_dydxv4_user_rewards_with_start_date(
            address,
            limit=10,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
        )
        print('User Rewards:', rewards)

        # Fetch user transfers with date range
        transfers = fetch_dydxv4_user_transfers_with_date_range(
            address,
            limit=10,
            start_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 12, 31, tzinfo=timezone.utc)
        )
        print('User Transfers:', transfers)

    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")


        for position in positions['positions']:
            print(position)
            print('-' * 100)