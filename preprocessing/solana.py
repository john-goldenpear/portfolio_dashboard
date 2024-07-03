import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)

# Assuming SOLANA_TOKENS is imported or defined elsewhere in the module
# SOLANA_TOKENS = [{'address': 'some_address', 'symbol': 'some_symbol'}, ...]

def create_position(wallet: Dict[str, str], position_id: str, symbol: str, amount: float, price: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (dict): Wallet information.
        position_id (str): Position ID.
        chain (str): Blockchain chain.
        protocol_id (str): Protocol ID.
        position_type (str): Type of position (e.g., 'wallet', 'supply', 'borrow', 'reward').
        symbol (str): Symbol of the asset.
        amount (float): Amount of the asset.
        price (float): Price of the asset.

    Returns:
        dict: Position dictionary.
    """
    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': position_id,
        'position_id': f"{wallet['id']}-sol-wallet-hodl-{symbol}",
        'chain': 'sol',
        'protocol': 'wallet',
        'type': 'hodl',
        'symbol': symbol,
        'amount': amount,
        'price': price
    }

def get_symbol_from_address(token_address: str, token_list: List[Dict[str, str]]) -> str:
    """
    Get the token symbol from the token address using a list of tokens.

    Args:
        token_address (str): The token address.
        token_list (list): The list of token dictionaries with 'address' and 'symbol' keys.

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
        wallet (dict): Wallet information.
        balance_data (dict): Raw balance data from the Solana API.

    Returns:
        list: Processed balance data with wallet information included.
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
        wallet (dict): Wallet information.
        token_positions_data (list): Raw token accounts data from the Solana API.
        token_list (list): List of token dictionaries with 'address' and 'symbol' keys.

    Returns:
        list: Processed token data with wallet information included.
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