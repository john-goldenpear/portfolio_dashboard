import logging
from typing import Dict, Any, List
from apis.blockcypher import fetch_blockcypher_user_balance

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], amount: float, symbol: str) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (dict): Wallet information.
        amount (float): Amount of the asset.
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        dict: Position dictionary.
    """
    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'position_id': f'{symbol}',
        'chain': f'{symbol}',
        'protocol': 'wallet',
        'type': 'hodl',
        'symbol': f'{symbol.upper()}',
        'amount': amount,
        'price': None  # Price is unknown
    }

def process_blockcypher_data(blockcypher_data: Dict[str, Any], wallet: Dict[str, str], symbol: str) -> List[Dict[str, Any]]:
    """
    Process BlockCypher data for a single wallet.

    Args:
        blockcypher_data (dict): Raw data pulled from BlockCypher API using fetch_blockcypher_user_balance in goldenpear_tools.
        wallet (dict): Dictionary containing wallet information (address, type, strategy).
        symbol (str): The type of cryptocurrency ('doge' or 'btc').

    Returns:
        list: Processed wallet data.
    """
    all_data = []
    try:
        balance = float(blockcypher_data.get('balance', 0)) / 1e8  # Convert from satoshis to BTC/DOGE
        position = create_position(wallet, balance, symbol)
        all_data.append(position)

        logging.info(f"Processed wallet {wallet['address']} with balance {balance}")

    except Exception as e:
        logging.error(f"Error processing data for wallet {wallet['address']}: {e}")

    return all_data

# Example usage
if __name__ == "__main__":
    wallet = {'address': 'ADNbM5fBujCRBW1vqezNeAWmnsLp19ki3n', 'type': 'doge', 'strategy': 'hold'}
    blockcypher_data = fetch_blockcypher_user_balance(wallet['address'], 'doge')
    doge_data = process_blockcypher_data(blockcypher_data, wallet, 'doge')
    print(doge_data)
    
    wallet = {'address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'type': 'btc', 'strategy': 'hold'}
    blockcypher_data = fetch_blockcypher_user_balance(wallet['address'], 'btc')
    btc_data = process_blockcypher_data(blockcypher_data, wallet, 'btc')
    print(btc_data)