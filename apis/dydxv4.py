import requests

DYDXV4_BASE_URL = 'https://indexer.dydx.trade/v4'
DYDXV4_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(endpoint, params=None):
    """
    Fetch data from the dydx V4 Indexer API.

    Args:
        endpoint (str): The API endpoint to request.
        headers (dict): The headers for the API request.
        params (dict, optional): Query parameters to include in the request.

    Returns:
        dict: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{DYDXV4_BASE_URL}/{endpoint}"
    print(f"URL: {url}")
    print(f"Headers: {DYDXV4_HEADERS}")
    if params:
        print(f"Params: {params}")
    try:
        response = requests.get(url, headers=DYDXV4_HEADERS, params=params)  # Use GET for fetching data
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response: {response.text}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def fetch_dydxv4_address_info(address):
    """
    Fetch dydx v4 account info for ethereum address from dydx v4 indexer API.
    This includes current positions and other information.

    Returns:
        dict: The JSON response containing the information.
    """
    return fetch_data(f'addresses/{address}')

def fetch_dydxv4_user_assets(address, subaccount_number=0):
    """
    Fetch asset positions from the dYdX V4 Indexer API.

    Args:
        address (str, optional): The address to filter trades.
        subaccount_number (int): The subaccount number to filter trades.

    Returns:
        dict: The JSON response containing the trades.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount_number
    }
    # Remove keys with None values
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_data(f'assetPositions', params)

def fetch_dydxv4_user_trades(address, subaccount_number=0, market=None, market_type=None, limit=None):
    """
    Fetch trades from the dYdX V4 Indexer API.

    Args:
        address (str, optional): The address to filter trades.
        subaccount_number (int): The subaccount number to filter trades.
        market (str, optional): The market identifier.
        market_type (str, optional): The market type ('PERPETUAL' or 'SPOT')... Doesn't seem to be working in example.
        limit (int, optional): The limit on the number of trades to fetch.

    Returns:
        dict: The JSON response containing the trades.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount_number,
        'market': market,
        'marketType': market_type,
        'limit': limit
    }
    # Remove keys with None values
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_data(f'fills', params)

def fetch_dydxv4_user_rewards(address, limit=None):
    """
    Fetch trading rewards from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        limit (int, optional): The limit on the number of trading reward records to fetch.

    Returns:
        dict: The JSON response containing the trades.
    """
    params = {
        'limit': limit
    }
    # Remove keys with None values
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_data(f'historicalBlockTradingRewards/{address}', params)

def fetch_dydxv4_user_transfers(address, subaccount=0, limit=None):
    """
    Fetch withdrawals and deposits for address and subaccount from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        subaccount_number (int): The subaccount number to pull transfers.
        limit (int, optional): The limit on the number of records to fetch.

    Returns:
        dict: The JSON response containing the trades.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount,
        'limit': limit
    }
    # Remove keys with None values
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_data(f'transfers', params)

def fetch_dydxv4_user_pnl(address, subaccount=0, limit=None, start_date=None, end_date=None):
    """
    Fetch historical pnl for address and subaccount from the dYdX V4 Indexer API.

    Args:
        address (str): The dydx wallet address.
        subaccount_number (int): The subaccount number to pull pnl.
        limit (int, optional): The limit on the number of pnl records to fetch.
        start_date (IsoString, optional): the date for which pnl record prior to this date are ignored.
        end_date (IsoString, optional): the date for which pnl record after to this date are ignored.

    Returns:
        dict: The JSON response containing the trades.
    """
    params = {
        'address': address,
        'subaccountNumber': subaccount,
        'limit': limit,
        'createdBeforeOrAt': start_date,
        'createdOnOrAfter': end_date
    }
    # Remove keys with None values
    params = {k: v for k, v in params.items() if v is not None}
    return fetch_data(f'historical-pnl', params)

if __name__ == "__main__":
    try:
        address = 'dydx18vgsfaarveyg7xy585657ak8a9jvut9z8yuzmv'  # Replace with your actual address

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

    except Exception as e:
        print(f"An error occurred during the example usage: {e}")