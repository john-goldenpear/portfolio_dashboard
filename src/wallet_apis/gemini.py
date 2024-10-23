import json
import base64
import hmac
import time
import hashlib
import logging
from typing import Dict, Any
from src.utils.utils import fetch_with_retries
from config import GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET
from datetime import datetime, timezone
from typing import Optional
import requests

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

def fetch_gemini_user_spot_trades(start_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Fetch transactions for the spot market from the Gemini API.

    Args:
        start_date (Optional[datetime]): The start date for the transaction history.

    Returns:
        Dict[str, Any]: The JSON response containing the transactions.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/mytrades", "nonce": payload_nonce}
    
    if start_date:
        timestamp = int(start_date.replace(tzinfo=timezone.utc).timestamp() * 1000)
        payload["timestamp"] = timestamp

    headers = generate_signature(GEMINI_SPOT_API_KEY, GEMINI_SPOT_API_SECRET, payload)
    return fetch_data("mytrades", headers, payload)

def fetch_gemini_user_spot_transfers(start_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Fetch transfers for the spot account from the Gemini API.

    Args:
        start_date (Optional[datetime]): The start date for the transfer history.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/transfers", "nonce": payload_nonce}
    
    if start_date:
        timestamp = int(start_date.replace(tzinfo=timezone.utc).timestamp() * 1000)
        payload["timestamp"] = timestamp

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

def fetch_gemini_user_perps_trades(start_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Fetch transactions for the perpetual futures market from the Gemini API.

    Args:
        start_date (Optional[datetime]): The start date for the transaction history.

    Returns:
        Dict[str, Any]: The JSON response containing the transactions.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/mytrades", "nonce": payload_nonce}
    
    if start_date:
        timestamp = int(start_date.replace(tzinfo=timezone.utc).timestamp() * 1000)
        payload["timestamp"] = timestamp

    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("mytrades", headers, payload)

def fetch_gemini_user_perps_transfers(start_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Fetch transfers for the perpetual futures account from the Gemini API.

    Args:
        start_date (Optional[datetime]): The start date for the transfer history.

    Returns:
        Dict[str, Any]: The JSON response containing the transfers.
    """
    payload_nonce = int(time.time() * 1000)
    payload = {"request": "/v1/transfers", "nonce": payload_nonce}
    
    if start_date:
        timestamp = int(start_date.replace(tzinfo=timezone.utc).timestamp() * 1000)
        payload["timestamp"] = timestamp

    headers = generate_signature(GEMINI_PERPS_API_KEY, GEMINI_PERPS_API_SECRET, payload)
    return fetch_data("transfers", headers, payload)

def fetch_gemini_spot_transactions(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Fetch spot transactions from Gemini API, including trades and transfers.

    Args:
        start_date (Optional[datetime]): The start date for the transaction history.
        end_date (Optional[datetime]): The end date for the transaction history.

    Returns:
        Dict[str, Any]: A dictionary containing both trades and transfers.
    """
    trades = fetch_gemini_user_spot_trades(start_date)
    transfers = fetch_gemini_user_spot_transfers(start_date)

    result = {
        "trades": trades,
        "transfers": transfers
    }

    # Add some logging to check what's being returned
    for key, value in result.items():
        logging.info(f"Spot {key}: {len(value)} items")

    return result

def fetch_gemini_perps_funding_payments(start_date: datetime, end_date: datetime, num_rows: int = 500, symbol: str = "BTCGUSDPERP") -> Dict[str, Any]:
    """
    Fetch funding payment report for perpetual futures from Gemini API.

    Args:
        start_date (datetime): Start date.
        end_date (datetime): End date.
        num_rows (int): Number of rows to return (default 500).
        symbol (str): The trading symbol (default "BTCGUSDPERP").

    Returns:
        Dict[str, Any]: The JSON response containing the funding payment report.
    """
    
    endpoint = f"perpetuals/fundingpaymentreport/records.json"
    url = f"{GEMINI_BASE_URL}{endpoint}"
    
    # Prepare payload
    payload_nonce = int(time.time() * 1000)
    payload = {
        "request": f"/v1/{endpoint}",
        "nonce": payload_nonce,
        "symbol": symbol,
        "fromDate": start_date.strftime('%Y-%m-%d'),
        "toDate": end_date.strftime('%Y-%m-%d'),
        "numRows": num_rows
    }
    
    # Encode payload
    encoded_payload = json.dumps(payload).encode()
    b64 = base64.b64encode(encoded_payload)
    
    # Generate signature
    signature = hmac.new(GEMINI_PERPS_API_SECRET.encode(), b64, hashlib.sha384).hexdigest()
    
    # Prepare headers
    headers = {
        'Content-Type': "text/plain",
        'Content-Length': "0",
        'X-GEMINI-APIKEY': GEMINI_PERPS_API_KEY,
        'X-GEMINI-PAYLOAD': b64.decode(),
        'X-GEMINI-SIGNATURE': signature,
        'Cache-Control': "no-cache"
    }
    
    # Prepare GET parameters
    params = {
        "symbol": symbol,
        "fromDate": start_date.strftime('%Y-%m-%d'),
        "toDate": end_date.strftime('%Y-%m-%d'),
        "numRows": num_rows
    }
    
    # Make the GET request
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()

# Update the fetch_gemini_perps_transactions function
def fetch_gemini_perps_transactions(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Fetch perpetual futures transactions from Gemini API, including trades, transfers, and funding payments.

    Args:
        start_date (datetime): Start date.
        end_date (datetime): End date.

    Returns:
        Dict[str, Any]: Perpetual futures transaction data.
    """
    trades = fetch_gemini_user_perps_trades(start_date)
    transfers = fetch_gemini_user_perps_transfers(start_date)
    funding_payments = fetch_gemini_perps_funding_payments(start_date, end_date)

    result = {
        "trades": trades,
        "transfers": transfers,
        "funding_payments": funding_payments
    }

    # Add some logging to check what's being returned
    for key, value in result.items():
        logging.info(f"{key}: {len(value)} items")

    return result

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    try:
        # specify date range for data retrieval
        start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
        
        # Fetch balances for the spot market
        spot_balances = fetch_gemini_user_spot_balances()
        logging.info(f'Spot Balances: {spot_balances}')

        # Fetch transactions for the spot market
        spot_trades = fetch_gemini_user_spot_trades(start_date)
        logging.info(f'Spot Trades: {spot_trades}')

        # Fetch transfers for the spot account
        spot_transfers = fetch_gemini_user_spot_transfers(start_date)
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

        # Fetch transfers for the perpetual futures account
        perps_transfers = fetch_gemini_user_perps_transfers(start_date)
        logging.info(f'Perpetual Futures Transfers: {perps_transfers}')

        # fetch perps trades
        perps_trades = fetch_gemini_user_perps_trades(start_date)
        logging.info(f'Perpetual Futures Trades: {perps_trades}')

        # Fetch funding payment report for perpetual futures
        funding_payments = fetch_gemini_perps_funding_payments(start_date, end_date)
        logging.info(f'Funding Payments: {funding_payments}')

        # Fetch transactions for the perpetual futures account with date range
        perps_transactions = fetch_gemini_perps_transactions(start_date, end_date)
        logging.info(f'Perpetual Futures Transactions: {perps_transactions}')

    except Exception as e:
        logging.error(f"An error occurred during the example usage: {e}")