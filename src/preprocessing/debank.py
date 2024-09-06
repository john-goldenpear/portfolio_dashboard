import logging
from typing import List, Dict, Any

from src.apis.debank import fetch_debank_user_balances_tokens, fetch_debank_user_balances_protocol

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], position_id: str, chain: str, protocol_id: str, position_type: str, symbol: str, amount: float, price: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        position_id (str): Position ID.
        chain (str): Blockchain chain.
        protocol_id (str): Protocol ID.
        position_type (str): Type of position (e.g., 'wallet', 'supply', 'borrow', 'reward').
        symbol (str): Symbol of the asset.
        amount (float): Amount of the asset.
        price (float): Price of the asset.

    Returns:
        Dict[str, Any]: Position dictionary.
    """ 
    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': position_id,
        'position_id': f"{wallet['id']}-{chain}-{protocol_id}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol_id,
        'type': position_type,
        'symbol': symbol,
        'amount': amount,
        'price': price,
    }

def process_evm_token_data(token_data: List[Dict[str, Any]], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process EVM token data fetched from the Debank API.

    Args:
        token_data (List[Dict[str, Any]]): List of token data dictionaries fetched from Debank.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).

    Returns:
        List[Dict[str, Any]]: Processed token data with wallet information included.
    """
    data = []
    for item in token_data:
        try:
            if not item.get('is_verified', False) or not item.get('is_wallet', False):
                continue
            
            position = create_position(
                wallet=wallet,
                position_id=item.get('id', ''),
                chain=item.get('chain', ''),
                protocol_id='wallet',
                position_type='hodl',
                symbol=item.get('symbol', ''),
                amount=item.get('amount', 0),
                price=item.get('price', 0)
            )
            data.append(position)
        except KeyError as e:
            logging.error(f"Key error: {e} in token data {item}")
        except Exception as e:
            logging.error(f"Unexpected error: {e} in token data {item}")
    return data

def process_evm_protocol_data(protocol_data: List[Dict[str, Any]], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process EVM protocol data fetched from the Debank API.

    Args:
        protocol_data (List[Dict[str, Any]]): List of protocol data dictionaries fetched from Debank.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).

    Returns:
        List[Dict[str, Any]]: Processed protocol data with wallet information included.
    """
    data = []
    for item in protocol_data:
        try:
            pool_id = item['portfolio_item_list'][0]['pool']['id']
            chain = item['chain']
            protocol = item['name']
            detail = item['portfolio_item_list'][0]['detail']
            
            if 'supply_token_list' in detail:
                for supply_token in detail['supply_token_list']:
                    position = create_position(
                        wallet=wallet,
                        position_id=pool_id,
                        chain=chain,
                        protocol_id=protocol,
                        position_type='supply',
                        symbol=supply_token.get('symbol', ''),
                        amount=supply_token.get('amount', 0),
                        price=supply_token.get('price', 0)
                    )
                    data.append(position)

            if 'borrow_token_list' in detail:
                for borrow_token in detail['borrow_token_list']:
                    position = create_position(
                        wallet=wallet,
                        position_id=pool_id,
                        chain=chain,
                        protocol_id=protocol,
                        position_type='borrow',
                        symbol=borrow_token.get('symbol', ''),
                        amount=borrow_token.get('amount', 0) * -1,
                        price=borrow_token.get('price', 0)
                    )
                    data.append(position)

            if 'reward_token_list' in detail:
                for reward_token in detail['reward_token_list']:
                    position = create_position(
                        wallet=wallet,
                        position_id=pool_id,
                        chain=chain,
                        protocol_id=protocol,
                        position_type='reward',
                        symbol=reward_token.get('symbol', ''),
                        amount=reward_token.get('amount', 0),
                        price=reward_token.get('price', 0)
                    )
                    data.append(position)
        except KeyError as e:
            logging.error(f"Key error: {e} in protocol data {item}")
        except Exception as e:
            logging.error(f"Unexpected error: {e} in protocol data {item}")
    return data

# Example usage
if __name__ == "__main__":
    wallet_list = [
        {'id': 'XXXX', 'address': '0x2af2a6f692231e394b48b701afce9f5cc2081ab4', 'type': 'EVM', 'strategy': 'Quality'},
        {'id': 'YYYY', 'address': '0x03c053470a6cfac6ae4e44f2dfb971549509fe0f', 'type': 'EVM', 'strategy': 'Quality'}
    ]

    all_data = []

    for wallet in wallet_list:
        if wallet['type'] == 'EVM':
            try:
                token_data = fetch_debank_user_balances_tokens(wallet['address'])
                protocol_data = fetch_debank_user_balances_protocol(wallet['address'])
                processed_token_data = process_evm_token_data(token_data, wallet)
                processed_protocol_data = process_evm_protocol_data(protocol_data, wallet)
                evm_data = processed_token_data + processed_protocol_data
                all_data.extend(evm_data)
            except Exception as e:
                logging.error(f"Error processing data for wallet {wallet['address']}: {e}")

    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(all_data)
    logging.info(df)