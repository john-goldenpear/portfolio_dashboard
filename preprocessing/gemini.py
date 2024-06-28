import logging
from typing import List, Dict, Any
import pandas as pd

from apis.gemini import fetch_gemini_user_perps_balances, fetch_gemini_user_spot_balances

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], data_type: str, currency: str, amount: float, price: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (dict): Wallet information.
        data_type (str): Type of data being processed ('spot' or 'perps').
        currency (str): Currency symbol.
        amount (float): Amount of the asset.
        price (float): Price of the asset.

    Returns:
        dict: Position dictionary.
    """
    return {
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'position_id': f'gemini-{data_type}-{currency}',
        'chain': 'gemini',
        'protocol_id': 'gemini',
        'type': ('hodl' if data_type == 'spot' else 'perps'),
        'symbol': currency,
        'amount': amount,
        'price': price
    }

def process_gemini_data(data: List[Dict[str, Any]], wallet: Dict[str, str], data_type: str) -> List[Dict[str, Any]]:
    """
    Process data fetched from the Gemini API.

    Args:
        data (list): List of positions in Gemini fetched from Gemini API.
        wallet (dict): Dictionary containing wallet information (address, type, strategy).
        data_type (str): Type of data being processed ('spot' or 'perps').

    Returns:
        list: Processed token data with wallet information included.
    """
    processed_data = []
    for position in data:
        try:
            amount = float(position['amount'])
            amount_notional = float(position['amountNotional'])
            price = amount_notional / amount

            processed_position = create_position(
                wallet=wallet,
                data_type=data_type,
                currency=position['currency'],
                amount=amount,
                price=price
            )
            processed_data.append(processed_position)
        except KeyError as e:
            logging.error(f"Missing expected key in position data: {e}")
        except ValueError as e:
            logging.error(f"Error converting data to float: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
    return processed_data

# Example usage
if __name__ == "__main__":
    wallet_list = [
        {'id': 'XXXX', 'address': '0x2af2a6f692231e394b48b701afce9f5cc2081ab4', 'type': 'gemini', 'strategy': 'Quality'},
        {'id': 'YYYY', 'address': '0x03c053470a6cfac6ae4e44f2dfb971549509fe0f', 'type': 'EVM', 'strategy': 'Quality'}
    ]

    all_data = []

    for wallet in wallet_list:
        if wallet['type'] == 'gemini':
            try:
                spot_data = fetch_gemini_user_spot_balances()
                perps_data = fetch_gemini_user_perps_balances()
            except Exception as e:
                logging.error(f"Error fetching data for wallet {wallet['address']}: {e}")
                continue

            processed_spot_data = process_gemini_data(spot_data, wallet, 'spot')
            processed_perps_data = process_gemini_data(perps_data, wallet, 'perps')
            gemini_data = processed_spot_data + processed_perps_data
            all_data.extend(gemini_data)

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    print(df)