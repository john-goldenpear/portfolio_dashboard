import requests
import logging
from typing import Dict, Any, Optional
from config import OCTAV_BEARER_TOKEN

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define constants for the Octav API
OCTAV_API_URL = 'https://octav-api.hasura.app/v1/graphql'
OCTAV_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OCTAV_BEARER_TOKEN}'  # Ensure Bearer prefix is included
}

def fetch_octav_data(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Fetch data from the Octav API using GraphQL.

    Args:
        query (str): The GraphQL query string.
        variables (Dict[str, Any], optional): The variables for the GraphQL query.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    try:
        logging.debug(f"Sending request to Octav API with query: {query} and variables: {variables}")
        response = requests.post(
            OCTAV_API_URL,
            headers=OCTAV_HEADERS,
            json={'query': query, 'variables': variables}
        )
        response.raise_for_status()
        json_response = response.json()
        logging.debug(f"Response from Octav API: {json_response}")
        return json_response
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from Octav API: {e}")
        return {}

def fetch_octav_portfolio(address: str) -> Dict[str, Any]:
    """
    Fetch the portfolio of a given address from the Octav API.

    Args:
        address (str): The wallet address to fetch the portfolio for.

    Returns:
        Dict[str, Any]: The JSON response containing the portfolio data.
    """
    query = """
    query GetPortfolios($params: Payload!) {
        GetPortfoliosQuery(params: $params) {
            address
            assetByProtocols
            cashBalance
            chains
            closedPnl
            dailyExpense
            dailyIncome
            fees
            feesFiat
            lastUpdated
            networth
            nftChains
            nftsByCollection
            openPnl
            totalCostBasis
        }
    }
    """
    variables = {
        'params': {
            'addresses': [address]
        }
    }
    portfolio_data = fetch_octav_data(query, variables)
    logging.info(f"Portfolio data for address {address}: {portfolio_data}")
    return portfolio_data

def fetch_octav_transactions(address: str) -> Dict[str, Any]:
    """
    Fetch the transactions of a given address from the Octav API.

    Args:
        address (str): The wallet address to fetch the transactions for.

    Returns:
        Dict[str, Any]: The JSON response containing the transactions data.
    """
    query = """
    query GetTransactions($params: Payload!) {
        GetTransactionsQuery(params: $params) {
            transactions {
                assetsIn {
                    balance
                    contract
                }
                assetsOut {
                    balance
                    contract
                }
                from
                to
                timestamp
                chain {
                    name
                }
                fees
            }
        }
    }
    """
    variables = {
        'params': {
            'addresses': [address]
        }
    }
    transactions_data = fetch_octav_data(query, variables)
    logging.info(f"Transactions data for address {address}: {transactions_data}")
    return transactions_data

def sync_octav_transactions(address: str) -> Dict[str, Any]:
    """
    Sync the transactions of a given address with the Octav API.

    Args:
        address (str): The wallet address to sync the transactions for.

    Returns:
        Dict[str, Any]: The JSON response from the API after syncing transactions.
    """
    query = """
    query SyncTransactions($params: Payload!) {
        SyncTransactionsQuery(params: $params)
    }
    """
    variables = {
        'params': {
            'addresses': [address]
        }
    }
    sync_data = fetch_octav_data(query, variables)
    logging.info(f"Sync transactions data for address {address}: {sync_data}")

    # Additional logging to help debug the error
    if 'errors' in sync_data:
        for error in sync_data['errors']:
            logging.error(f"Error syncing transactions: {error}")

    return sync_data

def sync_octav_portfolio(address: str) -> Dict[str, Any]:
    """
    Sync the portfolio of a given address with the Octav API.

    Args:
        address (str): The wallet address to sync the portfolio for.

    Returns:
        Dict[str, Any]: The JSON response from the API after syncing portfolio.
    """
    query = """
    query SyncPortfolio($params: Payload!) {
        SyncPortfolioQuery(params: $params)
    }
    """
    variables = {
        'params': {
            'addresses': [address]
        }
    }
    sync_data = fetch_octav_data(query, variables)
    logging.info(f"Sync portfolio data for address {address}: {sync_data}")

    # Additional logging to help debug the error
    if 'errors' in sync_data:
        for error in sync_data['errors']:
            logging.error(f"Error syncing portfolio: {error}")

    return sync_data

if __name__ == "__main__":
    try:
        address = '0x4a4e392290a382c9d2754e5dca8581ea1893db5d'  # Replace with your actual address

        # Sync the transactions and portfolio for the address
        sync_transactions = sync_octav_transactions(address)
        logging.info(f'Sync Transactions: {sync_transactions}')

        sync_portfolio = sync_octav_portfolio(address)
        logging.info(f'Sync Portfolio: {sync_portfolio}')

        # Fetch portfolio information
        portfolio_info = fetch_octav_portfolio(address)
        logging.info(f'Portfolio Information: {portfolio_info}')

        # Fetch and print transactions information
        transactions_info = fetch_octav_transactions(address)
        logging.info(f'Transactions Information: {transactions_info}')

    except Exception as e:
        logging.error(f"An error occurred: {e}")