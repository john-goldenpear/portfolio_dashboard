import logging
from typing import Dict, Any, List, Union
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_position(wallet: Dict[str, Any], chain: str, protocol: str, position_type: str, symbol: str, amount: float, price: float, totalClosedPnl: float, totalOpenPnl: float, contract_id: str) -> Dict[str, Union[str, float]]:
    """
    Create a position dictionary with the specified keys.

    Args:
        wallet (Dict[str, Any]): The wallet data dictionary.
        chain (str): The blockchain chain key.
        protocol (str): The protocol key.
        position_type (str): The type of position (e.g., 'LENDING', 'REWARDS').
        symbol (str): The asset symbol.
        amount (float): The amount of the asset.
        price (float): The price of the asset.
        totalClosedPnl (float): The total closed PnL for the position.
        totalOpenPnl (float): The total open PnL for the position.
        contract_id (str): The contract ID for the asset.

    Returns:
        Dict[str, Union[str, float]]: The structured position data.
    """
    # Calculate value after adjusting amount
    value = amount * price

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': contract_id,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol,
        'position_type': position_type,
        'position': None,
        'symbol': symbol,
        'base_asset': None,
        'asset_type': None,
        'sector': None,
        'amount': amount,
        'price': price,
        'value': value,
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

def process_octav_portfolio(data: Dict[str, Any], wallet: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Preprocess the portfolio data to extract asset information by protocols.

    Args:
        data (Dict[str, Any]): The portfolio data dictionary.
        wallet (Dict[str, Any]): The wallet data dictionary.

    Returns:
        List[Dict[str, Any]]: The preprocessed data.
    """
    processed_data = []

    # Navigate to the assetByProtocols section
    try:
        asset_by_protocols = data['getPortfolio'][0]['assetByProtocols']
    except (KeyError, IndexError) as e:
        logging.error(f"Error accessing assetByProtocols: {e}")
        return processed_data

    # Iterate over each protocol
    for protocol_key, protocol_data in asset_by_protocols.items():
        logging.debug(f"Processing protocol: {protocol_key}")
        chains = protocol_data.get('chains', {})
        
        for chain_key, chain_data in chains.items():
            logging.debug(f"Processing chain: {chain_key}")
            protocol_positions = chain_data.get('protocolPositions', {})
            
            for position_type, position_data in protocol_positions.items():
                logging.debug(f"Processing position type: {position_type}")
                # Process direct assets
                assets = position_data.get('assets', [])
                for asset in assets:
                    logging.debug(f"Processing asset: {asset.get('symbol', 'unknown')}")
                    # Extract necessary information from each asset
                    chain = chain_key
                    protocol = protocol_key
                    symbol = asset.get('symbol', 'unknown')
                    price = float(asset.get('price', 0))
                    amount = float(asset.get('balance', 0))
                    contract_id = asset.get('uuid', 'unknown')

                    position = create_position(
                        wallet,
                        chain,
                        protocol,
                        position_type.lower(),
                        symbol.upper(),
                        amount,
                        price,
                        totalClosedPnl=0,  # Assuming no closed PnL data available
                        totalOpenPnl=float(position_data.get('totalOpenPnl', 0)),
                        contract_id=contract_id
                    )
                    processed_data.append(position)

                # Process nested protocol positions
                nested_positions = position_data.get('protocolPositions', [])
                for nested_position in nested_positions:
                    logging.debug(f"Processing nested position: {nested_position.get('name', 'unknown')}")
                    
                    # Define all asset types to process
                    asset_types = ['assets', 'dexAssets', 'borrowAssets', 'supplyAssets', 'rewardAssets']
                    
                    for asset_type in asset_types:
                        assets = nested_position.get(asset_type, [])
                        for asset in assets:
                            logging.debug(f"Processing {asset_type[:-1]} asset: {asset.get('symbol', 'unknown')}")
                            # Extract necessary information from each asset
                            chain = chain_key
                            protocol = protocol_key
                            symbol = asset.get('symbol', 'unknown')
                            price = float(asset.get('price', 0))
                            amount = float(asset.get('balance', 0))

                            # Adjust amount for borrowAssets to be negative
                            if asset_type == 'borrowAssets':
                                amount = -amount

                            contract_id = asset.get('uuid', 'unknown')

                            position = create_position(
                                wallet,
                                chain,
                                protocol,
                                position_type.lower(),
                                symbol.upper(),
                                amount,
                                price,
                                totalClosedPnl=0,  # Assuming no closed PnL data available
                                totalOpenPnl=float(nested_position.get('totalOpenPnl', 0)),
                                contract_id=contract_id
                            )
                            processed_data.append(position)

    logging.info(f"Total processed positions: {len(processed_data)}")
    return processed_data

def create_transaction(wallet: Dict[str, Any], chain: str, protocol: str, function_name: str, transaction_type: str,
                       hash_value: str, timestamp: str, fees: float, fees_fiat: float, symbol: str, balance: float,
                       price: float, value: float, from_address: str, to_address: str) -> Dict[str, Union[str, float]]:
    """
    Create a transaction dictionary with the specified keys.

    Args:
        wallet (Dict[str, Any]): The wallet data dictionary.
        chain (str): The blockchain chain key.
        protocol (str): The protocol key.
        function_name (str): The function name of the transaction.
        transaction_type (str): The type of transaction (e.g., 'DEPOSIT', 'WITHDRAW').
        hash_value (str): The transaction hash.
        timestamp (str): The transaction timestamp.
        fees (float): The transaction fees.
        fees_fiat (float): The transaction fees in fiat.
        symbol (str): The asset symbol.
        balance (float): The asset balance.
        price (float): The asset price.
        value (float): The asset value.
        from_address (str): The sender address.
        to_address (str): The receiver address.

    Returns:
        Dict[str, Union[str, float]]: The structured transaction data.
    """
    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'chain': chain,
        'protocol': protocol,
        'function_name': function_name,
        'transaction_type': transaction_type,
        'hash': hash_value,
        'timestamp': timestamp,
        'fees': fees,
        'fees_fiat': fees_fiat,
        'symbol': symbol,
        'balance': balance,
        'price': price,
        'value': value,
        'from': from_address,
        'to': to_address
    }

def process_octav_transactions(data: Dict[str, Any], wallet: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Preprocess the transaction data to extract relevant information.

    Args:
        data (Dict[str, Any]): The transaction data dictionary.
        wallet (Dict[str, Any]): The wallet data dictionary.

    Returns:
        List[Dict[str, Any]]: The preprocessed transaction data.
    """
    processed_transactions = []

    # Navigate to the transactions section
    try:
        transactions = data['getTransactions']['transactions']
    except (KeyError, IndexError) as e:
        logging.error(f"Error accessing transactions: {e}")
        return processed_transactions

    # Iterate over each transaction
    for transaction in transactions:
        chain = transaction.get('chain', {}).get('key', 'unknown')
        protocol = transaction.get('protocol', {}).get('key', 'unknown')
        function_name = transaction.get('functionName', 'unknown')
        transaction_type = transaction.get('type', 'unknown')
        hash_value = transaction.get('hash', 'unknown')
        timestamp = transaction.get('timestamp', 'unknown')
        fees = float(transaction.get('fees', 0))
        fees_fiat = float(transaction.get('feesFiat', 0))

        # Process assets in and out
        assets_in = transaction.get('assetsIn', [])
        assets_out = transaction.get('assetsOut', [])

        for asset in assets_in + assets_out:
            symbol = asset.get('symbol', 'unknown')
            balance = float(asset.get('balance', 0))
            price = float(asset.get('price', 0))
            value = float(asset.get('value', 0))
            from_address = asset.get('from', 'unknown')
            to_address = asset.get('to', 'unknown')

            # Create a transaction entry
            transaction_entry = create_transaction(
                wallet,
                chain,
                protocol,
                function_name,
                transaction_type,
                hash_value,
                timestamp,
                fees,
                fees_fiat,
                symbol,
                balance,
                price,
                value,
                from_address,
                to_address
            )
            processed_transactions.append(transaction_entry)

    logging.info(f"Total processed transactions: {len(processed_transactions)}")
    return processed_transactions

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    try:
        from src.wallet_apis.octav import fetch_octav_portfolio, fetch_octav_transactions

        address = '4k8GVZEdH3M2coXZwnyEhg2TwWXpVmPefbmvWeb2SrrZ'  # Replace with your actual address

        # Example wallet information
        wallet_info = {
            'id': 'example_wallet_id',
            'address': address,
            'type': 'example_wallet_type',
            'strategy': 'example_strategy'
        }

        # Fetch portfolio information
        portfolio_info = fetch_octav_portfolio(address)
        logging.info(f'Portfolio Information: {portfolio_info}')

        # Preprocess the portfolio information
        preprocessed_data = process_octav_portfolio(portfolio_info, wallet_info)
        logging.info(f'Preprocessed Data: {preprocessed_data}')

        # Fetch and process transactions
        transactions_info = fetch_octav_transactions(address)
        processed_transactions = process_octav_transactions(transactions_info, wallet_info)
        logging.info(f'Processed Transactions: {processed_transactions}')

    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")

    for position in preprocessed_data:
        print(position)
        print('-' * 100)

    for transaction in processed_transactions:
        print(transaction)
        print('-' * 100)
