import openpyxl
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from config import WALLETS, ASSETS_DICT, ASSET_DICT_FILE_PATH, LOG_FILE_PATH, POSITIONS_FILE_PATH, TRANSACTIONS_FILE_PATH
from config import POSITIONS_DATABASE_FILE_PATH, TRANSACTIONS_DATABASE_FILE_PATH
from config import BINANCE_API_KEY, BINANCE_API_SECRET, MANUAL_POSITIONS, POSITIONS_DICT, BETA_LOOKBACK

from src.wallet_processing.dydxv4 import process_dydxv4_positions, process_dydxv4_transactions
from src.wallet_processing.gemini import process_gemini_positions, process_gemini_transactions
from src.wallet_processing.circle import process_circle_positions, process_circle_transactions
from src.wallet_processing.blockcypher import (
    process_blockcypher_position,
    process_blockcypher_transactions,
    fetch_and_filter_transactions
)
from src.wallet_processing.octav import process_octav_portfolio
from src.wallet_processing.manual import process_manual_positions  # Import the manual processing function

from src.wallet_apis.gemini import fetch_gemini_user_spot_balances, fetch_gemini_user_perps_positions, fetch_gemini_spot_transactions, fetch_gemini_perps_transactions
from src.wallet_apis.circle import fetch_circle_user_balance, fetch_circle_user_deposits, fetch_circle_user_transfers, fetch_circle_user_redemptions, fetch_circle_user_wallets
from src.wallet_apis.blockcypher import fetch_blockcypher_user_balance
from src.wallet_apis.octav import fetch_octav_portfolio

from src.utils.fetch_prices import fetch_multiple_prices
from src.utils.beta_calculator import add_beta_to_positions
from src.utils.binance import fetch_historical_data as fetch_binance_data
from src.utils.cryptocompare import fetch_historical_data as fetch_cryptocompare_data
import os

# Configure logging
logging.basicConfig(level=logging.INFO, filename='output/logs.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

def process_wallets(wallets: List[Dict[str, str]], start_date: str, end_date: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_positions = []
    all_transactions = []

    start_date = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    end_date = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)

    for wallet in wallets:

        logging.info(f"Processing wallet: {wallet['id']} of type {wallet['type']}")
        
        try:
            if wallet['type'] == 'DYDX':
                logging.info(f'Pulling {wallet["type"]} wallet data address:{wallet["address"][-4:]}')
                positions = process_dydxv4_positions(wallet, start_date, end_date)
                transactions = process_dydxv4_transactions(wallet, start_date, end_date)
            elif wallet['type'] == 'GEMINI':
                logging.info(f'Pulling {wallet["type"]} wallet data address:{wallet["address"][-4:]}')
                spot_balances = fetch_gemini_user_spot_balances()
                perps_positions = fetch_gemini_user_perps_positions()
                spot_transactions = fetch_gemini_spot_transactions(start_date, end_date)
                perps_transactions = fetch_gemini_perps_transactions(start_date, end_date)
                positions = process_gemini_positions(spot_balances, perps_positions, wallet)
                transactions = process_gemini_transactions(spot_transactions, perps_transactions, wallet)
            elif wallet['type'] == 'CIRCLE':
                logging.info(f'Pulling {wallet["type"]} wallet data address:{wallet["address"][-4:]}')
                balances = fetch_circle_user_balance()
                positions = process_circle_positions(balances, wallet)
                transactions = process_circle_transactions(wallet, start_date, end_date)
            elif wallet['type'] in ['BTC', 'DOGE']:
                symbol = wallet['type'].lower()
                logging.info(f'Pulling {wallet["type"]} wallet data address:{wallet["address"][-4:]}')
                balance_data = fetch_blockcypher_user_balance(wallet['address'], symbol)
                positions = process_blockcypher_position(balance_data, wallet, symbol)
                raw_transactions = fetch_and_filter_transactions(wallet['address'], symbol, start_date, end_date)
                transactions = process_blockcypher_transactions(raw_transactions, wallet, symbol)
            elif wallet['type'] in ['EVM', 'SOL']:
                logging.info(f'Pulling {wallet["type"]} wallet data address:{wallet["address"][-4:]}')
                portfolio = fetch_octav_portfolio(wallet['address'])
                positions = process_octav_portfolio(portfolio, wallet)
            elif wallet['type'] == 'MANUAL':
                logging.info(f"Processing manual positions for wallet: {wallet['id']}")
                positions = process_manual_positions(MANUAL_POSITIONS, wallet)
                transactions = []  # No transactions for manual positions
            else:
                logging.warning(f"Unsupported wallet type: {wallet['type']}")
                continue

            all_positions.extend(positions)
            all_transactions.extend(transactions)

        except Exception as e:
            logging.error(f"Error processing wallet {wallet['id']}: {e}")

    positions_df = pd.DataFrame(all_positions)
    transactions_df = pd.DataFrame(all_transactions)

    return positions_df, transactions_df

def enrich_positions_with_asset_info(positions_df: pd.DataFrame, assets_dict: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    # Map asset information from ASSETS_DICT to the DataFrame
    positions_df['base_asset'] = positions_df['symbol'].map(lambda x: assets_dict.get(x, {}).get('base_asset', None))
    positions_df['asset_type'] = positions_df['symbol'].map(lambda x: assets_dict.get(x, {}).get('asset_type', None))
    positions_df['sector'] = positions_df['symbol'].map(lambda x: assets_dict.get(x, {}).get('sector', None))
    positions_df['reward_type'] = positions_df['symbol'].map(lambda x: assets_dict.get(x, {}).get('rewards', None))
    
    return positions_df

def append_missing_symbols_to_excel(missing_symbols: List[str], positions_df: pd.DataFrame):
    # Filter missing symbols based on position value > $5
    filtered_symbols = positions_df[
        (positions_df['symbol'].isin(missing_symbols)) & 
        (positions_df['value'] > 5)
    ]['symbol'].unique()

    if len(filtered_symbols) == 0:
        logging.info("No missing symbols with position value greater than $5 to add.")
        return

    # Load the existing Excel file
    try:
        assets_df = pd.read_excel(ASSET_DICT_FILE_PATH)
    except FileNotFoundError:
        logging.error(f"Excel file not found at {ASSET_DICT_FILE_PATH}. Creating a new one.")
        assets_df = pd.DataFrame(columns=['symbol', 'base_asset', 'asset_type', 'sector'])

    # Add missing symbols with empty fields
    new_entries = pd.DataFrame({'symbol': filtered_symbols, 'base_asset': None, 'asset_type': None, 'sector': None})
    updated_assets_df = pd.concat([assets_df, new_entries]).drop_duplicates(subset='symbol', keep='first')

    # Save the updated DataFrame back to the Excel file
    updated_assets_df.to_excel(ASSET_DICT_FILE_PATH, index=False)
    logging.info(f"Added missing symbols to Excel: {filtered_symbols}")

def fill_missing_prices_values_and_equity(positions_df: pd.DataFrame) -> pd.DataFrame:
    # Fill missing prices using existing data in the DataFrame
    positions_df['price'] = positions_df.groupby('symbol')['price'].transform(lambda x: x.ffill().bfill())

    # Identify symbols with missing prices
    missing_price_symbols = positions_df[positions_df['price'].isna()]['symbol'].unique()

    if missing_price_symbols.size > 0:
        logging.info(f"Fetching prices for missing symbols: {missing_price_symbols}")
        # Fetch prices for missing symbols
        fetched_prices = fetch_multiple_prices(missing_price_symbols)

        # Fill in the missing prices
        for symbol, price in fetched_prices.items():
            positions_df.loc[(positions_df['symbol'] == symbol) & (positions_df['price'].isna()), 'price'] = price

    # Fill missing values using 'amount' * 'price'
    positions_df['value'] = positions_df.apply(
        lambda row: row['amount'] * row['price'] if pd.isna(row['value']) else row['value'],
        axis=1
    )

    # Fill missing equity values with 'value' unless 'position_type' is 'perps'
    positions_df['equity'] = positions_df.apply(
        lambda row: row['value'] if pd.isna(row['equity']) and row['position_type'] != 'perps' else row['equity'],
        axis=1
    )

    # Fill missing notional values
    positions_df['notional'] = positions_df.apply(
        lambda row: 0 if (row['asset_type'] == 'STABLE' and row['value'] < 0) else abs(row['value']),
        axis=1
    )

    return positions_df

def main():
    start_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    logging.info(f"Portfolio successfully run. Start date: {start_date}, End date: {end_date}")

    positions_df, transactions_df = process_wallets(WALLETS, start_date, end_date)

    logging.info(f"Total positions: {len(positions_df)}")
    logging.info(f"Total transactions: {len(transactions_df)}")

    # Enrich positions with asset information
    positions_df = enrich_positions_with_asset_info(positions_df, ASSETS_DICT)

    # Fill missing prices, values, equity, and notional in positions DataFrame
    positions_df = fill_missing_prices_values_and_equity(positions_df)

    # Filter out positions with a 'value' less than the absolute value of (-1, 1)
    positions_df = positions_df[positions_df['value'].abs() >= 1]

    # Log symbols not found in the asset dictionary
    missing_symbols = positions_df[positions_df['base_asset'].isna()]['symbol'].unique()
    if missing_symbols.size > 0:
        logging.warning(f"The following symbols are missing information in the asset dictionary: {missing_symbols}. Please add information and run reprocessing.")
        append_missing_symbols_to_excel(missing_symbols, positions_df)

    # Add 'position' column based on 'protocol' and 'symbol'
    positions_df['position'] = positions_df.apply(
        lambda row: (
            'cash' if (
                row['protocol'] in ['wallet', 'gemini', 'circle', 'dydxv4'] and 
                row['asset_type'] == 'STABLE' and 
                row['reward_type'] == 'none'
            ) else (
                f"{row['protocol']} - {row['symbol']}" if row['protocol'] != 'wallet' 
                else row['symbol']
            )
        ),
        axis=1
    )

    # Add a date column with the end date
    positions_df['date'] = pd.to_datetime(end_date).date()

    # Create a dictionary from POSITIONS_DICT for easy lookup
    positions_dict = {entry['position_id']: entry for entry in POSITIONS_DICT}

    # Function to update position and position_type
    def update_position(row):
        pos_info = positions_dict.get(row['position_id'])
        if pos_info:
            row['position'] = pos_info.get('position', row['position'])
            row['position_type'] = pos_info.get('position_type', row.get('position_type'))
        return row

    # Apply the update function
    positions_df = positions_df.apply(update_position, axis=1)

    # Calculate and add beta columns using Binance for historical data
    from binance.client import Client
    client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

    # First attempt to calculate beta using CryptoCompare
    btc_data = fetch_cryptocompare_data('BTC', limit=BETA_LOOKBACK)
    positions_df = add_beta_to_positions(positions_df, btc_data, lambda symbol, lookback_days: fetch_cryptocompare_data(symbol, limit=lookback_days))

    # Check if 'beta_daily' column exists before accessing it
    if 'beta_daily' in positions_df.columns:
        # Identify assets with NaN beta values
        missing_beta_assets = positions_df[positions_df['beta_daily'].isna()]['base_asset'].unique()

        if missing_beta_assets.size > 0:
            missing_value = positions_df[positions_df['base_asset'].isin(missing_beta_assets)]['value'].sum()
            logging.warning(f"Symbols {missing_beta_assets} are missing historical price information and are not accounted for in beta calculations. This equates to {missing_value} amount of value.")
            logging.info(f"Attempting to calculate beta for missing assets using Binance: {missing_beta_assets}")
            btc_data = fetch_binance_data('BTC', client, BETA_LOOKBACK)

            # Filter positions to only include missing assets
            missing_positions_df = positions_df[positions_df['base_asset'].isin(missing_beta_assets)]

            # Calculate beta for missing assets using Binance
            updated_missing_positions_df = add_beta_to_positions(missing_positions_df, btc_data, lambda symbol, lookback_days: fetch_binance_data(symbol, client, lookback_days))

            # Update the original positions DataFrame with the newly calculated betas
            positions_df.update(updated_missing_positions_df)

    # Set the date column as the index
    positions_df.set_index('date', inplace=True)
    transactions_df['date'] = pd.to_datetime(end_date).date()
    transactions_df.set_index('date', inplace=True)

    # Save current positions and transactions to Excel files
    positions_df.to_excel(POSITIONS_FILE_PATH, engine='openpyxl')
    transactions_df.to_excel(TRANSACTIONS_FILE_PATH, engine='openpyxl')

    # Append current positions to the positions database
    if os.path.exists(POSITIONS_DATABASE_FILE_PATH):
        positions_db_df = pd.read_excel(POSITIONS_DATABASE_FILE_PATH, index_col=0)
        positions_db_df = pd.concat([positions_db_df, positions_df], ignore_index=False)
    else:
        positions_db_df = positions_df

    positions_db_df.to_excel(POSITIONS_DATABASE_FILE_PATH, engine='openpyxl')

    # Append current transactions to the transactions database
    if os.path.exists(TRANSACTIONS_DATABASE_FILE_PATH):
        transactions_db_df = pd.read_excel(TRANSACTIONS_DATABASE_FILE_PATH, index_col=0)
        transactions_db_df = pd.concat([transactions_db_df, transactions_df], ignore_index=False)
    else:
        transactions_db_df = transactions_df

    transactions_db_df.to_excel(TRANSACTIONS_DATABASE_FILE_PATH, engine='openpyxl')

    logging.info("Data processing complete. Results saved to positions.xlsx and transactions.xlsx")

if __name__ == "__main__":
    main()
