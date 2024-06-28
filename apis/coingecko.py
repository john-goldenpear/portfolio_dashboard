import requests

# Define constants locally within the module
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3'
COINGECKO_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

def fetch_data(endpoint: str, params: dict = None) -> dict:
    """
    Fetch data from the CoinGecko API.

    Args:
        endpoint (str): The API endpoint to request.
        params (dict, optional): Query parameters to include in the request.

    Returns:
        dict: The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request returns an unsuccessful status code.
    """
    url = f"{COINGECKO_API_URL}/{endpoint}"
    try:
        response = requests.get(url, headers=COINGECKO_HEADERS, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Response: {response.text}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def fetch_coingecko_token_info(token_address: str) -> dict:
    """
    Fetch all token information from CoinGecko API.

    Args:
        token_address (str): Token address.

    Returns:
        dict: The JSON response containing the token information.
    """
    endpoint = f'coins/solana/contract/{token_address}'
    try:
        return fetch_data(endpoint)
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching data for token {token_address}: {e}")
    except Exception as e:
        print(f"Unexpected error fetching data for token {token_address}: {e}")
    return None

def fetch_coingecko_token_symbol_and_price(token_address: str) -> dict:
    """
    Fetch token symbol and price from CoinGecko API using token info.

    Args:
        token_address (str): Token address.

    Returns:
        dict: Dictionary containing the token symbol and price.
    """
    token_info = fetch_coingecko_token_info(token_address)
    if token_info:
        try:
            symbol = token_info['symbol'].upper()
            price = token_info['market_data']['current_price']['usd']
            return {'symbol': symbol, 'price': price}
        except KeyError as e:
            print(f"Key error: {e} in response {token_info}")
    return None

def fetch_coingecko_price(coingecko_id: str) -> float:
    """
    Fetch the price of a token from CoinGecko using its ID.

    Args:
        coingecko_id (str): The CoinGecko ID of the token.

    Returns:
        float: The current price of the token in USD.
    """
    endpoint = f'coins/{coingecko_id}'
    try:
        token_info = fetch_data(endpoint)
        if token_info:
            return token_info['market_data']['current_price']['usd']
    except KeyError as e:
        print(f"Key error: {e} in response {token_info}")
    return None

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    token_addresses = ['So11111111111111111111111111111111111111112', '4k3Dyjzvzp8eGN8wxD3YdbJQH7qENNE6jn7W9VpujwJ4']
    token_symbols = ['bitcoin', 'ethereum']
    
    try:
        # Fetch and print token info from CoinGecko
        for address in token_addresses:
            token_symbol_and_price = fetch_coingecko_token_symbol_and_price(address)
            if token_symbol_and_price:
                print(f"Token Address: {address}")
                print(f"Symbol: {token_symbol_and_price['symbol']}")
                print(f"Price (USD): {token_symbol_and_price['price']}")
            else:
                print(f"Token information for {address} not found.")

        # Fetch and print token prices from CoinGecko
        for symbol in token_symbols:
            price = fetch_coingecko_price(symbol)
            if price is not None:
                print(f"The current price of {symbol.upper()} is ${price}")
            else:
                print(f"Price for {symbol.upper()} not found.")
    except Exception as e:
        print(f"An error occurred during the example usage: {e}")



