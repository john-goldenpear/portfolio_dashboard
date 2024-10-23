import logging
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

from src.wallet_apis.blockcypher import fetch_blockcypher_user_balance, fetch_blockcypher_transactions

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], amount: float, symbol: str) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        amount (float): Amount of the asset.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    protocol = 'wallet'
    position_type = 'hodl'
    chain = f'{symbol}'

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': symbol,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol.upper()}",
        'position_type': position_type,
        'chain': chain,
        'protocol': protocol,
        'symbol': symbol.upper(),
        'base_asset': None,
        'asset_type': None,
        'sector': None,
        'amount': amount,
        'price': np.nan,
        'value': np.nan,
        'equity': np.nan,
        'notional': np.nan,
        'cost_basis': np.nan,
        'unrealized_gain': np.nan,
        'realized_gain': np.nan,
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

def create_transaction(wallet: Dict[str, str], tx: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    """
    Helper function to create a transaction dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        tx (Dict[str, Any]): Transaction data from BlockCypher.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        Dict[str, Any]: Transaction dictionary.
    """
    is_send = wallet['address'] in tx.get('inputs', [{}])[0].get('addresses', [])
    
    amount = tx['total'] / 1e8  # Convert from satoshis to BTC/DOGE
    fee = tx.get('fees', 0) / 1e8  # Convert from satoshis to BTC/DOGE

    # Convert 'received' timestamp to datetime and round to nearest minute
    timestamp_str = tx['received']
    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    timestamp = timestamp.replace(second=0, microsecond=0) + timedelta(minutes=timestamp.second // 30)
    
    return {
        'timestamp': timestamp,
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'transaction_id': tx['hash'],
        'chain': symbol,
        'protocol': None,
        'type': 'send' if is_send else 'receive',
        'symbol': symbol.upper(),
        'amount': amount if is_send else -amount,
        'fee': fee,
        'fee_asset': symbol.upper()
    }

def fetch_and_filter_transactions(address: str, symbol: str, start_date: datetime, end_date: datetime, max_transactions: int = 1000) -> List[Dict[str, Any]]:
    """
    Fetch and filter transactions for a given address within a date range.

    Args:
        address (str): Cryptocurrency address.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').
        start_date (datetime): Start date for transaction filtering (inclusive).
        end_date (datetime): End date for transaction filtering (inclusive).
        max_transactions (int): Maximum number of transactions to fetch.

    Returns:
        List[Dict[str, Any]]: Filtered list of transactions within the specified date range.
    """
    # Ensure start_date and end_date are timezone-aware
    start_datetime = start_date.replace(tzinfo=timezone.utc)
    end_datetime = end_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)

    all_transactions = []
    before = None

    while len(all_transactions) < max_transactions:
        params = {'limit': 50}
        if before:
            params['before'] = before

        response = fetch_blockcypher_transactions(address, symbol, params)
        new_txs = response.get('txs', [])

        if not new_txs:
            break

        for tx in new_txs:
            if 'received' in tx:
                tx_time = tx['received']
                if isinstance(tx_time, str):
                    tx_time = datetime.fromisoformat(tx_time.replace('Z', '+00:00'))
                elif isinstance(tx_time, datetime):
                    tx_time = tx_time.replace(tzinfo=timezone.utc)
                else:
                    logging.warning(f"Unexpected 'received' time format in transaction: {tx}")
                    continue

                if start_datetime <= tx_time <= end_datetime:
                    all_transactions.append(tx)
                elif tx_time < start_datetime:
                    return all_transactions

        if len(new_txs) < 50:
            break

        before = new_txs[-1]['block_height']

    logging.info(f"Fetched and filtered {len(all_transactions)} transactions for {address} between {start_date.isoformat()} and {end_date.isoformat()}")
    return all_transactions

def process_blockcypher_position(blockcypher_data: Dict[str, Any], wallet: Dict[str, str], symbol: str) -> List[Dict[str, Any]]:
    """
    Process BlockCypher data for a single wallet to get position information.

    Args:
        blockcypher_data (Dict[str, Any]): Raw data pulled from BlockCypher API using fetch_blockcypher_user_balance.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        List[Dict[str, Any]]: Processed wallet position.
    """
    try:
        balance = float(blockcypher_data.get('balance', 0)) / 1e8  # Convert from satoshis to BTC/DOGE
        
        # Create position
        position = create_position(wallet, balance, symbol)
        
        logging.info(f"Processed wallet {wallet['address']} with balance {balance}")
        return [position]

    except Exception as e:
        logging.error(f"Error processing position data for wallet {wallet['address']}: {e}")
        return []

def process_blockcypher_transactions(transactions: List[Dict[str, Any]], wallet: Dict[str, str], symbol: str) -> List[Dict[str, Any]]:
    """
    Process BlockCypher transactions for a single wallet.

    Args:
        transactions (List[Dict[str, Any]]): List of transactions for the wallet.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        List[Dict[str, Any]]: Processed transactions.
    """
    if not transactions:
        logging.warning(f"No transactions provided for wallet {wallet['address']}")
        return []

    processed_transactions = []
    try:
        for tx in transactions:
            transaction = create_transaction(wallet, tx, symbol)
            processed_transactions.append(transaction)

        logging.info(f"Processed {len(processed_transactions)} transactions for wallet {wallet['address']}")
        return processed_transactions

    except Exception as e:
        logging.error(f"Error processing transaction data for wallet {wallet['address']}: {e}")
        return []

# Example usage
if __name__ == "__main__":
    # Dogecoin example
    doge_wallet = {'id': 'DOGE-1', 'address': 'ADNbM5fBujCRBW1vqezNeAWmnsLp19ki3n', 'type': 'doge', 'strategy': 'hold'}
    doge_balance = fetch_blockcypher_user_balance(doge_wallet['address'], 'doge')
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=1)
    doge_transactions = fetch_and_filter_transactions(doge_wallet['address'], 'doge', start_date, end_date)
    
    doge_position = process_blockcypher_position(doge_balance, doge_wallet, 'doge')
    doge_recent_transactions = process_blockcypher_transactions(doge_transactions, doge_wallet, 'doge')
    
    logging.info(f"Processed Doge Position: {doge_position}")
    logging.info(f"Processed Doge Transactions: {doge_recent_transactions}")
    
    # Bitcoin example
    btc_wallet = {'id': 'BTC-1', 'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'type': 'btc', 'strategy': 'hold'}
    btc_balance = fetch_blockcypher_user_balance(btc_wallet['address'], 'btc')
    
    btc_transactions = fetch_and_filter_transactions(btc_wallet['address'], 'btc', start_date, end_date)
    
    btc_position = process_blockcypher_position(btc_balance, btc_wallet, 'btc')
    btc_recent_transactions = process_blockcypher_transactions(btc_transactions, btc_wallet, 'btc')
    
    logging.info(f"Processed BTC Position: {btc_position}")
    logging.info(f"Processed BTC Transactions: {btc_recent_transactions}")

    for tx in doge_recent_transactions:
        print(tx)
        print("-" * 100)

    for tx in btc_position:
        print(tx)
        print("-" * 100)