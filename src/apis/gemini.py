import json
import base64
import hmac
import time
import hashlib
import logging
from typing import Dict, Any
from apis.utils import fetch_with_retries
from config import GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define constants locally within the module
GEMINI_BASE_URL = 'https://api.gemini.com/v1/'

def generate_signature(api_key: str, api_secret: str, payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate the signature and headers for a Gemini API request.

    Args:
        api_key (str): The API key.
        api_secret (str): The API secret.
        payload (Dict[str, Any]): The payload to be included in the request.

    Returns:
        Dict[str, str]: The headers for the API request.
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

def fetch_data(endpoint: str, headers: Dict[str, str], params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Fetch data from the Gemini API using the POST method.

    Args:
        endpoint (str): The API endpoint to request.
        headers (Dict[str, str]): The headers for the API request.
        params (Dict[str, Any], optional): Query parameters to include in the request.

    Returns:
        Dict[str, Any]: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{GEMINI_BASE_URL}{endpoint}"
    return fetch_with_retries(url, headers, params, method='POST')

def fetch_gemini_user_spot_balances() -> Dict[str, Any]:
    """
    Fetch balances for the spot market from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/notionalbalances/usd", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("notionalbalances/usd", headers, payload)

def fetch_gemini_user_spot_transactions() -> Dict[str, Any]:
    """
    Fetch transactions for the spot market from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the transactions.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/mytrades", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("mytrades", headers, payload)

def fetch_gemini_user_spot_transfers() -> Dict[str, Any]:
    """
    Fetch transfers for the spot account from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/transfers", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("transfers", headers, payload)

def fetch_gemini_user_spot_custody_fees() -> Dict[str, Any]:
    """
    Fetch custody fees for the spot account from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the custody fees.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/custodyaccountfees", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("custodyaccountfees", headers, payload)

def fetch_gemini_user_perps_account_balance() -> Dict[str, Any]:
    """
    Fetch perpetual account balance from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/notionalbalances/usd", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("notionalbalances/usd", headers, payload)

def fetch_gemini_user_perps_positions() -> Dict[str, Any]:
    """
    Fetch balances for the perpetual futures market from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the balances.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/positions", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("positions", headers, payload)

def fetch_gemini_user_perps_transactions() -> Dict[str, Any]:
    """
    Fetch transactions for the perpetual futures market from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the transactions.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/mytrades", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("mytrades", headers, payload)

def fetch_gemini_user_perps_transfers() -> Dict[str, Any]:
    """
    Fetch transfers for the perpetual futures account from the Gemini API.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/transfers", "nonce": payload_nonce}
    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("transfers", headers, payload)

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    try:
        # Fetch balances for the spot market
        spot_balances = fetch_gemini_user_spot_balances()
        logging.info(f'Spot Balances: {spot_balances}')

        # Fetch transactions for the spot market
        spot_transactions = fetch_gemini_user_spot_transactions()
        logging.info(f'Spot Transactions: {spot_transactions}')

        # Fetch transfers for the spot account
        spot_transfers = fetch_gemini_user_spot_transfers()
        logging.info(f'Spot Transfers: {spot_transfers}')

        # Fetch custody fees for the spot account
        spot_custody_fees = fetch_gemini_user_spot_custody_fees()
        logging.info(f'Spot Custody Fees: {spot_custody_fees}')

        # Fetch details for the perpetual futures account
        perps_balance = fetch_gemini_user_perps_account_balance()
        logging.info(f'Perpetual Futures Positions: {perps_balance}')
        
        # Fetch balances for the perpetual futures market
        perps_positions = fetch_gemini_user_perps_positions()
        logging.info(f'Perpetual Futures Positions: {perps_positions}')

        # Fetch transactions for the perpetual futures market
        perps_transactions = fetch_gemini_user_perps_transactions()
        logging.info(f'Perpetual Futures Transactions: {perps_transactions}')

        # Fetch transfers for the perpetual futures account
        perps_transfers = fetch_gemini_user_perps_transfers()
        logging.info(f'Perpetual Futures Transfers: {perps_transfers}')

    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")