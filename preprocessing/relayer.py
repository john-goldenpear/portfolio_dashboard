import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from apis.relayer import fetch_relayer_positions
from apis.debank import fetch_debank_user_transactions

logging.basicConfig(level=logging.INFO)

# Mapping of chain numbers to chain names
CHAIN_MAP = {
    '1': 'eth',
    '10': 'op',
    '137': 'polygon',
    '324': 'zk',
    '8453': 'base',
    '34443': 'mode',
    '42161': 'arb',
    '59144': 'linea'
}

def create_position(wallet: Dict[str, str], position_id: str, chain: str, protocol_id: str, position_type: str, symbol: str, amount: float, price: float, income_asset_change: float, income_usd_change: float, opened_qty: float, closed_qty: float, opened_price: float, closed_price: float, fees_asset_change: float) -> Dict[str, Any]:
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
        income_asset_change (float): Income asset change.
        income_usd_change (float): Income USD change.
        opened_qty (float): Quantity opened.
        closed_qty (float): Quantity closed.
        opened_price (float): Price opened.
        closed_price (float): Price closed.
        fees_asset_change (float): Fees asset change.

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
        'income_asset_change': income_asset_change,
        'income_usd_change': income_usd_change,
        'opened_qty': opened_qty,
        'closed_qty': closed_qty,
        'opened_price': opened_price,
        'closed_price': closed_price,
        'fees_asset_change': fees_asset_change
    }

def fetch_and_process_transactions(wallet_address: str) -> List[Dict[str, Any]]:
    """
    Fetch and process transactions for a given wallet address and chain IDs.

    Args:
        wallet_address (str): The wallet address to fetch transactions for.
        chain_ids (List[str]): List of chain IDs to fetch transactions for.

    Returns:
        List[Dict[str, Any]]: Processed transactions data.
    """
    end_time = int(datetime.now().timestamp())
    start_time = end_time - 24 * 3600  # Transactions from the last 24 hours
    transactions = fetch_debank_user_transactions(wallet_address, end_time, start_time)
    return transactions

def calculate_transaction_sums(transactions: List[Dict[str, Any]], wallet_address: str) -> Dict[str, float]:
    """
    Calculate sums for opened_qty, closed_qty, and fees_asset_change based on transactions.

    Args:
        transactions (List[Dict[str, Any]]): List of transactions.
        wallet_address (str): The wallet address to check against.

    Returns:
        Dict[str, float]: Calculated sums for opened_qty, closed_qty, and fees_asset_change.
    """
    opened_qty = 0
    closed_qty = 0
    fees_asset_change = 0

    for txn in transactions:
        tx_details = txn['tx']
        if tx_details['name'] == ('transfer' or 'Receive' or 'Send') :
            opened_qty += sum(receive['amount'] for receive in txn['receives'] if receive['from_addr'] != wallet_address)
            closed_qty += sum(send['amount'] for send in txn['sends'] if send['to_addr'] != wallet_address)
            fees_asset_change += tx_details.get('eth_gas_fee', 0)

    return {
        'opened_qty': opened_qty,
        'closed_qty': closed_qty,
        'fees_asset_change': fees_asset_change
    }

def process_relayer_portfolio_data(relayer_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process relayer portfolio data fetched from the Relayer API.

    Args:
        relayer_data (Dict[str, Any]): Dictionary containing relayer data fetched from the API.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).

    Returns:
        List[Dict[str, Any]]: Processed relayer portfolio data with wallet information included.
    """
    processed_data = []
    transactions = fetch_and_process_transactions(wallet['address'])

    transaction_sums = calculate_transaction_sums(transactions, wallet['address'])
    opened_qty = transaction_sums['opened_qty']
    closed_qty = transaction_sums['closed_qty']
    fees_asset_change = transaction_sums['fees_asset_change']

    portfolio = relayer_data.get('portfolio', {})
    for asset, details in portfolio.items():
        income_asset_change = details.get('profit24h', 0) / (10 ** 18)
        income_usd_change = details.get('profitUsd', 0)

        position = create_position(
            wallet=wallet,
            position_id=f"across-relay-{asset}",
            chain='N/A',
            protocol_id='across-relay',
            position_type='relay',
            symbol=asset,
            amount=details.get('balance', 0) / (10 ** 18),  # Convert from wei to ETH/ERC20 standard
            price=details.get('price', 0),
            income_asset_change=income_asset_change,
            income_usd_change=income_usd_change,
            opened_qty=opened_qty,
            closed_qty=closed_qty,
            opened_price=None,
            closed_price=None,
            fees_asset_change=fees_asset_change
        )
        processed_data.append(position)

    return processed_data

def process_relayer_position_data(relayer_data: Dict[str, Any], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process relayer position data fetched from the Relayer API.

    Args:
        relayer_data (Dict[str, Any]): Dictionary containing relayer data fetched from the API.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).

    Returns:
        List[Dict[str, Any]]: Processed relayer position data with wallet information included.
    """
    processed_data = []
    transactions = fetch_and_process_transactions(wallet['address'])

    transaction_sums = calculate_transaction_sums(transactions, wallet['address'])
    opened_qty = transaction_sums['opened_qty']
    closed_qty = transaction_sums['closed_qty']
    fees_asset_change = transaction_sums['fees_asset_change']

    protocol = 'across relay'

    positions = relayer_data.get('positions', {})
    for chain_key, tokens in positions.items():
        chain_number = chain_key.replace('chain_', '')
        chain = CHAIN_MAP.get(chain_number, 'unknown')
        for token, details in tokens.items():
            position_type = 'hodl' if token == 'nativeToken' else 'relay'
            symbol = 'ETH' if token == 'nativeToken' else token
            income_asset_change = details.get('profit24h', 0) / (10 ** 18)
            income_usd_change = details.get('profitUsd', 0)

            position = create_position(
                wallet=wallet,
                position_id=f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
                chain=chain,
                protocol_id=protocol,
                position_type=position_type,
                symbol=symbol,
                amount=details.get('positionTotal', 0) / (10 ** 18),  # Convert from wei to ETH/ERC20 standard
                price=details.get('price', 0),
                income_asset_change=income_asset_change,
                income_usd_change=income_usd_change,
                opened_qty=opened_qty,
                closed_qty=closed_qty,
                opened_price=None,
                closed_price=None,
                fees_asset_change=fees_asset_change
            )
            processed_data.append(position)

    return processed_data

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'XXXX', 'address': '0x4a4e392290A382C9d2754E5Dca8581eA1893db5D', 'type': 'EVM', 'strategy': 'Quality'}
    try:
        relayer_data = fetch_relayer_positions(wallet['address'])
        
        # Process portfolio-level data
        portfolio_data = process_relayer_portfolio_data(relayer_data, wallet)
        logging.info(f"Portfolio Data: {portfolio_data}")
        
        # Process position-level data
        position_data = process_relayer_position_data(relayer_data, wallet)
        logging.info(f"Position Data: {position_data}")

    except Exception as e:
        logging.error(f"Error processing data for wallet {wallet['address']}: {e}")

for position in position_data:
    print('--------')
    print(position)