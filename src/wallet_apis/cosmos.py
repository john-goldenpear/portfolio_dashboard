import requests
from typing import Dict, Any, List
from config import MINTSCAN_API_KEY

MINTSCAN_API_BASE_URL = "https://api.mintscan.io/v1"  # Mintscan API base URL
MINSTCSCAN_HEADERS = {
    'Authorization': 'Bearer ' + MINTSCAN_API_KEY
}

def fetch_account_info(network: str, address: str) -> Dict[str, Any]:
    """
    Fetch account information for a given Cosmos address using Mintscan.

    Args:
        network (str): The Cosmos network identifier (e.g., 'cosmos').
        address (str): The Cosmos address.

    Returns:
        Dict[str, Any]: Account information including balances.
    """
    url = f"{MINTSCAN_API_BASE_URL}/{network}/accounts/{address}"
    headers = MINSTCSCAN_HEADERS
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_mintscan_account_balances(chain: str, address: str) -> List[Dict[str, Any]]:
    """
    Fetch account balances for a given Cosmos address using Mintscan.

    Args:
        chain (str): The Cosmos chain identifier (e.g., 'cosmos', 'osmosis').
        address (str): The Cosmos address.

    Returns:
        List[Dict[str, Any]]: List of balances.
    """
    url = f"{MINTSCAN_API_BASE_URL}/{chain}/account/{address}/balances"
    headers = MINSTCSCAN_HEADERS
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('balances', [])

def fetch_mintscan_account_transactions(chain: str, address: str) -> List[Dict[str, Any]]:
    """
    Fetch transaction history for a given Cosmos address using Mintscan.

    Args:
        chain (str): The Cosmos chain identifier (e.g., 'cosmos', 'osmosis').
        address (str): The Cosmos address.

    Returns:
        List[Dict[str, Any]]: List of transactions.
    """
    url = f"{MINTSCAN_API_BASE_URL}/{chain}/account/{address}/txs"
    headers = MINSTCSCAN_HEADERS
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('txs', [])

# Example usage
if __name__ == "__main__":
    # Example Cosmos chain identifier and address
    chain = 'cosmos'  # Replace with the actual chain identifier
    address = 'cosmos1clpqr4nrk4khgkxj78fcwwh6dl3uw4ep4tgu9q'  # Replace with the actual address

    try:
        # Fetch account balances
        balances = fetch_mintscan_account_balances(chain, address)
        print("Account Balances:")
        for balance in balances:
            print(f"Denom: {balance['denom']}, Amount: {balance['amount']}")

        # Fetch account transactions
        transactions = fetch_mintscan_account_transactions(chain, address)
        print("\nAccount Transactions:")
        for tx in transactions:
            print(f"Tx Hash: {tx['txhash']}, Height: {tx['height']}, Timestamp: {tx['timestamp']}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
