import requests
from config import CIRCLE_API_KEY

# Define constants locally within the module
CIRCLE_BASE_URL = 'https://api.circle.com/v1/businessAccount/'
CIRCLE_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(endpoint, params=None):
    """
    Fetch data from the Circle API.

    Args:
        endpoint (str): The API endpoint to request.
        params (dict, optional): Query parameters to include in the request.

    Returns:
        dict: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{CIRCLE_BASE_URL}{endpoint}"
    headers = {
        **CIRCLE_HEADERS,
        'Authorization': 'Bearer ' + CIRCLE_API_KEY
    }
    print(f"Fetching data from {url} with params {params}")  # Debug statement
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response: {response.text}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def fetch_circle_user_balance():
    """
    Fetch balances from the Circle API.

    Returns:
        dict: The JSON response containing the balances.
    """
    return fetch_data('balances')

def fetch_circle_user_deposits():
    """
    Fetch deposits from the Circle API.

    Returns:
        dict: The JSON response containing the deposits.
    """
    return fetch_data('deposits')

def fetch_circle_user_transfers():
    """
    Fetch transfers from the Circle API.

    Returns:
        dict: The JSON response containing the transfers.
    """
    return fetch_data('transfers')

def fetch_circle_user_redemptions():
    """
    Fetch redemptions (payouts) from the Circle API.

    Returns:
        dict: The JSON response containing the redemptions.
    """
    return fetch_data('payouts')

def fetch_circle_user_wallets():
    """
    Fetch wallets from the Circle API.

    Returns:
        dict: The JSON response containing the wallets.
    """
    return fetch_data('wallets/addresses/deposit')

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    try:
        # Fetch and print Circle balance
        balances = fetch_circle_user_balance()
        print('Circle Balances:', balances)

        # Fetch and print Circle deposits
        deposits = fetch_circle_user_deposits()
        print('Circle Deposits:', deposits)

        # Fetch and print Circle transfers
        transfers = fetch_circle_user_transfers()
        print('Circle Transfers:', transfers)

        # Fetch and print Circle redemptions (payouts)
        redemptions = fetch_circle_user_redemptions()
        print('Circle Redemptions:', redemptions)

        # Fetch and print Circle wallets
        wallets = fetch_circle_user_wallets()
        print('Circle Wallets:', wallets)

    except Exception as e:
        print(f"An error occurred during the example usage: {e}")
