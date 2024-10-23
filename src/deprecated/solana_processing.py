import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], position_id: str, symbol: str, amount: float, price: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        position_id (str): Position ID.
        symbol (str): Symbol of the asset.
        amount (float): Amount of the asset.
        price (float): Price of the asset.

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    chain = 'sol'
    protocol = 'wallet'
    position_type = 'hodl'

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': position_id,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol,
        'type': position_type,
        'symbol': symbol,
        'amount': amount,
        'price': price,
    }

def get_symbol_from_address(token_address: str, token_list: List[Dict[str, str]]) -> str:
    """
    Get the token symbol from the token address using a list of tokens.

    Args:
        token_address (str): The token address.
        token_list (List[Dict[str, str]]): The list of token dictionaries with 'address' and 'symbol' keys.

    Returns:
        str: The token symbol or None if not found.
    """
    for token in token_list:
        if token['address'] == token_address:
            return token['symbol']
    return None

def process_solana_data(wallet: Dict[str, str], balance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process Solana native balance data for a single wallet.

    Args:
        wallet (Dict[str, str]): Wallet information.
        balance_data (Dict[str, Any]): Raw balance data from the Solana API.

    Returns:
        List[Dict[str, Any]]: Processed balance data with wallet information included.
    """
    all_data = []
    try:
        balance = float(balance_data['result']['value']) / 1e9  # Convert lamports to SOL
        position = create_position(
            wallet=wallet,
            position_id='SOL',
            symbol='SOL',
            amount=balance,
            price=None  # Price to be handled outside this function
        )
        all_data.append(position)
        logging.info(f"Processed SOL balance for wallet {wallet['address']} with balance {balance}")

    except Exception as e:
        logging.error(f"Error processing SOL balance data for wallet {wallet['address']}: {e}")

    return all_data

def process_solana_token_data(wallet: Dict[str, str], token_positions_data: List[Dict[str, Any]], token_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Process Solana token accounts data for a single wallet.

    Args:
        wallet (Dict[str, str]): Wallet information.
        token_positions_data (List[Dict[str, Any]]): Raw token accounts data from the Solana API.
        token_list (List[Dict[str, str]]): List of token dictionaries with 'address' and 'symbol' keys.

    Returns:
        List[Dict[str, Any]]: Processed token data with wallet information included.
    """
    all_data = []
    try:
        for account in token_positions_data:
            mint_address = account['account']['data']['parsed']['info']['mint']
            amount = float(account['account']['data']['parsed']['info']['tokenAmount']['uiAmount'])
            symbol = get_symbol_from_address(mint_address, token_list)

            if symbol:  # Only process if symbol is found in token_list
                position = create_position(
                    wallet=wallet,
                    position_id=mint_address,
                    symbol=symbol,
                    amount=amount,
                    price=None  # Price to be handled outside this function
                )
                all_data.append(position)

        logging.info(f"Processed token accounts for wallet {wallet['address']}")

    except KeyError as e:
        logging.error(f"Key error: {e} in token account data")
    except Exception as e:
        logging.error(f"Unexpected error: {e} in processing token account data")

    return all_data

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'XXXX', 'address': 'AVzP2GeRmqGphJsMxWoqjpUifPpCret7LqWhD8NWQK49', 'type': 'sol', 'strategy': 'Quality'}
    try:
        from deprecated.solana_api import fetch_solana_user_balance, fetch_solana_user_token_balances
        from config import SOLANA_TOKENS
        
        # Fetch and process SOL balance
        balance_data = fetch_solana_user_balance(wallet['address'])
        sol_data = process_solana_data(wallet, balance_data)
        logging.info(f"Processed SOL Data: {sol_data}")

        # Fetch and process SOL token accounts
        token_positions_data = fetch_solana_user_token_balances(wallet['address'])
        token_data = process_solana_token_data(wallet, token_positions_data, SOLANA_TOKENS)
        logging.info(f"Processed SOL Token Data: {token_data}")

    except Exception as e:
        logging.error(f"Error processing data for wallet {wallet['address']}: {e}")