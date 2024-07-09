from apis.relayer import fetch_relayer_positions

# Mapping of chain numbers to chain names
CHAIN_MAP = {
    '1': 'eth',
    '10': 'op',
    '137': 'polygon',
    '324': 'zk',
    '8453': 'base',
    '34443': 'mode',
    '42161': 'arb',
    '59144': 'linea'
}

def process_relayer_portfolio_data(relayer_data, wallet):
    """
    Process relayer portfolio data fetched from the Relayer API.

    Args:
        relayer_data (dict): Dictionary containing relayer data fetched from the API.
        wallet (dict): Dictionary containing wallet information (address, type, strategy).

    Returns:
        list: Processed relayer portfolio data with wallet information included.
    """
    processed_data = []

    

    # Extract portfolio data
    portfolio = relayer_data.get('portfolio', {})
    for asset, details in portfolio.items():
        processed_data.append({
            'wallet_address': wallet['address'],
            'wallet_type': wallet['type'],
            'strategy': wallet['strategy'],
            'position_id': f"across-relay-{asset}",
            'chain': 'N/A',
            'protocol_id': 'across-relay',
            'type': 'relay',
            'symbol': asset,
            'amount': details.get('balance', 0) / (10 ** 18),  # Divide by 10^18 for human-readable format
            'price': details.get('price', 0)
        })

    return processed_data

def process_relayer_position_data(relayer_data, wallet):
    """
    Process relayer position data fetched from the Relayer API.

    Args:
        relayer_data (dict): Dictionary containing relayer data fetched from the API.
        wallet (dict): Dictionary containing wallet information (address, type, strategy).

    Returns:
        list: Processed relayer position data with wallet information included.
    """
    processed_data = []

    protocol = 'across relay'
    position_type = 'hodl' if token == 'nativeToken' else 'relay'
    symbol = 'ETH' if token == 'nativeToken' else token

    # Extract positions data
    positions = relayer_data.get('positions', {})
    for chain_key, tokens in positions.items():
        chain_number = chain_key.replace('chain_', '')
        chain = CHAIN_MAP.get(str(chain_number), 'unknown')
        for token, details in tokens.items():
            processed_data.append({
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
                'amount': details.get('positionTotal', 0) / (10 ** 18),  # Divide by 10^18 for human-readable format
                'price': details.get('price', 0)
            })

    return processed_data

# Example usage
if __name__ == "__main__":
    wallet_list = [
        {'id': 'XXXX', 'address': '0x4a4e392290A382C9d2754E5Dca8581eA1893db5D', 'type': 'EVM', 'strategy': 'Quality'},
    ]

    for wallet in wallet_list:
        relayer_data = fetch_relayer_positions(wallet['address'])
        
        # Process portfolio-level data
        portfolio_data = process_relayer_portfolio_data(relayer_data, wallet)
        print("Portfolio Data:", portfolio_data)
        
        # Process position-level data
        position_data = process_relayer_position_data(relayer_data, wallet)
        print("Position Data:", position_data)