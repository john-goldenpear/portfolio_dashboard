import logging
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.wallet_apis.gemini import fetch_gemini_user_spot_balances, fetch_gemini_user_perps_positions, fetch_gemini_spot_transactions, fetch_gemini_perps_transactions

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], balance: Dict[str, Any], position_type: str) -> Dict[str, Any]:
    """
    Create a position dictionary for Gemini assets.

    Args:
        wallet (Dict[str, str]): Wallet information.
        balance (Dict[str, Any]): Balance data from Gemini API.
        position_type (str): Type of position ('spot' or 'perps').

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    chain = 'gemini'
    protocol = 'gemini'
    
    if position_type == 'spot':
        symbol = balance['currency']
        amount = float(balance['amount'])
        price = float(balance['amountNotional']) / amount if amount != 0 else 0
        position = 'cash' if symbol == 'GUSD' else symbol
    else:  # perps
        symbol = balance['symbol'].replace('gusdperp', '').upper()
        amount = float(balance['quantity'])
        price = float(balance['mark_price'])
        position = None

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'chain': 'gemini',
        'protocol': 'gemini',
        'contract_address': symbol,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'position': None,
        'position_type': position_type,
        'symbol': symbol,
        'base_asset': None,
        'asset_type': None,
        'sector': None,
        'amount': amount,
        'price': price,
        'value': amount * price,
        'equity': np.nan,
        'notional': abs(price * amount),
        'cost_basis': float(balance.get('average_cost', 0)) * amount if position_type == 'perps' else np.nan,
        'unrealized_gain': float(balance.get('unrealised_pnl', 0)) if position_type == 'perps' else np.nan,
        'realized_gain': float(balance.get('realised_pnl', 0)) if position_type == 'perps' else np.nan,
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
    Create a transaction dictionary for Gemini assets.

    Args:
        wallet (Dict[str, str]): Wallet information.
        tx (Dict[str, Any]): Transaction data from Gemini API.
        tx_type (str): Type of transaction ('spot', 'perps', 'funding', or 'transfer').

    Returns:
        Dict[str, Any]: Transaction dictionary.
    """
    try:
        if tx_type in ['spot', 'perps']:
            timestamp = datetime.fromtimestamp(tx['timestamp'] / 1000)
            symbol = tx['symbol'].split('/')[0] if tx_type == 'spot' else tx['symbol'].replace('gusdperp', '').upper()
            amount = float(tx['amount'])
            fee = float(tx.get('fee_amount', 0))
            fee_asset = tx.get('fee_currency', 'GUSD')
            transaction_type = tx['type']
            transaction_id = tx['tid']
        elif tx_type == 'funding':
            funding_data = tx['hourlyFundingTransfer']
            timestamp = datetime.fromtimestamp(funding_data['timestamp'] / 1000)
            symbol = funding_data['assetCode']
            amount = float(funding_data['quantity']['value'])
            fee = 0
            fee_asset = symbol
            transaction_type = 'Funding'
            transaction_id = f"funding-{funding_data['timestamp']}"
        elif tx_type == 'transfer':
            timestamp = datetime.fromtimestamp(tx['timestampms'] / 1000)
            symbol = tx['currency']
            amount = float(tx['amount'])
            fee = 0
            fee_asset = symbol
            transaction_type = tx['type']
            transaction_id = tx.get('transferId', f"{tx['type']}-{tx['timestampms']}-{tx['eid']}")
        else:
            raise ValueError(f"Unknown transaction type: {tx_type}")

        return {
            'timestamp': timestamp,
            'wallet_id': wallet['id'],
            'wallet_address': wallet['address'],
            'wallet_type': wallet['type'],
            'strategy': wallet['strategy'],
            'transaction_id': transaction_id,
            'chain': 'gemini',
            'protocol': 'gemini',
            'type': transaction_type,
            'symbol': symbol,
            'amount': amount,
            'fee': fee,
            'fee_asset': fee_asset
        }
    except KeyError as e:
        logging.error(f"Error processing {tx_type} transaction: Missing key {e}. Transaction data: {tx}")
        return None
    except Exception as e:
        logging.error(f"Error processing {tx_type} transaction: {e}. Transaction data: {tx}")
        return None

def process_gemini_positions(spot_data: Dict[str, Any], perps_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process Gemini balance data to create positions for both spot and perpetual futures.

    Args:
        spot_data (Dict[str, Any]): Spot balance data fetched from the Gemini API.
        perps_data (Dict[str, Any]): Perpetual futures balance data fetched from the Gemini API.
        wallet (Dict[str, str]): Dictionary containing wallet information.

    Returns:
        List[Dict[str, Any]]: List of processed positions.
    """
    positions = []

    for balance in spot_data:
        try:
            position = create_position(wallet, balance, 'spot')
            positions.append(position)
        except Exception as e:
            logging.error(f"Error processing spot position: {e}")

    for balance in perps_data:
        try:
            position = create_position(wallet, balance, 'perps')
            positions.append(position)
        except Exception as e:
            logging.error(f"Error processing perps position: {e}")

    return positions

def process_gemini_transactions(spot_txs: Dict[str, Any], perps_txs: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process Gemini transaction data for spot, perpetual futures, funding payments, and transfers.

    Args:
        spot_txs (Dict[str, Any]): Spot transactions data fetched from the Gemini API.
        perps_txs (Dict[str, Any]): Perpetual futures transactions data fetched from the Gemini API.
        wallet (Dict[str, str]): Dictionary containing wallet information.

    Returns:
        List[Dict[str, Any]]: Processed transactions.
    """
    transactions = []

    logging.info(f"Processing spot trades: {len(spot_txs.get('trades', []))}")
    logging.info(f"Processing spot transfers: {len(spot_txs.get('transfers', []))}")
    logging.info(f"Processing perps trades: {len(perps_txs.get('trades', []))}")
    logging.info(f"Processing perps transfers: {len(perps_txs.get('transfers', []))}")
    logging.info(f"Processing funding payments: {len(perps_txs.get('funding_payments', []))}")

    # Process spot trades
    for tx in spot_txs.get('trades', []):
        transaction = create_transaction(wallet, tx, 'spot')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process spot trade: {tx}")

    # Process spot transfers
    for tx in spot_txs.get('transfers', []):
        transaction = create_transaction(wallet, tx, 'transfer')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process spot transfer: {tx}")

    # Process perps trades
    for tx in perps_txs.get('trades', []):
        transaction = create_transaction(wallet, tx, 'perps')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process perps trade: {tx}")

    # Process perps transfers
    for tx in perps_txs.get('transfers', []):
        transaction = create_transaction(wallet, tx, 'transfer')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process perps transfer: {tx}")

    # Process funding payments
    for tx in perps_txs.get('funding_payments', []):
        transaction = create_transaction(wallet, tx, 'funding')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process funding payment: {tx}")

    logging.info(f"Total processed transactions: {len(transactions)}")

    return transactions

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'gemini_wallet', 'address': 'gemini_address', 'type': 'gemini', 'strategy': 'trading'}
    
    start_date = '2023-01-01'
    end_date = '2024-12-31'

    try:
        spot_balances = fetch_gemini_user_spot_balances()
        perps_positions = fetch_gemini_user_perps_positions()
        spot_transactions = fetch_gemini_spot_transactions(start_date, end_date)
        perps_transactions = fetch_gemini_perps_transactions(start_date, end_date)

        positions = process_gemini_positions(spot_balances, perps_positions, wallet)
        transactions = process_gemini_transactions(spot_transactions, perps_transactions, wallet)

        logging.info(f"Processed Gemini Positions: {positions}")
        logging.info(f"Processed Gemini Transactions: {transactions}")

    except Exception as e:
        logging.error(f"Error processing Gemini data: {e}")