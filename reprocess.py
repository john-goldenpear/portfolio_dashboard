import pandas as pd
from config import ASSETS_DICT, POSITIONS_FILE_PATH, POSITIONS_DATABASE_FILE_PATH, POSITIONS_DICT
from typing import Dict, Any

def fill_missing_asset_info(df: pd.DataFrame, assets_dict: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    # Fill missing asset information
    df['base_asset'] = df['symbol'].map(lambda x: assets_dict.get(x, {}).get('base_asset', None))
    df['asset_type'] = df['symbol'].map(lambda x: assets_dict.get(x, {}).get('asset_type', None))
    df['sector'] = df['symbol'].map(lambda x: assets_dict.get(x, {}).get('sector', None))
    df['reward_type'] = df['symbol'].map(lambda x: assets_dict.get(x, {}).get('rewards', None))
    return df

def update_positions(df: pd.DataFrame, positions_list: list) -> pd.DataFrame:
    # Convert list to dictionary for easy lookup
    positions_dict = {entry['position_id']: entry for entry in positions_list}

    # Update positions based on the positions dictionary
    def update_position(row):
        pos_info = positions_dict.get(row['position_id'])
        if pos_info:
            row['position'] = pos_info.get('position', row['position'])
            row['position_type'] = pos_info.get('position_type', row.get('position_type'))
        return row

    return df.apply(update_position, axis=1)

def reprocess_positions():
    # Load positions and positions database
    positions_df = pd.read_excel(POSITIONS_FILE_PATH, index_col=0)
    positions_db_df = pd.read_excel(POSITIONS_DATABASE_FILE_PATH, index_col=0)

    # Fill missing asset information
    positions_df = fill_missing_asset_info(positions_df, ASSETS_DICT)
    positions_db_df = fill_missing_asset_info(positions_db_df, ASSETS_DICT)

    # Update positions
    positions_df = update_positions(positions_df, POSITIONS_DICT)
    positions_db_df = update_positions(positions_db_df, POSITIONS_DICT)

    # Save updated DataFrames back to Excel files
    positions_df.to_excel(POSITIONS_FILE_PATH, engine='openpyxl')
    positions_db_df.to_excel(POSITIONS_DATABASE_FILE_PATH, engine='openpyxl')

    print("Reprocessing complete. Updated positions and positions_db files.")

if __name__ == "__main__":
    reprocess_positions()
