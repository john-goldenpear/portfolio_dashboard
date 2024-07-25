import os
import pandas as pd
from dotenv import load_dotenv

# load environment variables once
load_dotenv()

# API Keys
DEBANK_API_KEY = os.getenv('DEBANK_API_KEY')
CIRCLE_API_KEY = os.getenv('CIRCLE_API_KEY')
GEMINI_SPOT_API_KEY = os.getenv('GEMINI_SPOT_API_KEY')
GEMINI_SPOT_API_SECRET = os.getenv('GEMINI_SPOT_API_SECRET')
GEMINI_PERPS_API_KEY = os.getenv('GEMINI_PERPS_API_KEY')
GEMINI_PERPS_API_SECRET = os.getenv('GEMINI_PERPS_API_SECRET')
OCTAV_BEARER_TOKEN = os.getenv('OCTAV_BEARER_TOKEN')

# Load wallets.xlsx into a dictionary
wallets_df = pd.read_excel('dicts/wallets.xlsx')
WALLETS = wallets_df.to_dict(orient='records')

# Specify solana tokens to track. Note will need to update this based on wwhat we are holding on sol... 
# Note this is needed because solana data processing requires finding sol token symbols and prices using coingecko api which is limited... can't check all dust etc. 
solana_tokens_df = pd.read_excel('dicts/solana_tokens.xlsx')
SOLANA_TOKENS = solana_tokens_df.to_dict(orient='records')

# Load the assets dictionary from the Excel file
assets_df = pd.read_excel('dicts/assets.xlsx')
ASSETS_DICT = assets_df.set_index('symbol').to_dict(orient='index')