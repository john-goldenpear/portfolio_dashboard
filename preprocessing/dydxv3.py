from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
from apis.dydxv3 import dydxClient

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], position_type: str, symbol: str, amount: float, price: float, equity: float, cost_basis: float, unrealized_pnl: float, realized_pnl: float, income_usd: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (dict): Wallet information.
        market (str): Market symbol.
        position_type (str): Type of position (e.g., 'perps', 'funding', 'collateral').
        symbol (str): Symbol of the asset.
        amount (float): Amount of the asset.
        price (float): Price of the asset.
        equity (float):
        cost_basis (float):
        income_usd (float):
        unrealized_pnl (float):
        realized_pnl (float):

    Returns:
        dict: Position dictionary.
    """
    chain = 'starkware'
    protocol = 'dydxV3'

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': None,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol,
        'type': position_type,
        'symbol': symbol,
        'amount': amount,
        'price': price,
        'equity': equity,
        'cost_basis': cost_basis,
        'income_usd': income_usd,
        'unrealized_gain': unrealized_pnl,
        'realized_gain': realized_pnl,
    }

def process_dydxv3_data(dydxv3_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process dydxv3 data to extract and structure relevant information.
    """
    
    data = []

    total_equity = float(dydxv3_data['account'].get('equity', 0))
    open_perpetual_positions = dydxv3_data['account'].get('openPositions', {})
    closed_positions = dydxv3_data.get('positions', [])
    total_account_position_value = 0.0

    # Process open positions
    if open_perpetual_positions:
        positions = []
        for position_details in open_perpetual_positions.values():
            amount = float(position_details['size'])
            entry_price = float(position_details['entryPrice'])
            unrealized_pnl = float(position_details['unrealizedPnl'])
            price = entry_price + (unrealized_pnl / amount) if amount != 0 else 0
            cost_basis = entry_price * amount
            position_value = amount * price
            income_usd = float(position_details['netFunding'])
            symbol = position_details['market'].split('-')[0]  # Extract symbol from market (e.g., 'BTC-USD' -> 'BTC')
            realized_pnl = float(position_details['realizedPnl']) - float(position_details['netFunding'])

            positions.append((position_details, amount, price, symbol, position_value, cost_basis, unrealized_pnl, realized_pnl, income_usd))
            total_account_position_value += abs(position_value)

        for position_details, amount, price, symbol, position_value, cost_basis, unrealized_pnl, realized_pnl, income_usd in positions:
            collateral_attribution = abs(position_value) / total_account_position_value if total_account_position_value != 0 else 0
            equity = collateral_attribution * total_equity

            position = create_position(wallet, 'perps', symbol, amount, price, equity, cost_basis, unrealized_pnl, realized_pnl, income_usd)
            
            data.append(position)

    else:
        data.append(create_position(wallet, 'cash', 'USDC', total_equity, 1, total_equity, 0, 0, 0, 0))

    # Process closed positions within the last 24 hours
    now = datetime.utcnow()
    for position in closed_positions:
        closed_at = datetime.strptime(position['closedAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if now - closed_at < timedelta(hours=24):
            amount = 0.0
            entry_price = 0.0
            unrealized_pnl = 0.0
            price = 0.0
            cost_basis = 0.0
            position_value = 0.0
            income_usd = float(position['netFunding'])
            symbol = position['market'].split('-')[0]  # Extract symbol from market (e.g., 'BTC-USD' -> 'BTC')
            realized_pnl = float(position['realizedPnl']) - float(position['netFunding'])
            equity = 0.0  # Closed positions have no equity

            closed_position = create_position(wallet, 'perps', symbol, amount, price, equity, cost_basis, unrealized_pnl, realized_pnl, income_usd)
            data.append(closed_position)

    return data

if __name__ == "__main__":
    from config import DYDXV3_API_KEY_2, DYDXV3_API_SECRET_2, DYDXV3_API_PASSPHRASE_2
    ETHEREUM_ADDRESS = 'TEST ADDRESS'
    
    # Initialize the client
    client = dydxClient(
        api_key=DYDXV3_API_KEY_2,
        api_secret=DYDXV3_API_SECRET_2,
        api_passphrase=DYDXV3_API_PASSPHRASE_2,
        ethereum_address=ETHEREUM_ADDRESS
    )

    # Fetch dYdX account information
    account_info = client.get_account_info()
    print('Account Information:', account_info)

    # Process the dYdX account information
    wallet_info = {'address': ETHEREUM_ADDRESS, 'type': 'dydx', 'strategy': 'hold'}
    processed_data = process_dydxv3_data(account_info, wallet_info)

    # Print the processed data
    for entry in processed_data:
        print(entry)