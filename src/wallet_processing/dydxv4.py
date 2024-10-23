import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
import numpy as np

from src.wallet_apis.dydxv4 import (
    fetch_dydxv4_user_assets,
    fetch_dydxv4_perpetual_positions,
    fetch_dydxv4_user_fills_with_start_date,
    fetch_dydxv4_user_rewards_with_start_date,
    fetch_dydxv4_user_transfers_with_date_range,
    fetch_dydxv4_oracle_price,
    fetch_dydxv4_address_info
)

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], asset: Dict[str, Any], position_type: str) -> Dict[str, Any]:
    """
    Create a position dictionary for dYdX v4 assets.

    Args:
        wallet (Dict[str, str]): Wallet information.
        asset (Dict[str, Any]): Asset data from dYdX v4 API.
        position_type (str): Type of position ('spot' or 'perps').

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    chain = 'dydx'
    protocol = 'dydxv4'

    if position_type == 'spot' or position_type == 'cash':
        symbol = asset['symbol']
        amount = float(asset['size'])
        price = 1.0 if symbol == 'USDC' else np.nan  # Assuming USDC is always 1:1 with USD
        fee_asset = symbol
        equity = amount  # Equity is equal to the balance for spot positions
        position = 'cash' if symbol == 'USDC' else None
    else:  # perps
        market = asset['market']
        symbol = market.rstrip('-USD')
        amount = float(asset['size'])
        entry_price = float(asset['entryPrice'])
        position = None
        
        # Fetch the current oracle price
        try:
            oracle_price = float(fetch_dydxv4_oracle_price(market))
        except Exception as e:
            logging.warning(f"Failed to fetch oracle price for {symbol}: {e}. Using entry price instead.")
            oracle_price = entry_price

        price = oracle_price
        fee_asset = 'USDC'  # Fees for perpetual positions are in USDC
        equity = np.nan  # Equity will be calculated separately for perps

    position = {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet.get('strategy', ''),
        'chain': chain,
        'protocol': protocol,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'position': None,
        'position_type': position_type,
        'asset_type': np.nan,
        'symbol': symbol,
        'base_asset': None,
        'asset_type': None,
        'sector': None,
        'amount': amount,
        'price': price,
        'value': price * amount,
        'equity': equity,
        'notional': abs(price * amount),
        'cost_basis': entry_price * amount if position_type == 'perps' else np.nan,
        'unrealized_gain': float(asset.get('unrealizedPnl', 0)) if position_type == 'perps' else np.nan,
        'realized_gain': float(asset.get('realizedPnl', 0)) if position_type == 'perps' else np.nan,
        'funding': float(asset.get('netFunding', 0)) if position_type == 'perps' else np.nan,
        'rewards': 0,
        'rewards_asset': None,
        'income': np.nan,
        'income_asset': np.nan,
        'interest_exp': 0,
        'interest_asset': None,
        'net_income_usd': 0,
        'fees': np.nan,
        'fee_asset': np.nan,
        'fees_usd': np.nan
    }

    print ('position_id', position['position_id'])
    return position

def create_transaction(wallet: Dict[str, str], tx: Dict[str, Any], tx_type: str) -> Dict[str, Any]:
    """
    Create a transaction dictionary for dYdX v4 assets.

    Args:
        wallet (Dict[str, str]): Wallet information.
        tx (Dict[str, Any]): Transaction data from dYdX v4 API.
        tx_type (str): Type of transaction ('fill', 'reward', or 'transfer').

    Returns:
        Dict[str, Any]: Transaction dictionary.
    """
    try:
        if tx_type == 'fill':
            timestamp = datetime.fromisoformat(tx['createdAt'].rstrip('Z'))
            symbol = tx['market']
            amount = float(tx['size'])
            price = float(tx['price'])
            fee = float(tx['fee'])
            fee_asset = 'USDC'
            transaction_type = 'Buy' if tx['side'] == 'BUY' else 'Sell'
            transaction_id = tx['id']
        elif tx_type == 'reward':
            timestamp = datetime.fromisoformat(tx['createdAt'].rstrip('Z'))
            symbol = 'USDC'  # Assuming rewards are in USDC
            amount = float(tx['tradingReward'])
            price = 1.0
            fee = 0
            fee_asset = 'USDC'
            transaction_type = 'Reward'
            transaction_id = f"reward-{tx['createdAt']}"
        elif tx_type == 'transfer':
            timestamp = datetime.fromisoformat(tx['createdAt'].rstrip('Z'))
            symbol = tx['symbol']
            amount = float(tx['size'])
            price = 1.0 if symbol == 'USDC' else np.nan
            fee = 0
            fee_asset = symbol
            transaction_type = tx['type'].capitalize()
            transaction_id = tx['id']
        else:
            raise ValueError(f"Unknown transaction type: {tx_type}")

        return {
            'timestamp': timestamp,
            'wallet_id': wallet['id'],
            'wallet_address': wallet['address'],
            'wallet_type': wallet['type'],
            'strategy': wallet['strategy'],
            'transaction_id': transaction_id,
            'chain': 'dydx',
            'protocol': 'dydxv4',
            'type': transaction_type,
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'fee': fee,
            'fee_asset': fee_asset
        }
    except KeyError as e:
        logging.error(f"Error processing {tx_type} transaction: Missing key {e}. Transaction data: {tx}")
        return None
    except Exception as e:
        logging.error(f"Error processing {tx_type} transaction: {e}. Transaction data: {tx}")
        return None

def process_dydxv4_positions(wallet: Dict[str, str], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Process dYdX v4 position data for both spot and perpetual futures.

    Args:
        wallet (Dict[str, str]): Dictionary containing wallet information.
        start_date (datetime): Start date for filtering positions.
        end_date (datetime): End date for filtering positions.

    Returns:
        List[Dict[str, Any]]: List of processed positions.
    """
    positions = []
    assets = fetch_dydxv4_user_assets(wallet['address'])
    perp_positions = fetch_dydxv4_perpetual_positions(wallet['address'])
    address_info = fetch_dydxv4_address_info(wallet['address'])
    
    # Extract total equity from the first subaccount
    total_equity = float(address_info['subaccounts'][0]['equity'])
    
    # Calculate total notional for open positions
    total_notional = 0
    open_positions = []
    for position in perp_positions.get('positions', []):
        if position['status'] == 'OPEN':
            processed_position = create_position(wallet, position, 'perps')
            open_positions.append(processed_position)
            total_notional += processed_position['notional']
    
    # Distribute equity pro rata across open positions
    for position in open_positions:
        position_equity = (position['notional'] / total_notional) * total_equity
        position['equity'] = position_equity
        positions.append(position)

    # Include closed positions within the date range
    for position in perp_positions.get('positions', []):
        if position['status'] == 'CLOSED':
            closed_at = datetime.fromisoformat(position['closedAt'].rstrip('Z')).replace(tzinfo=timezone.utc)
            if start_date <= closed_at <= end_date:
                processed_position = create_position(wallet, position, 'perps')
                positions.append(processed_position)

    # Check for USDC spot balance if no open perpetual positions
    if not open_positions:
        for asset in assets.get('positions', []):
            if asset['symbol'] == 'USDC':
                usdc_amount = float(asset['size'])
                if usdc_amount > 0:
                    cash_position = create_position(wallet, asset, 'cash')
                    cash_position['notional'] = np.nan  # Set notional value to 0 for cash
                    positions.append(cash_position)

    return positions

def process_dydxv4_transactions(wallet: Dict[str, str], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Process dYdX v4 transaction data including fills, rewards, and transfers.

    Args:
        wallet (Dict[str, str]): Dictionary containing wallet information.
        start_date (datetime): Start date for fetching transactions.
        end_date (datetime): End date for fetching transactions.

    Returns:
        List[Dict[str, Any]]: Processed transactions.
    """
    transactions = []

    # Fetch and process fills
    fills = fetch_dydxv4_user_fills_with_start_date(wallet['address'], start_date=start_date, end_date=end_date)
    for fill in fills:
        transaction = create_transaction(wallet, fill, 'fill')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process fill: {fill}")

    # Fetch and process rewards
    rewards = fetch_dydxv4_user_rewards_with_start_date(wallet['address'], start_date=start_date, end_date=end_date)
    for reward in rewards:
        transaction = create_transaction(wallet, reward, 'reward')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process reward: {reward}")

    # Fetch and process transfers
    transfers = fetch_dydxv4_user_transfers_with_date_range(wallet['address'], start_date=start_date, end_date=end_date)
    for transfer in transfers:
        transaction = create_transaction(wallet, transfer, 'transfer')
        if transaction:
            transactions.append(transaction)
        else:
            logging.warning(f"Failed to process transfer: {transfer}")

    logging.info(f"Total processed transactions: {len(transactions)}")
    return transactions

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'dydx_wallet', 'address': 'dydx1vwu7mpdzu9kcljtxfkv8ehm8zdckm6d7ccppm9', 'type': 'dydx', 'strategy': 'trading'}
    
    start_date = datetime(2024, 10, 14, tzinfo=timezone.utc)
    end_date = datetime(2024, 10, 15, tzinfo=timezone.utc)

    try:
        positions = process_dydxv4_positions(wallet, start_date, end_date)
        transactions = process_dydxv4_transactions(wallet, start_date, end_date)

        logging.info(f"Processed dYdX v4 Positions: {positions}")
        logging.info(f"Processed dYdX v4 Transactions: {transactions}")

    except Exception as e:
        logging.error(f"Error processing dYdX v4 data: {e}")

    for x in positions:
        print(x)
        print('-'*100)