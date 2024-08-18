import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from apis.circle import fetch_circle_user_balance, fetch_circle_user_deposits, fetch_circle_user_transfers, fetch_circle_user_redemptions

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], amount: float, qty_opened: float, qty_closed: float) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        amount (float): Amount of the asset.
        qty_opened (float): Quantity opened.
        qty_closed (float): Quantity closed.

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    chain = 'circle'
    protocol = 'circle'
    position_type = 'hodl'
    symbol = 'USDC'

    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': None,
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol,
        'type': position_type,
        'symbol': symbol,
        'amount': amount,
        'price': 1.0,  # Price is 1.0 as it represents cash
        'opened_qty': qty_opened,
        'closed_qty': qty_closed,
        'opened_price': 1,
        'closed_price': 1,
        'fees_day': None,
        'fees_asset': symbol,
        'fees_day_usd': None
    }

def process_circle_data(circle_data: Dict[str, Any], wallet: Dict[str, str], deposits: List[Dict[str, Any]], transfers: List[Dict[str, Any]], redemptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process Circle data to extract and structure relevant information.

    Args:
        circle_data (Dict[str, Any]): Data fetched from the Circle API.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).
        deposits (List[Dict[str, Any]]): List of deposit transactions.
        transfers (List[Dict[str, Any]]): List of transfer transactions.
        redemptions (List[Dict[str, Any]]): List of redemption transactions.

    Returns:
        List[Dict[str, Any]]: Processed data with wallet information included.
    """
    data = []

    now = datetime.utcnow()
    past_24_hours = now - timedelta(hours=24)
    
    qty_opened = sum(float(d['amount']['amount']) for d in deposits['data'] if past_24_hours <= datetime.strptime(d['createDate'], '%Y-%m-%dT%H:%M:%S.%fZ') <= now)
    qty_closed = sum(float(t['amount']['amount']) for t in transfers['data'] if past_24_hours <= datetime.strptime(t['createDate'], '%Y-%m-%dT%H:%M:%S.%fZ') <= now)
    qty_closed += sum(float(r['amount']['amount']) for r in redemptions['data'] if past_24_hours <= datetime.strptime(r['createDate'], '%Y-%m-%dT%H:%M:%S.%fZ') <= now)

    available_balance = circle_data.get('data', {}).get('available', [])
    if available_balance:
        balance = available_balance[0]  # There will only be one position
        amount = float(balance['amount'])
        position = create_position(wallet, amount, qty_opened, qty_closed)
        data.append(position)

    return data

# Example usage
if __name__ == "__main__":
    wallet = {'id': 'circle', 'address': 'circle', 'type': 'circle', 'strategy': 'hold'}
    circle_data = fetch_circle_user_balance()
    deposits = fetch_circle_user_deposits()
    transfers = fetch_circle_user_transfers()
    redemptions = fetch_circle_user_redemptions()
    processed_data = process_circle_data(circle_data, wallet, deposits, transfers, redemptions)
    logging.info(f"Processed Circle Data: {processed_data}")