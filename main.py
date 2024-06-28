import pandas as pd
import numpy as np
from config import WALLETS, SOLANA_TOKENS, ASSETS_DICT

from apis.circle import fetch_circle_user_balance
from apis.gemini import fetch_gemini_user_spot_balances, fetch_gemini_user_perps_balances
from apis.debank import fetch_debank_user_balances_protocol, fetch_debank_user_balances_tokens
from apis.relayer import fetch_relayer_positions
from apis.blockcypher import fetch_blockcypher_user_balance
from apis.solana import fetch_solana_user_balance, fetch_solana_user_token_balances
from apis.dydxv4 import fetch_dydxv4_address_info
from apis.dydxv3 import dydxClient

from preprocessing.fetch_prices import fetch_multiple_prices
from preprocessing.circle import process_circle_data
from preprocessing.gemini import process_gemini_data
from preprocessing.debank import process_evm_protocol_data, process_evm_token_data
from preprocessing.relayer import process_relayer_position_data
from preprocessing.blockcypher import process_blockcypher_data
from preprocessing.dydxv4 import process_dydxv4_data
from preprocessing.dydxv3 import process_dydxv3_data
from preprocessing.solana import process_solana_data, process_solana_token_data

all_positions = []

for wallet in WALLETS:
    address = wallet['address']
    wallet_type = wallet['type']
    key = wallet.get('dydxv3_key')
    secret = wallet.get('dydxv3_secret')
    passphrase = wallet.get('dydxv3_phrase')

    if wallet_type == 'CIRCLE':
        positions_raw = fetch_circle_user_balance()
        positions = process_circle_data(positions_raw, wallet)

    elif wallet_type == 'GEMINI':
        spot_positions_raw = fetch_gemini_user_spot_balances()
        perps_positions_raw = fetch_gemini_user_perps_balances()
        positions = process_gemini_data(spot_positions_raw, wallet, 'spot') + process_gemini_data(perps_positions_raw, wallet, 'perps')

    elif wallet_type == 'DYDX':
        positions_raw = fetch_dydxv4_address_info(address)
        positions = process_dydxv4_data(positions_raw, wallet)

    elif wallet_type == 'RELAY':
        positions_raw = fetch_relayer_positions(address)
        positions = process_relayer_position_data(positions_raw, wallet)

    elif wallet_type == 'BTC':
        position_raw = fetch_blockcypher_user_balance(address, 'btc')
        positions = process_blockcypher_data(position_raw, wallet, 'BTC')

    elif wallet_type == 'DOGE':
        position_raw = fetch_blockcypher_user_balance(address, 'doge')
        positions = process_blockcypher_data(position_raw, wallet, 'DOGE')

    elif wallet_type == 'EVM':
        positions_tokens_raw = fetch_debank_user_balances_tokens(address)
        positions_protocols_raw = fetch_debank_user_balances_protocol(address)
        positions = process_evm_token_data(positions_tokens_raw, wallet) + process_evm_protocol_data(positions_protocols_raw, wallet)

        if pd.notna(key) and pd.notna(secret) and pd.notna(passphrase):
            dydxv3_balances = dydxClient(key, secret, passphrase, address).get_account_info()
            dydxv3_positions = process_dydxv3_data(dydxv3_balances, wallet)
            positions.extend(dydxv3_positions)

    elif wallet_type == 'SOL':
        print(wallet['address'])
        sol_balance_raw = fetch_solana_user_balance(address)
        sol_token_positions_raw = fetch_solana_user_token_balances(address)
        sol_positions = process_solana_data(wallet, sol_balance_raw)
        sol_token_positions = process_solana_token_data(wallet, sol_token_positions_raw, SOLANA_TOKENS)
        positions = sol_positions + sol_token_positions

    all_positions.extend(positions)

# Create DataFrame
positions_df = pd.DataFrame(all_positions)

# Fetch prices for rows where price is None (solana, btc, and doge)
symbols_to_fetch = positions_df[positions_df['price'].isnull()]['symbol'].unique()
prices = fetch_multiple_prices(symbols_to_fetch)
positions_df['price'] = positions_df.apply(lambda row: prices.get(row['symbol']) if pd.isna(row['price']) else row['price'], axis=1)

# Add value column and eliminate anything below $100
positions_df['value'] = positions_df['amount'] * positions_df['price']
positions_df = positions_df[positions_df['value'] >= 100]

# Add columns 'base_asset', 'sector', 'asset_type' from ASSETS_DICT
positions_df['base_asset'] = positions_df['symbol'].map(lambda x: ASSETS_DICT.get(x, {}).get('base_asset'))
positions_df['sector'] = positions_df['symbol'].map(lambda x: ASSETS_DICT.get(x, {}).get('sector'))
positions_df['asset_type'] = positions_df['symbol'].map(lambda x: ASSETS_DICT.get(x, {}).get('asset_type'))

# Add notional column
positions_df['notional'] = positions_df.apply(lambda row: abs(row['value']) if row['asset_type'] != 'STABLE' else 0, axis=1)

# Save DataFrame to Excel file
filename = 'positions_data.xlsx'
positions_df.to_excel(filename, index=False)