import requests
import json
import base64
import hmac
import time
import hashlib
from config import GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET

# Define constants locally within the module
GEMINI_BASE_URL = 'https://api.gemini.com/v1/'

def generate_signature(api_key, api_secret, payload):
    """
    Generate the signature and headers for a Gemini API request.

    Args:
        api_key (str): The API key.
        api_secret (str): The API secret.
        payload (dict): The payload to be included in the request.

    Returns:
        dict: The headers for the API request.
    """
    gemini_api_secret = api_secret.encode()
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

    headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': api_key,
        'X-GEMINI-PAYLOAD': b64.decode(),
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }
    return headers

def fetch_data(endpoint, headers, params=None):
    """
    Fetch data from the Gemini API.

    Args:
        endpoint (str): The API endpoint to request.
        headers (dict): The headers for the API request.
        params (dict, optional): Query parameters to include in the request.

    Returns:
        dict: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{GEMINI_BASE_URL}{endpoint}"
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    if params:
        print(f"Params: {params}")
    try:
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response: {response.text}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    
def fetch_gemini_user_spot_balances():
    """
    Fetch balances for the perpetual futures market from the Gemini API.

    Returns:
        dict: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/notionalbalances/usd", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("notionalbalances/usd", headers)

def fetch_gemini_user_spot_transactions():
    """
    Fetch transactions for the spot market from the Gemini API.

    Returns:
        dict: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/mytrades", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("mytrades", headers)

def fetch_gemini_user_spot_transfers():
    """
    Fetch transfers for the spot account from the Gemini API.

    Returns:
        dict: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/transfers", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("transfers", headers)

def fetch_gemini_user_spot_custody_fees():
    """
    Fetch custody fees for the spot account from the Gemini API.

    Returns:
        dict: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/custodyaccountfees", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("custodyaccountfees", headers)

def fetch_gemini_user_perps_balances():
    """
    Fetch balances for the perpetual futures market from the Gemini API.

    Returns:
        dict: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/notionalbalances/usd", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("notionalbalances/usd", headers)

def fetch_gemini_user_perps_transactions():
    """
    Fetch transactions for the perpetual futures market from the Gemini API.

    Returns:
        dict: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/mytrades", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("mytrades", headers)

def fetch_gemini_user_perps_transfers():
    """
    Fetch transfers for the perpetual futures account from the Gemini API.

    Returns:
        dict: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/transfers", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("transfers", headers)

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    # Fetch balances for the spot market
    spot_balances = fetch_gemini_user_spot_balances()
    print('Spot Balances:', spot_balances)

    # Fetch transactions for the spot market
    spot_transactions = fetch_gemini_user_spot_transactions()
    print('Spot Transactions:', spot_transactions)

    # Fetch transfers for the spot account
    spot_transfers = fetch_gemini_user_spot_transfers()
    print('Spot Transfers:', spot_transfers)

    # Fetch custody fees for the spot account
    spot_custody_fees = fetch_gemini_user_spot_custody_fees()
    print('Spot Custody Fees:', spot_custody_fees)

    # Fetch balances for the perpetual futures market
    perps_balances = fetch_gemini_user_perps_balances()
    print('Perpetual Futures Balances:', perps_balances)

    # Fetch transactions for the perpetual futures market
    perps_transactions = fetch_gemini_user_perps_transactions()
    print('Perpetual Futures Transactions:', perps_transactions)

    # Fetch transfers for the perpetual futures account
    perps_transfers = fetch_gemini_user_perps_transfers()
    print('Perpetual Futures Transfers:', perps_transfers)