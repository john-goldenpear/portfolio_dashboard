import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.apis.blockcypher import fetch_blockcypher_user_balance, fetch_blockcypher_transactions

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], amount: float, symbol: str, opened_qty: float, closed_qty: float, fees_asset_change: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        amount (float): Amount of the asset.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').
        opened_qty (float): Quantity opened in the last 24 hours.
        closed_qty (float): Quantity closed in the last 24 hours.
        fees_asset_change (float): Sum of fees for all send transactions in the last 24 hours.

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    protocol = 'wallet'
    position_type = 'hodl'

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': f'{symbol}',
        'position_id': f"{wallet['id']}-{symbol}-{protocol}-{position_type}-{symbol.upper()}",
        'chain': f'{symbol}',
        'protocol': protocol,
        'type': position_type,
        'symbol': f'{symbol.upper()}',
        'amount': amount,
        'price': None,  # Price is unknown
        'opened_qty': opened_qty,
        'closed_qty': closed_qty,
        'opened_price': None,  # Will figure out later
        'closed_price': None,  # Will figure out later
        'fees_day': fees_asset_change,
        'fees_asset': symbol
    }

def process_blockcypher_data(blockcypher_data: Dict[str, Any], wallet: Dict[str, str], symbol: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process BlockCypher data for a single wallet.

    Args:
        blockcypher_data (Dict[str, Any]): Raw data pulled from BlockCypher API using fetch_blockcypher_user_balance.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).
        symbol (str): The type of cryptocurrency ('doge' or 'btc').
        transactions (List[Dict[str, Any]]): List of transactions for the wallet.

    Returns:
        List[Dict[str, Any]]: Processed wallet data.
    """
    all_data = []
    try:
        balance = float(blockcypher_data.get('balance', 0)) / 1e8  # Convert from satoshis to BTC/DOGE
        
        # Initialize the new fields
        opened_qty = 0.0
        closed_qty = 0.0
        fees_asset_change = 0.0
        
        # Define the time window for the last 24 hours
        time_window = datetime.utcnow() - timedelta(days=1)
        
        for tx in transactions:
            tx_time_str = tx.get('received')
            if '.' in tx_time_str:
                tx_time = datetime.strptime(tx_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                tx_time = datetime.strptime(tx_time_str, '%Y-%m-%dT%H:%M:%SZ')

            if tx_time > time_window:
                is_send = any(wallet['address'] in inp['addresses'] for inp in tx['inputs'])
                if is_send:
                    closed_qty += sum(out['value'] for out in tx['outputs'] if wallet['address'] not in out['addresses']) / 1e8
                    fees_asset_change += tx['fees'] / 1e8
                else:
                    opened_qty += sum(out['value'] for out in tx['outputs'] if wallet['address'] in out['addresses']) / 1e8

        position = create_position(wallet, balance, symbol, opened_qty, closed_qty, fees_asset_change)
        all_data.append(position)

        logging.info(f"Processed wallet {wallet['address']} with balance {balance}")

    except Exception as e:
        logging.error(f"Error processing data for wallet {wallet['address']}: {e}")

    return all_data

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'DOGE-1', 'address': 'ADNbM5fBujCRBW1vqezNeAWmnsLp19ki3n', 'type': 'doge', 'strategy': 'hold'}
    blockcypher_data = fetch_blockcypher_user_balance(wallet['address'], 'doge')
    doge_transactions = fetch_blockcypher_transactions(wallet['address'], 'doge')
    doge_data = process_blockcypher_data(blockcypher_data, wallet, 'doge', doge_transactions)
    logging.info(f"Processed Doge Data: {doge_data}")
    
    wallet = {'id': 'BTC-1', 'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'type': 'btc', 'strategy': 'hold'}
    blockcypher_data = fetch_blockcypher_user_balance(wallet['address'], 'btc')
    btc_transactions = fetch_blockcypher_transactions(wallet['address'], 'btc')
    btc_data = process_blockcypher_data(blockcypher_data, wallet, 'btc', btc_transactions)
    logging.info(f"Processed BTC Data: {btc_data}")