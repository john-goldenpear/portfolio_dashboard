import pandas as pd
import numpy as np
from config import BETA_LOOKBACK

def calculate_beta(asset_returns, btc_returns, window):
    """Calculate the rolling beta of an asset relative to Bitcoin."""
    covariance = asset_returns.rolling(window).cov(btc_returns)
    variance = btc_returns.rolling(window).var()
    beta = covariance / variance
    return beta

def add_beta_to_positions(positions_df, btc_data, fetch_historical_data_func):
    """Add the calculated beta to each position in the positions dataframe."""
    # Calculate daily and weekly returns for BTC
    btc_daily_returns = btc_data.pct_change().dropna()
    btc_weekly_returns = btc_data.resample('W').ffill().pct_change().dropna()

    betas_daily = {}
    betas_weekly = {}
    for base_asset in positions_df['base_asset'].unique():
        try:
            # Fetch historical data using the lookback period
            asset_data = fetch_historical_data_func(base_asset, BETA_LOOKBACK)

            # Calculate daily and weekly returns for the asset
            asset_daily_returns = asset_data.pct_change().dropna()
            asset_weekly_returns = asset_data.resample('W').ffill().pct_change().dropna()

            # Use the specified rolling window from config
            window_daily = min(len(asset_daily_returns), BETA_LOOKBACK)
            window_weekly = min(len(asset_weekly_returns), BETA_LOOKBACK)

            beta_daily = calculate_beta(asset_daily_returns, btc_daily_returns, window=window_daily)
            beta_weekly = calculate_beta(asset_weekly_returns, btc_weekly_returns, window=window_weekly)

            betas_daily[base_asset] = beta_daily.iloc[-1]  # Get the most recent beta
            betas_weekly[base_asset] = beta_weekly.iloc[-1]  # Get the most recent beta
        except Exception as e:
            print(f"Error fetching data for {base_asset}: {e}")
            betas_daily[base_asset] = np.nan
            betas_weekly[base_asset] = np.nan

    # Assign betas to the positions dataframe using .loc to avoid SettingWithCopyWarning
    positions_df.loc[:, 'beta_daily'] = positions_df['base_asset'].map(betas_daily)
    positions_df.loc[:, 'beta_weekly'] = positions_df['base_asset'].map(betas_weekly)

    # Set beta to 0 for stablecoin assets if their beta is NaN
    stablecoin_mask = (positions_df['asset_type'] == 'STABLE')
    positions_df.loc[stablecoin_mask, 'beta_daily'] = 0
    positions_df.loc[stablecoin_mask, 'beta_weekly'] = 0

    return positions_df

# Example usage in main.py
if __name__ == '__main__':
    from config import BINANCE_API_KEY, BINANCE_API_SECRET
    from binance.client import Client
    from src.utils.binance import fetch_historical_data as fetch_binance_data
    from src.utils.cryptocompare import fetch_historical_data as fetch_cryptocompare_data

    client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
    btc_data = fetch_binance_data('BTC', client, BETA_LOOKBACK)
    positions_df = pd.read_excel('output/positions.xlsx')
    positions_df = add_beta_to_positions(positions_df, btc_data, lambda symbol: fetch_binance_data(symbol, client, BETA_LOOKBACK))
    print(positions_df.head())

    btc_data = fetch_cryptocompare_data('BTC', limit=BETA_LOOKBACK)
    positions_df = pd.read_excel('output/positions.xlsx')
    positions_df = add_beta_to_positions(positions_df, btc_data, lambda symbol: fetch_cryptocompare_data(symbol, limit=BETA_LOOKBACK))
    print(positions_df.head())
