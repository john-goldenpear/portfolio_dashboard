# import os and sys
import os
import sys

# Add the parent directory of src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import other packages
import pandas as pd
import logging
from datetime import datetime, timedelta

# import environment variables from config file
from config import WALLETS, SOLANA_TOKENS, ASSETS_DICT

# import custom api functions from project files
from apis.circle import fetch_circle_user_balance, fetch_circle_user_deposits, fetch_circle_user_redemptions, fetch_circle_user_transfers
from apis.gemini import fetch_gemini_user_spot_balances, fetch_gemini_user_spot_transfers, fetch_gemini_user_spot_transactions, fetch_gemini_user_spot_custody_fees, fetch_gemini_user_perps_positions, fetch_gemini_user_perps_transfers, fetch_gemini_user_perps_transactions, fetch_gemini_user_perps_account_balance
from apis.debank import fetch_debank_user_balances_protocol, fetch_debank_user_balances_tokens
from apis.relayer import fetch_relayer_positions
from apis.blockcypher import fetch_blockcypher_user_balance, fetch_blockcypher_transactions
from apis.solana import fetch_solana_user_balance, fetch_solana_user_token_balances
from apis.dydxv4 import fetch_dydxv4_address_info
from apis.dydxv3 import dydxClient

# import custom preprocessing functions from project files
from preprocessing.fetch_prices import fetch_multiple_prices
from preprocessing.circle import process_circle_data
from preprocessing.gemini import process_gemini_perps_data, process_gemini_spot_data
from preprocessing.debank import process_evm_protocol_data, process_evm_token_data
from preprocessing.relayer import process_relayer_position_data
from preprocessing.blockcypher import process_blockcypher_data
from preprocessing.dydxv4 import process_dydxv4_data
from preprocessing.dydxv3 import process_dydxv3_data
from preprocessing.solana import process_solana_data, process_solana_token_data

# define function for main code
def main():

    # Configure logging
    log_file_path = r'C:\Users\JohnRogic\OneDrive - Golden Pear\Shared Documents - GP Research Share Site\John\.Projects\.github\portfolio_dashboard\output\portfolio_dashboard.log'
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Log script start time
    start_time = datetime.utcnow()
    logging.info("Script started.")

    all_positions = []

    for wallet in WALLETS:
        address = wallet['address']
        wallet_type = wallet['type']
        key = wallet.get('dydxv3_key')
        secret = wallet.get('dydxv3_secret')
        passphrase = wallet.get('dydxv3_phrase')

        try:
            if wallet_type == 'CIRCLE':
                logging.info('Pulling Circle wallet data')
                positions_raw = fetch_circle_user_balance()
                deposits = fetch_circle_user_deposits()
                transfers = fetch_circle_user_transfers()
                redemptions = fetch_circle_user_redemptions()
                positions = process_circle_data(positions_raw, wallet, deposits, transfers, redemptions)

            elif wallet_type == 'GEMINI':
                logging.info('Pulling Gemini wallet data')
                spot_positions_raw = fetch_gemini_user_spot_balances()
                spot_transactions = fetch_gemini_user_spot_transactions()
                perps_positions_raw = fetch_gemini_user_perps_positions()
                perps_transactions = fetch_gemini_user_perps_transactions()
                positions = process_gemini_spot_data(spot_positions_raw, spot_transactions, wallet) + process_gemini_perps_data(perps_positions_raw, perps_transactions, wallet)

            elif wallet_type == 'DYDX':
                logging.info(f'Pulling dYdX v4 wallet data address:{wallet["address"][-4:]}')
                positions_raw = fetch_dydxv4_address_info(address)
                positions = process_dydxv4_data(positions_raw, wallet)

            elif wallet_type == 'RELAY':
                logging.info(f'Pulling Relay wallet data address:{wallet["address"][-4:]}')
                positions_raw = fetch_relayer_positions(address)
                positions = process_relayer_position_data(positions_raw, wallet)

            elif wallet_type == 'BTC':
                logging.info(f'Pulling Bitcoin wallet data address:{wallet["address"][-4:]}')
                position_raw = fetch_blockcypher_user_balance(address, 'btc')
                transactions = fetch_blockcypher_transactions(address)
                positions = process_blockcypher_data(position_raw, wallet, 'BTC', transactions)

            elif wallet_type == 'DOGE':
                logging.info(f'Pulling Doge wallet data  address:{wallet["address"][-4:]}')
                position_raw = fetch_blockcypher_user_balance(address, 'doge')
                transactions = fetch_blockcypher_transactions(address)
                positions = process_blockcypher_data(position_raw, wallet, 'DOGE', transactions)

            elif wallet_type == 'EVM':
                logging.info(f'Pulling EVM wallet data address:{wallet["address"][-4:]}')
                positions_tokens_raw = fetch_debank_user_balances_tokens(address)
                positions_protocols_raw = fetch_debank_user_balances_protocol(address)
                positions = process_evm_token_data(positions_tokens_raw, wallet) + process_evm_protocol_data(positions_protocols_raw, wallet)

                if pd.notna(key) and pd.notna(secret) and pd.notna(passphrase):
                    logging.info(f'Pulling dYdX v3 account data address:{wallet["address"][-4:]}')
                    dydxv3_balances = dydxClient(key, secret, passphrase, address).get_account_info()
                    dydxv3_positions = process_dydxv3_data(dydxv3_balances, wallet)
                    positions.extend(dydxv3_positions)

            elif wallet_type == 'SOL':
                logging.info(f'Pulling Solana wallet data address:{wallet["address"][-4:]}')
                sol_balance_raw = fetch_solana_user_balance(address)
                sol_token_positions_raw = fetch_solana_user_token_balances(address)
                sol_positions = process_solana_data(wallet, sol_balance_raw)
                sol_token_positions = process_solana_token_data(wallet, sol_token_positions_raw, SOLANA_TOKENS)
                positions = sol_positions + sol_token_positions

            all_positions.extend(positions)
        except Exception as e:
            logging.error(f"Error processing wallet {wallet['address'][-4:]}: {e}")

    # Create DataFrame
    positions_df = pd.DataFrame(all_positions)

    # Add date column
    positions_df['date'] = start_time.date()

    # Fetch prices for rows where price is None (solana, btc, and doge)
    symbols_to_fetch = positions_df[positions_df['price'].isnull()]['symbol'].unique()
    prices = fetch_multiple_prices(symbols_to_fetch)
    positions_df['price'] = positions_df.apply(lambda row: prices.get(row['symbol']) if pd.isna(row['price']) else row['price'], axis=1)

    # Add value column and equity column
    positions_df['value'] = positions_df['amount'] * positions_df['price']
    positions_df['equity'] = positions_df['equity'].fillna(positions_df['value'])

    # Add columns 'base_asset', 'sector', 'asset_type' from ASSETS_DICT
    positions_df['base_asset'] = positions_df['symbol'].map(lambda x: ASSETS_DICT.get(x, {}).get('base_asset'))
    positions_df['sector'] = positions_df['symbol'].map(lambda x: ASSETS_DICT.get(x, {}).get('sector'))
    positions_df['bucket'] = positions_df['symbol'].map(lambda x: ASSETS_DICT.get(x, {}).get('bucket'))

    # Add notional column
    positions_df['notional'] = positions_df.apply(lambda row: abs(row['value']) if row['bucket'] != 'STABLE' else 0, axis=1)

    # Add change_amount columns
    positions_df['amount_change'] = 0.0

    # Reorder columns
    positions_df = positions_df[['date', 'wallet_address', 'wallet_id', 'wallet_type', 'contract_address', 'position_id', 'strategy', 'chain', 'protocol', 'symbol', 'base_asset', 'sector', 'bucket', 'type', 'amount', 'price', 'value', 'equity', 'notional', 
                                'opened_qty', 'closed_qty', 'opened_price', 'closed_price', 'cost_basis', 'unrealized_gain', 'realized_gain', 'income_usd', 'fees_day', 'fees_asset', 'fees_day_usd', 'amount_change']]
    # Check if the master file exists
    master_file = r'C:\Users\JohnRogic\OneDrive - Golden Pear\Shared Documents - GP Research Share Site\John\.Projects\.github\portfolio_dashboard\output\positions_database.xlsx'

    if os.path.exists(master_file):
        # Load the existing master file
        existing_df = pd.read_excel(master_file)

        # Set cost_basis and change_amount based on the previous day's data
        previous_day = (datetime.now() - timedelta(days=1)).date()
        previous_day_df = existing_df[existing_df['date'] == previous_day]

        if not previous_day_df.empty:
            for idx, row in positions_df.iterrows():
                previous_position = previous_day_df[previous_day_df['position_id'] == row['position_id']]
                if not previous_position.empty:
                    positions_df.at[idx, 'cost_basis'] = previous_position.iloc[0]['cost_basis']
                    positions_df.at[idx, 'amount_change'] = row['amount'] - previous_position.iloc[0]['amount']
                else:
                    positions_df.at[idx, 'cost_basis'] = row['value']
                    positions_df.at[idx, 'amount_change'] = row['amount']
        else:
            positions_df['cost_basis'] = positions_df['value']
            positions_df['amount_change'] = positions_df['amount']
        
        # Append the new data
        combined_df = pd.concat([existing_df, positions_df], ignore_index=True)

        # Save the combined data back to the master file
        combined_df.to_excel(master_file, index=False)
    else:
        # If the master file doesn't exist, save the new data as the master file
        positions_df['cost_basis'] = positions_df['value']
        positions_df['amount_change'] = positions_df['amount']
        positions_df.to_excel(master_file, index=False)

    # Save today's data to a separate file for reference
    filename = r'C:\Users\JohnRogic\OneDrive - Golden Pear\Shared Documents - GP Research Share Site\John\.Projects\.github\portfolio_dashboard\output\positions_data.xlsx'
    positions_df.to_excel(filename, index=False)

    # Log script end time
    end_time = datetime.utcnow()
    logging.info("Script completed successfully.")
    logging.info(f"Script started at: {start_time}")
    logging.info(f"Script ended at: {end_time}")

if __name__ == "__main__":
    main()