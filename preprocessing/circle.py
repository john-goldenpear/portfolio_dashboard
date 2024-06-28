import logging
from typing import List, Dict, Any
from goldenpear_tools.apis_wallet.circle import fetch_circle_user_balance

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], amount: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (dict): Wallet information.
        amount (float): Amount of the asset.

    Returns:
        dict: Position dictionary.
    """
    return {
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'position_id': f'circle-cash',
        'chain': 'circle',
        'protocol_id': 'circle',
        'type': 'hodl',
        'symbol': 'USDC',
        'amount': amount,
        'price': 1.0  # Price is 1.0 as it represents cash
    }

def process_circle_data(circle_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process Circle data to extract and structure relevant information.

    Args:
        circle_data (dict): Data fetched from the Circle API.
        wallet (dict): Dictionary containing wallet information (address, type, strategy).

    Returns:
        list: Processed data with wallet information included.
    """
    data = []

    available_balance = circle_data.get('data', {}).get('available', [])
    if available_balance:
        balance = available_balance[0]  # There will only be one position
        amount = float(balance['amount'])
        position = create_position(wallet, amount)
        data.append(position)

    return data

# Example usage
if __name__ == "__main__":
    from goldenpear_tools.apis_wallet.circle import fetch_circle_user_balance

    wallet_list = [
        {'id': 'XXXX', 'address': 'circle-wallet-1', 'type': 'circle', 'strategy': 'Quality'},
        {'id': 'YYYY', 'address': 'circle-wallet-2', 'type': 'circle', 'strategy': 'Growth'}
    ]

    all_data = []

    for wallet in wallet_list:
        if wallet['type'] == 'circle':
            try:
                circle_data = fetch_circle_user_balance()
                processed_data = process_circle_data(circle_data, wallet)
                all_data.extend(processed_data)
            except Exception as e:
                logging.error(f"Error processing data for wallet {wallet['address']}: {e}")

    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(all_data)
    print(df)




