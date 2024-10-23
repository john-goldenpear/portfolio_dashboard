import logging
from typing import Dict, Any, List, Union
import numpy as np

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_manual_position(wallet: Dict[str, Any], chain: str, protocol: str, position_type: str, symbol: str, amount: float) -> Dict[str, Union[str, float]]:
    """
    Create a manual position dictionary with the specified keys.

    Args:
        wallet (Dict[str, Any]): The wallet data dictionary.
        chain (str): The blockchain chain key.
        protocol (str): The protocol key.
        position_type (str): The type of position (e.g., 'LOCK').
        symbol (str): The asset symbol.
        amount (float): The amount of the asset.

    Returns:
        Dict[str, Union[str, float]]: The structured position data.
    """
    # Assume price is not available for manual positions, set to NaN

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet.get('strategy', 'manual'),
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol,
        'position_type': position_type,
        'position': None,
        'symbol': symbol,
        'base_asset': None,
        'asset_type': None,
        'sector': None,
        'amount': float(amount),
        'price': np.nan,
        'value': np.nan,
        'equity': np.nan,
        'notional': np.nan,
        'cost_basis': np.nan,
        'unrealized_gain': np.nan,
        'realized_gain': np.nan,
        'funding': np.nan,
        'rewards': np.nan,
        'rewards_asset': None,
        'income': np.nan,
        'income_asset': np.nan,
        'interest_exp': np.nan,
        'interest_asset': None,
        'net_income_usd': np.nan,
        'fees': np.nan,
        'fee_asset': np.nan,
        'fees_usd': np.nan
    }

def process_manual_positions(manual_positions: List[Dict[str, Any]], wallet: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process the manual positions from the list.

    Args:
        manual_positions (List[Dict[str, Any]]): The list of manual positions.
        wallet (Dict[str, Any]): The wallet data dictionary.

    Returns:
        List[Dict[str, Any]]: The processed manual positions.
    """
    processed_positions = []

    for position in manual_positions:
        logging.debug(f"Processing manual position: {position['symbol']}")
        chain = position['chain']
        protocol = position['protocol']
        symbol = position['symbol']
        amount = float(position['amount'])
        position_type = position['position_type']

        manual_position = create_manual_position(
            wallet,
            chain,
            protocol,
            position_type,
            symbol,
            amount
        )
        processed_positions.append(manual_position)

    logging.info(f"Total processed manual positions: {len(processed_positions)}")
    return processed_positions

# Example code to test the manual position processing
if __name__ == "__main__":
    # Example wallet information
    wallet_info = {
        'id': 'manual_wallet_id',
        'address': 'manual_wallet_address',
        'type': 'MANUAL',
        'strategy': 'manual_strategy'
    }

    # Example manual positions
    manual_positions = [
        {
            'chain': 'ethereum',
            'protocol': 'manual_protocol',
            'symbol': 'ETH',
            'amount': 10.0,
            'position_type': 'LOCK'
        },
        {
            'chain': 'bitcoin',
            'protocol': 'manual_protocol',
            'symbol': 'BTC',
            'amount': 2.0,
            'position_type': 'LOCK'
        }
    ]

    # Process the manual positions
    processed_positions = process_manual_positions(manual_positions, wallet_info)

    # Print the processed positions
    for position in processed_positions:
        print(position)
