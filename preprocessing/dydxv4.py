import logging
import requests
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)

def fetch_dydxv4_address_info(address: str) -> Dict[str, Any]:
    """
    Fetch dydx v4 account info for Ethereum address from dydx v4 indexer API.
    This includes current positions and other information.

    Args:
        address (str): The address to fetch information for.

    Returns:
        dict: The JSON response containing the information.
    """
    url = f'https://indexer.dydx.trade/v4/addresses/{address}'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

def create_position(wallet: Dict[str, str], market: str, position_type: str, symbol: str, amount: float, price: float) -> Dict[str, Any]:
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
        'position_id': f'dydxv4-{market}-{position_type}',
        'chain': 'dydxv4',
        'protocol_id': 'dydxv4',
        'type': position_type,
        'symbol': symbol,
        'amount': amount,
        'price': price
    }

def process_dydxv4_data(dydxv4_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process dydxv4 data to extract and structure relevant information.

    Args:
        dydxv4_data (dict): Data fetched from the dydxv4 API.
        wallet (dict): Dictionary containing wallet information (address, type, strategy).

    Returns:
        list: Processed data with wallet information included.
    """
    data = []

    for subaccount in dydxv4_data.get('subaccounts', []):
        subaccount_number = subaccount.get('subaccountNumber', 'unknown')
        total_equity = float(subaccount.get('equity', 0))
        open_perpetual_positions = subaccount.get('openPerpetualPositions', {})
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

                position = create_position(wallet, market, f'{subaccount_number}-perp', market, amount, price)
                proceeds_or_cost = create_position(wallet, market, f'{subaccount_number}-cost', 'USDC', -amount, 1)
                funding = create_position(wallet, market, f'{subaccount_number}-funding', 'USDC', float(position_details['netFunding']), 1)
                collateral = create_position(wallet, market, f'{subaccount_number}-collateral', 'USDC', collateral_attribution * total_equity, 1)

                data.extend([position, proceeds_or_cost, funding, collateral])
        else:
            data.append(create_position(wallet, 'cash', 'hodl', 'USDC', total_equity, 1))

    return data

# Example usage
if __name__ == "__main__":
    wallet_list = [
        {'id': 'XXXX', 'address': 'dydx18vgsfaarveyg7xy585657ak8a9jvut9z8yuzmv', 'type': 'dydxv4', 'strategy': 'Quality'},
        {'id': 'YYYY', 'address': '0x03c053470a6cfac6ae4e44f2dfb971549509fe0f', 'type': 'EVM', 'strategy': 'Quality'}
    ]

    all_data = []

    for wallet in wallet_list:
        if wallet['type'] == 'dydxv4':
            try:
                dydxv4_data = fetch_dydxv4_address_info(wallet['address'])
                processed_data = process_dydxv4_data(dydxv4_data, wallet)
                all_data.extend(processed_data)
            except Exception as e:
                logging.error(f"Error processing data for wallet {wallet['address']}: {e}")

    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(all_data)
    print(df)
