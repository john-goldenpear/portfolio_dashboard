import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from apis.gemini import fetch_gemini_user_perps_positions, fetch_gemini_user_spot_balances, fetch_gemini_user_perps_transactions, fetch_gemini_user_spot_transactions

logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, str], data_type: str, symbol: str, amount: float, price: float, cost_basis: float = 0.0, unrealized_gain: float = 0.0, realized_gain: float = 0.0, closed_qty: float = None, closed_price: float = None, opened_qty: float = None, opened_price: float = None) -> Dict[str, Any]:
    """
    Helper function to create a position dictionary.

    Args:
        wallet (Dict[str, str]): Wallet information.
        data_type (str): Type of data being processed ('spot' or 'perps').
        symbol (str): Symbol of the asset.
        amount (float): Amount of the asset.
        price (float): Price of the asset.
        cost_basis (float): Cost basis of the asset. Defaults to 0.0.
        unrealized_gain (float): Unrealized gain of the asset. Defaults to 0.0.
        realized_gain (float): Realized gain of the asset. Defaults to 0.0.
        closed_qty (float, optional): Quantity of the asset when the position is closed. Defaults to None.
        closed_price (float, optional): Price of the asset when the position is closed. Defaults to None.
        opened_qty (float, optional): Quantity of the asset when the position is opened within the last 24 hours. Defaults to None.
        opened_price (float, optional): Price of the asset when the position is opened within the last 24 hours. Defaults to None.

    Returns:
        Dict[str, Any]: Position dictionary.
    """
    chain = 'gemini'
    protocol = 'gemini'
    position_type = 'hodl' if data_type == 'spot' else 'perps'

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
        'price': price,
        'cost_basis': cost_basis,
        'unrealized_gain': unrealized_gain,
        'realized_gain': realized_gain,
        'opened_qty': opened_qty,
        'closed_qty': closed_qty,
        'opened_price': opened_price,
        'closed_price': closed_price
    }

def process_gemini_spot_data(data: List[Dict[str, Any]], transactions: List[Dict[str, Any]], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process spot data fetched from the Gemini API.

    Args:
        data (List[Dict[str, Any]]): List of positions in Gemini fetched from Gemini API.
        transactions (List[Dict[str, Any]]): List of transactions in Gemini fetched from Gemini API.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).

    Returns:
        List[Dict[str, Any]]: Processed token data with wallet information included.
    """
    processed_data = []
    now = datetime.utcnow()

    # Process open positions
    open_positions = set()
    for position in data:
        try:
            symbol = position['currency']
            amount = float(position['amount'])
            amount_notional = float(position['amountNotional'])
            price = amount_notional / amount

            processed_position = create_position(
                wallet=wallet,
                data_type='spot',
                symbol=symbol,
                amount=amount,
                price=price
            )
            processed_data.append(processed_position)

            open_positions.add(symbol)
        except KeyError as e:
            logging.error(f"Missing expected key in position data: {e}")
        except ValueError as e:
            logging.error(f"Error converting data to float: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    # Aggregate transactions to find recently closed positions and any corresponding opening transactions
    closed_positions = {}
    for transaction in transactions:
        try:
            timestamp = datetime.utcfromtimestamp(transaction['timestamp'])
            symbol = transaction['symbol']
            amount = float(transaction['amount'])
            price = float(transaction['price'])

            if now - timestamp < timedelta(hours=24):
                if symbol not in open_positions:
                    if symbol not in closed_positions:
                        closed_positions[symbol] = {
                            'closed_qty': 0.0,
                            'total_closed_price_qty': 0.0,
                            'opened_qty': 0.0,
                            'total_opened_price_qty': 0.0
                        }
                    if transaction['type'].lower() == 'sell':
                        closed_positions[symbol]['closed_qty'] += amount
                        closed_positions[symbol]['total_closed_price_qty'] += amount * price
                    elif transaction['type'].lower() == 'buy':
                        closed_positions[symbol]['opened_qty'] += amount
                        closed_positions[symbol]['total_opened_price_qty'] += amount * price
        except KeyError as e:
            logging.error(f"Missing expected key in transaction data: {e}")
        except ValueError as e:
            logging.error(f"Error converting data to float: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    for symbol, values in closed_positions.items():
        closed_qty = values['closed_qty']
        closed_price = values['total_closed_price_qty'] / closed_qty if closed_qty != 0 else 0

        opened_qty = values['opened_qty']
        opened_price = values['total_opened_price_qty'] / opened_qty if opened_qty != 0 else 0

        closed_position = create_position(
            wallet=wallet,
            data_type='spot',
            symbol=symbol,
            amount=0.0,  # Closed positions have no amount
            price=0.0,  # Closed positions have no price
            cost_basis=None,  # We do not know the cost basis for closed positions
            unrealized_gain=0.0,
            realized_gain=0.0,
            closed_qty=closed_qty,
            closed_price=closed_price,
            opened_qty=opened_qty if opened_qty > 0 else None,
            opened_price=opened_price if opened_price > 0 else None
        )
        processed_data.append(closed_position)

    return processed_data

def process_gemini_perps_data(data: List[Dict[str, Any]], transactions: List[Dict[str, Any]], wallet: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process perpetual data fetched from the Gemini API.

    Args:
        data (List[Dict[str, Any]]): List of positions in Gemini fetched from Gemini API.
        transactions (List[Dict[str, Any]]): List of transactions in Gemini fetched from Gemini API.
        wallet (Dict[str, str]): Dictionary containing wallet information (address, type, strategy).

    Returns:
        List[Dict[str, Any]]: Processed token data with wallet information included.
    """
    processed_data = []
    now = datetime.utcnow()

    # Process open positions
    open_positions = set()
    for position in data:
        try:
            symbol = position['symbol'].replace('gusdperp', '').upper()
            amount = float(position['quantity'])
            price = float(position['mark_price'])
            cost_basis = float(position['average_cost']) * amount
            unrealized_gain = float(position['unrealised_pnl'])
            realized_gain = float(position['realised_pnl'])

            processed_position = create_position(
                wallet=wallet,
                data_type='perps',
                symbol=symbol,
                amount=amount,
                price=price,
                cost_basis=cost_basis,
                unrealized_gain=unrealized_gain,
                realized_gain=realized_gain
            )
            processed_data.append(processed_position)

            open_positions.add(symbol)
        except KeyError as e:
            logging.error(f"Missing expected key in position data: {e}")
        except ValueError as e:
            logging.error(f"Error converting data to float: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    # Aggregate transactions to find recently closed positions and any corresponding opening transactions
    closed_positions = {}
    for transaction in transactions:
        try:
            timestamp = datetime.utcfromtimestamp(transaction['timestamp'])
            symbol = transaction['symbol'].replace('gusdperp', '').upper()
            amount = float(transaction['amount'])
            price = float(transaction['price'])

            if now - timestamp < timedelta(hours=24):
                if symbol not in open_positions:
                    if symbol not in closed_positions:
                        closed_positions[symbol] = {
                            'closed_qty': 0.0,
                            'total_closed_price_qty': 0.0,
                            'opened_qty': 0.0,
                            'total_opened_price_qty': 0.0
                        }
                    if transaction['type'].lower() == 'buy':
                        closed_positions[symbol]['closed_qty'] += amount
                        closed_positions[symbol]['total_closed_price_qty'] += amount * price
                    elif transaction['type'].lower() == 'sell':
                        closed_positions[symbol]['opened_qty'] += amount
                        closed_positions[symbol]['total_opened_price_qty'] += amount * price
        except KeyError as e:
            logging.error(f"Missing expected key in transaction data: {e}")
        except ValueError as e:
            logging.error(f"Error converting data to float: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    for symbol, values in closed_positions.items():
        closed_qty = values['closed_qty']
        closed_price = values['total_closed_price_qty'] / closed_qty if closed_qty != 0 else 0

        opened_qty = values['opened_qty']
        opened_price = values['total_opened_price_qty'] / opened_qty if opened_qty != 0 else 0

        closed_position = create_position(
            wallet=wallet,
            data_type='perps',
            symbol=symbol,
            amount=0.0,  # Closed positions have no amount
            price=0.0,  # Closed positions have no price
            cost_basis=None,  # We do not know the cost basis for closed positions
            unrealized_gain=0.0,
            realized_gain=0.0,
            closed_qty=closed_qty,
            closed_price=closed_price,
            opened_qty=opened_qty if opened_qty > 0 else None,
            opened_price=opened_price if opened_price > 0 else None
        )
        processed_data.append(closed_position)

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
                spot_transactions = fetch_gemini_user_spot_transactions()
                perps_positions = fetch_gemini_user_perps_positions()
                perps_transactions = fetch_gemini_user_perps_transactions()
            except Exception as e:
                logging.error(f"Error fetching data for wallet {wallet['address']}: {e}")
                continue

            processed_spot_data = process_gemini_spot_data(spot_data, spot_transactions, wallet)
            processed_perps_data = process_gemini_perps_data(perps_positions, perps_transactions, wallet)
            gemini_data = processed_spot_data + processed_perps_data
            all_data.extend(gemini_data)

    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame(all_data)
    logging.info(df)