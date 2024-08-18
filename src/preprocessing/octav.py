import logging
from typing import Dict, Any, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_position(wallet: Dict[str, Any], chain: str, protocol: str, position_type: str, asset: Dict[str, Any], totalClosedPnl: float, totalOpenPnl: float) -> Dict[str, Union[str, float]]:
    """
    Create a position dictionary with the specified keys.

    Args:
        wallet (Dict[str, Any]): The wallet data dictionary.
        chain (str): The blockchain chain key.
        protocol (str): The protocol key.
        position_type (str): The type of position (e.g., 'LENDING', 'REWARDS').
        asset (Dict[str, Any]): The asset data dictionary.
        totalClosedPnl (float): The total closed PnL for the position.
        totalOpenPnl (float): The total open PnL for the position.

    Returns:
        Dict[str, Union[str, float]]: The structured position data.
    """
    symbol = asset['symbol']
    return {
        'wallet_id': wallet['id'],
        'wallet_address': wallet['address'],
        'wallet_type': wallet['type'],
        'strategy': wallet['strategy'],
        'contract_address': asset['contract'],
        'position_id': f"{wallet['id']}-{chain}-{protocol}-{position_type}-{symbol}",
        'chain': chain,
        'protocol': protocol,
        'type': position_type,
        'symbol': symbol,
        'amount': float(asset['balance']),
        'price': float(asset['price']),
        'cost_basis': float(asset['totalCostBasis']),
        'unrealized_gain': totalOpenPnl,
        'realized_gain': totalClosedPnl,
        'opened_qty': None,
        'closed_qty': None,
        'opened_price': None,
        'closed_price': None
    }

def preprocess_octav_portfolio(data: Dict[str, Any], wallet: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Preprocess the portfolio data to extract asset information by protocols.

    Args:
        data (Dict[str, Any]): The portfolio data dictionary.
        wallet (Dict[str, Any]): The wallet data dictionary.

    Returns:
        List[Dict[str, Any]]: The preprocessed data.
    """
    processed_data = []

    asset_by_protocols = data.get('data', {}).get('GetPortfoliosQuery', {}).get('assetByProtocols', {})
    
    for protocol_key, protocol_value in asset_by_protocols.items():
        protocol_name = protocol_value.get('name', protocol_key)
        chains = protocol_value.get('chains', {})
        
        for chain_key, chain_value in chains.items():
            protocol_positions = chain_value.get('protocolPositions', {})
            
            for position_type, position_data in protocol_positions.items():
                for sub_value in position_data.get('protocolPositions', []):
                    assets = sub_value.get('supplyAssets', []) + sub_value.get('borrowAssets', []) + sub_value.get('rewardAssets', []) + sub_value.get('dexAssets', [])
                    
                    for asset in assets:
                        position = create_position(
                            wallet,
                            chain_key,
                            protocol_name,
                            position_type.lower(),  # Using lower case for consistency
                            asset,
                            float(sub_value.get('totalClosedPnl', 0)),
                            float(sub_value.get('totalOpenPnl', 0))
                        )
                        processed_data.append(position)

    return processed_data

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    try:
        from apis.octav import fetch_octav_portfolio

        address = '0x3e8734ec146c981e3ed1f6b582d447dde701d90c'  # Replace with your actual address

        # Example wallet information
        wallet_info = {
            'id': 'example_wallet_id',
            'address': address,
            'type': 'example_wallet_type',
            'strategy': 'example_strategy'
        }

        # Fetch portfolio information
        portfolio_info = fetch_octav_portfolio(address)
        logging.info(f'Portfolio Information: {portfolio_info}')

        # Preprocess the portfolio information
        preprocessed_data = preprocess_octav_portfolio(portfolio_info, wallet_info)
        logging.info(f'Preprocessed Data: {preprocessed_data}')

    except Exception as e:
        logging.error(f"An error occurred during preprocessing: {e}")