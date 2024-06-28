import logging
from typing import Dict, Any, List
from goldenpear_tools.apis_wallet.dydxv3 import dydxClient

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], position_type: str, symbol: str, amount: float, price: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (dict): Wallet information.
        market (str): Market symbol.
        position_type (str): Type of position (e.g., 'perps', 'income').
        symbol (str): Symbol of the asset.
        amount (float): Amount of the asset.
        price (float): Price of the asset.

    Returns:
        dict: Position dictionary.
    """
    return {
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'position_id': f'dydxv3-{symbol}-{position_type}',
        'chain': 'starkware',
        'protocol_id': 'dydxv3',
        'type': 'perps',
        'symbol': symbol,
        'amount': amount,
        'price': price
    }

def process_dydxv3_data(dydxv3_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process dydxv3 data to extract and structure relevant information.

    Args:
        dydxv3_data (dict): Data fetched from the dydxv3 API.
        wallet (dict): Dictionary containing wallet information (address, type, strategy).

    Returns:
        list: Processed data with wallet information included.
    """
    data = []

    total_equity = float(dydxv3_data['account'].get('equity', 0))
    open_perpetual_positions = dydxv3_data['account'].get('openPositions', {})
    total_account_position_value = 0.0

    if open_perpetual_positions:
        positions = []
        for position_details in open_perpetual_positions.values():
            amount = float(position_details['size'])
            entry_price = float(position_details['entryPrice'])
            unrealized_pnl = float(position_details['unrealizedPnl'])
            price = entry_price + (unrealized_pnl / amount)
            position_value = amount * price

            positions.append((position_details, amount, price, position_value))
            total_account_position_value += position_value

        for position_details, amount, price, position_value in positions:
            collateral_attribution = position_value / total_account_position_value
            market = position_details['market']
            symbol = market.split('-')[0]  # Extract symbol from market (e.g., 'BTC-USD' -> 'BTC')

            position = create_position(wallet, 'perp', symbol, amount, price)
            proceeds_or_cost = create_position(wallet, 'cost', 'USDC', -amount * entry_price, 1)
            funding = create_position(wallet, 'funding', 'USDC', float(position_details['netFunding']), 1)
            collateral = create_position(wallet, 'collateral', 'USDC', collateral_attribution * total_equity, 1)

            data.extend([position, proceeds_or_cost, funding, collateral])
    else:
        data.append(create_position(wallet, 'cash', 'hodl', 'USDC', total_equity, 1))

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