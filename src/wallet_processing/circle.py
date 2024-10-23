import logging
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

from src.wallet_apis.circle import fetch_circle_user_balance, fetch_circle_user_deposits, fetch_circle_user_transfers, fetch_circle_user_redemptions

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], balance: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a position dictionary for Circle USDC.

    Args:
        wallet (Dict[str, str]): Wallet information.
        balance (Dict[str, Any]): Balance data from Circle API.

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    chain = 'circle'
    protocol = 'circle'
    position = 'cash'
    position_type = 'cash'
    symbol = 'USDC'

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'chain': chain,
        'protocol': protocol,
        'contract_address': symbol,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'position': position,
        'position_type': position_type,
        'symbol': symbol,
        'base_asset': None,
        'asset_type': None,
        'sector': None,
        'amount': float(balance['amount']),
        'price': np.nan,
        'value': np.nan,
        'equity': np.nan,
        'notional': np.nan,
        'cost_basis': np.nan,
        'unrealized_gain': np.nan, 
        'realized_gain': np.nan, # fill later    
        'funding': np.nan,
        'rewards': np.nan,
        'rewards_asset': np.nan,
        'income': np.nan,
        'income_asset': np.nan,
        'interest_exp': np.nan,
        'interest_asset': np.nan,
        'net_income_usd': np.nan,
        'fees': np.nan,
        'fee_asset': np.nan,
        'fees_usd': np.nan
    }

def create_transaction(wallet: Dict[str, str], tx: Dict[str, Any], tx_type: str) -> Dict[str, Any]:
    """
    Create a transaction dictionary for Circle USDC.

    Args:
        wallet (Dict[str, str]): Wallet information.
        tx (Dict[str, Any]): Transaction data from Circle API.
        tx_type (str): Type of transaction ('deposit', 'transfer', or 'redemption').

    Returns:
        Dict[str, Any]: Transaction dictionary.
    """
    amount = float(tx['amount']['amount'])
    if tx_type in ['transfer', 'redemption']:
        amount = -amount  # Outgoing transactions are negative

    timestamp = datetime.fromisoformat(tx['createDate'].replace('Z', '+00:00'))
    timestamp = timestamp.replace(second=0, microsecond=0) + timedelta(minutes=timestamp.second // 30)

    return {
        'timestamp': timestamp,
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'transaction_id': tx['id'],
        'chain': 'circle',
        'protocol': 'circle',
        'type': tx_type,
        'symbol': 'USDC',
        'amount': amount,
        'fee': 0,  # Circle doesn't charge fees for these operations
        'fee_asset': 'USDC'
    }

def process_circle_positions(circle_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process Circle balance data to create positions.

    Args:
        circle_data (Dict[str, Any]): Data fetched from the Circle API.
        wallet (Dict[str, str]): Dictionary containing wallet information.

    Returns:
        List[Dict[str, Any]]: List of processed positions.
    """
    positions = []
    available_balance = circle_data.get('data', {}).get('available', [])
    if available_balance:
        position = create_position(wallet, available_balance[0])
        positions.append(position)
    return positions

def process_circle_transactions(wallet: Dict[str, str], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Process Circle transaction data to create a list of transactions within a date range.

    Args:
        wallet (Dict[str, str]): Dictionary containing wallet information.
        start_date (datetime): Start date for fetching transactions.
        end_date (datetime): End date for fetching transactions.

    Returns:
        List[Dict[str, Any]]: List of processed transactions.
    """
    transactions = []
    
    deposits = fetch_circle_user_deposits(start_date, end_date)
    transfers = fetch_circle_user_transfers(start_date, end_date)
    redemptions = fetch_circle_user_redemptions(start_date, end_date)
    
    for deposit in deposits.get('data', []):
        transactions.append(create_transaction(wallet, deposit, 'deposit'))
    
    for transfer in transfers.get('data', []):
        transactions.append(create_transaction(wallet, transfer, 'transfer'))
    
    for redemption in redemptions.get('data', []):
        transactions.append(create_transaction(wallet, redemption, 'redemption'))
    
    return transactions

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'circle', 'address': 'circle', 'type': 'circle', 'strategy': 'hold'}
    circle_data = fetch_circle_user_balance()
    
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
    
    positions = process_circle_positions(circle_data, wallet)
    transactions = process_circle_transactions(wallet, start_date, end_date)
    
    logging.info(f"Processed Circle Positions: {positions}")
    logging.info(f"Processed Circle Transactions: {transactions}")

    for tx in transactions:
        print(tx)
        print("-" * 100)

    for position in positions:
        print(position)
        print("-" * 100)
