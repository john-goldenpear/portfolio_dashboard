import pandas as pd
from binance.client import Client
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

def initialize_binance_client(api_key: str, api_secret: str) -> Client:
    """
    Initialize the Binance client with the provided API key and secret.

    Args:
        api_key (str): Your Binance API key.
        api_secret (str): Your Binance API secret.

    Returns:
        Client: An instance of the Binance client.
    """
    return Client(api_key=api_key, api_secret=api_secret)

def fetch_historical_data(symbol: str, client: Client, lookback_days: int) -> pd.Series:
    """
    Fetch historical daily price data for a cryptocurrency symbol from Binance.

    Args:
        symbol (str): The cryptocurrency symbol (e.g., 'BTC').
        client (Client): An instance of the Binance client.
        lookback_days (int): The number of days to look back for historical data.

    Returns:
        pd.Series: A pandas Series with dates as index and closing prices as values.
    """
    try:
        # Calculate the start date based on the lookback period
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        # Append 'USDT' to the symbol for Binance
        binance_symbol = f"{symbol}USDT"
        klines = client.get_historical_klines(binance_symbol, Client.KLINE_INTERVAL_1DAY, start_date)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['close'] = df['close'].astype(float)
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('date', inplace=True)
        return df['close']
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {e}")
        return pd.Series(dtype=float)

# Example usage
if __name__ == "__main__":
    from config import BINANCE_API_KEY, BINANCE_API_SECRET
    client = initialize_binance_client(BINANCE_API_KEY, BINANCE_API_SECRET)
    symbol = 'BTC'
    historical_prices = fetch_historical_data(symbol, client, 30)
    logging.info(f"Fetched historical prices for {symbol}: {historical_prices.head()}")
    print(historical_prices.index)
