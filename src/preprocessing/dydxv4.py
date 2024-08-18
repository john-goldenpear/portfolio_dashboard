import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.apis.dydxv4 import fetch_dydxv4_address_info, fetch_dydxv4_perpetual_positions

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], subaccount: int, position_type: str, symbol: str, amount: float, price: float, equity: float, cost_basis: float, unrealized_pnl: float, realized_pnl: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        subaccount (int): Subaccount number.
        position_type (str): Type of position (e.g., 'perps', 'funding', 'collateral').
        symbol (str): Symbol of the asset.
        amount (float): Amount of the asset.
        price (float): Price of the asset.
        equity (float): Equity value of the asset.
        cost_basis (float): Cost basis of the asset.
        unrealized_pnl (float): Unrealized P&L of the asset.
        realized_pnl (float): Realized P&L of the asset.

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    chain = 'starkware'
    protocol = 'dydxV4'

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': None,
        'position_id': f"{wallet['id']}-{subaccount}-{chain}-{protocol}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol,
        'type': position_type,
        'symbol': symbol,
        'amount': amount,
        'price': price,
        'equity': equity,
        'cost_basis': cost_basis,
        'unrealized_gain': unrealized_pnl,
        'realized_gain': realized_pnl
    }

def process_dydxv4_data(dydxv4_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process dydxv4 data to extract and structure relevant information.

    Args:
        dydxv4_data (Dict[str, Any]): Data from the dydxv4 API.
        wallet (Dict[str, str]): Dictionary containing wallet information.

    Returns:
        List[Dict[str, Any]]: Processed data with wallet information included.
    """
    data = []

    subaccounts = dydxv4_data.get('subaccounts', [])
    now = datetime.utcnow()

    for subaccount in subaccounts:
        subaccount_number = subaccount['subaccountNumber']
        total_equity = float(subaccount.get('equity', 0))
        positions_data = fetch_dydxv4_perpetual_positions(wallet['address'], subaccount_number=subaccount_number)

        total_account_position_value = 0.0
        open_positions = []
        for position in positions_data.get('positions', []):
            status = position['status']
            closed_at = position.get('closedAt')
            include_position = False

            if status == 'OPEN':
                include_position = True
            elif status == 'CLOSED' and closed_at:
                closed_at_datetime = datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%S.%fZ')
                if now - closed_at_datetime < timedelta(hours=24):
                    include_position = True

            if include_position:
                amount = float(position['size'])
                entry_price = float(position['entryPrice'])
                unrealized_pnl = float(position['unrealizedPnl'])
                price = entry_price + (unrealized_pnl / amount) if amount != 0 else 0
                cost_basis = entry_price * amount
                realized_pnl = float(position['realizedPnl']) - float(position['netFunding'])
                symbol = position['market'].split('-')[0]  # Extract symbol from market (e.g., 'BTC-USD' -> 'BTC')
                position_value = amount * price

                if status == 'OPEN':
                    open_positions.append((position, amount, price, symbol, position_value, cost_basis, unrealized_pnl, realized_pnl))
                    total_account_position_value += abs(position_value)
                else:
                    position_data = create_position(wallet, subaccount_number, 'perps', symbol, amount, price, 0.0, cost_basis, unrealized_pnl, realized_pnl)
                    data.append(position_data)

        for position, amount, price, symbol, position_value, cost_basis, unrealized_pnl, realized_pnl in open_positions:
            collateral_attribution = abs(position_value) / total_account_position_value if total_account_position_value != 0 else 0
            equity = collateral_attribution * total_equity
            position_data = create_position(wallet, subaccount_number, 'perps', symbol, amount, price, equity, cost_basis, unrealized_pnl, realized_pnl)
            data.append(position_data)

    return data

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'XXXX', 'address': 'dydx1apl362xyztk6kg6kujnlashx8zsjlkcxnv4uud', 'type': 'dydx', 'strategy': 'hold'}
    try:
        # Fetch and process dydxv4 data
        dydxv4_data = fetch_dydxv4_address_info(wallet['address'])
        processed_data = process_dydxv4_data(dydxv4_data, wallet)
        logging.info(f"Processed Data: {processed_data}")

    except Exception as e:
        logging.error(f"Error processing data for wallet {wallet['address']}: {e}")