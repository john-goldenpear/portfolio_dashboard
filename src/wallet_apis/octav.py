import requests
import logging
from typing import Dict, Any, Optional
from config import OCTAV_BEARER_TOKEN

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define constants for the Octav API
OCTAV_API_BASE_URL = 'https://octav-api.hasura.app/api/rest'
OCTAV_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OCTAV_BEARER_TOKEN}'  # Ensure Bearer prefix is included
}

def fetch_octav_portfolio(address: str, aggregated: bool = False) -> Dict[str, Any]:
    """
    Fetch the portfolio of a given address from the Octav REST API.

    Args:
        address (str): The wallet address to fetch the portfolio for.
        aggregated (bool): Whether to fetch aggregated data.

    Returns:
        Dict[str, Any]: The JSON response containing the portfolio data.
    """
    url = f"{OCTAV_API_BASE_URL}/portfolio"
    params = {
        'addresses': address,
        'aggregated': str(aggregated).lower()  # Convert boolean to lowercase string
    }
    try:
        logging.debug(f"Sending request to Octav API for portfolio: {url} with params: {params}")
        response = requests.get(url, headers=OCTAV_HEADERS, params=params)
        response.raise_for_status()
        portfolio_data = response.json()
        logging.debug(f"Portfolio data for address {address}: {portfolio_data}")
        return portfolio_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching portfolio data from Octav API: {e}")
        return {}

def fetch_octav_transactions(
    address: str,
    limit: int = 10,
    offset: int = 0,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    hide_spam: str = 'true',
    sort: str = 'DESC',
    initial_search_text: Optional[str] = None,
    interacting_addresses: Optional[str] = None,
    networks: Optional[str] = None,
    tx_types: Optional[str] = None,
    protocols: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch transactions for a given address from the Octav REST API.

    Args:
        address (str): The wallet address to fetch transactions for.
        limit (int): The number of transactions to retrieve per page.
        offset (int): The offset for pagination.
        start_date (str, optional): The start date for filtering transactions.
        end_date (str, optional): The end date for filtering transactions.
        hide_spam (str): Filter out spam transactions if specified.
        sort (str): Sort order for the transactions.
        initial_search_text (str, optional): Initial search text to filter transactions.
        interacting_addresses (str, optional): A comma-separated list of interacting addresses.
        networks (str, optional): A comma-separated list of networks to filter transactions.
        tx_types (str, optional): A comma-separated list of transaction types to filter by.
        protocols (str, optional): A comma-separated list of protocols to filter by.
        status (str, optional): Filter transactions by status.

    Returns:
        Dict[str, Any]: The JSON response containing the transactions data.
    """
    url = f"{OCTAV_API_BASE_URL}/transactions"
    params = {
        'addresses': address,
        'limit': limit,
        'offset': offset,
        'startDate': start_date,
        'endDate': end_date,
        'hideSpam': hide_spam,
        'sort': sort,
        'initialSearchText': initial_search_text,
        'interactingAddresses': interacting_addresses,
        'networks': networks,
        'txTypes': tx_types,
        'protocols': protocols,
        'status': status
    }
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}

    try:
        logging.debug(f"Sending request to Octav API for transactions: {url} with params: {params}")
        response = requests.get(url, headers=OCTAV_HEADERS, params=params)
        response.raise_for_status()
        transactions_data = response.json()
        logging.debug(f"Transactions data for address {address}: {transactions_data}")
        return transactions_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching transactions data from Octav API: {e}")
        return {}

def fetch_octav_status(address: str) -> Dict[str, Any]:
    """
    Fetch the status for a given address from the Octav REST API.

    Args:
        address (str): The wallet address to fetch the status for.

    Returns:
        Dict[str, Any]: The JSON response containing the status data.
    """
    url = f"{OCTAV_API_BASE_URL}/status"
    params = {
        'addresses': address
    }
    try:
        logging.debug(f"Sending request to Octav API for status: {url} with params: {params}")
        response = requests.get(url, headers=OCTAV_HEADERS, params=params)
        response.raise_for_status()
        status_data = response.json()
        logging.debug(f"Status data for address {address}: {status_data}")
        return status_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching status from Octav API: {e}")
        return {}

if __name__ == "__main__":
    try:
        address = '4k8GVZEdH3M2coXZwnyEhg2TwWXpVmPefbmvWeb2SrrZ'  # Replace with your actual address

        # Fetch portfolio information
        portfolio_info = fetch_octav_portfolio(address)
        logging.info(f'Portfolio Information: {portfolio_info}')

        status_info = fetch_octav_status(address)
        logging.info(f'Status Information: {status_info}')

        # Fetch and print transactions information
        transactions_info = fetch_octav_transactions(
            address,
            start_date=None,
            end_date=None
        )
        logging.info(f'Transactions Information: {transactions_info}')

    except Exception as e:
        logging.error(f"An error occurred: {e}")

''''from config import WALLETS
for wallet in WALLETS:
    if wallet['type'] == 'EVM':
        status_info = fetch_octav_status(wallet['address'])
        print(status_info)

wallet = WALLETS[4]
portfolio_info = fetch_octav_portfolio(wallet['address'])
status_info = fetch_octav_status(wallet['address'])
print(status_info)

wallet_2 = '0x7fea76e6f6148fd2fc5bb644381bea4862b913b5'
portfolio_info = fetch_octav_portfolio(wallet_2)
status_info = fetch_octav_status(wallet_2)
print(status_info)'''
