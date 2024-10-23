import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

# API Keys
DEBANK_API_KEY = os.getenv('DEBANK_API_KEY')
CIRCLE_API_KEY = os.getenv('CIRCLE_API_KEY')
GEMINI_SPOT_API_KEY = os.getenv('GEMINI_SPOT_API_KEY')
GEMINI_SPOT_API_SECRET = os.getenv('GEMINI_SPOT_API_SECRET')
GEMINI_PERPS_API_KEY = os.getenv('GEMINI_PERPS_API_KEY')
GEMINI_PERPS_API_SECRET = os.getenv('GEMINI_PERPS_API_SECRET')
OCTAV_BEARER_TOKEN = os.getenv('OCTAV_BEARER_TOKEN')
BLOCKCYPHER_TOKEN = os.getenv('BLOCKCYPHER_TOKEN')
MINTSCAN_API_KEY = os.getenv('MINTSCAN_API_KEY')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# Base path for the project
BASE_PATH = r'C:\Users\JohnRogic\OneDrive - Golden Pear\Shared Documents - GP Research Share Site\John\.Projects\.github\portfolio_dashboard'

# Load wallets.xlsx into a dictionary
wallets_df = pd.read_excel(os.path.join(BASE_PATH, 'dicts', 'wallets.xlsx'))
WALLETS = wallets_df.to_dict(orient='records')

# load manual positions (i.e. locked solana)
manual_positions_df = pd.read_excel(os.path.join(BASE_PATH, 'dicts', 'manual_positions.xlsx'))
MANUAL_POSITIONS = manual_positions_df.to_dict(orient='records')

# load custom positions (i.e. locked solana)
custom_positions_df = pd.read_excel(os.path.join(BASE_PATH, 'dicts', 'positions.xlsx'))
POSITIONS_DICT = custom_positions_df.to_dict(orient='records')

# Load the assets dictionary from the Excel file
assets_df = pd.read_excel(os.path.join(BASE_PATH, 'dicts', 'assets.xlsx'))
ASSETS_DICT = assets_df.set_index('symbol').to_dict(orient='index')

# File path constants
ASSET_DICT_FILE_PATH = os.path.join(BASE_PATH, 'dicts', 'assets.xlsx')

# Output file paths
LOG_FILE_PATH = os.path.join(BASE_PATH, 'output', 'logs.log')
POSITIONS_FILE_PATH = os.path.join(BASE_PATH, 'output', f'positions.xlsx')
TRANSACTIONS_FILE_PATH = os.path.join(BASE_PATH, 'output', f'transactions.xlsx')
POSITIONS_DATABASE_FILE_PATH = os.path.join(BASE_PATH, 'output', 'positions_db.xlsx')
TRANSACTIONS_DATABASE_FILE_PATH = os.path.join(BASE_PATH, 'output', 'transactions_db.xlsx')

# Beta calculation settings
BETA_LOOKBACK = 180  # Lookback period in days or weeks

