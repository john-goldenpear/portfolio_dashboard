import requests

def fetch_relayer_positions(wallet_address):
    """
    Fetch relayer positions for a given wallet address.

    Args:
        wallet_address (str): The wallet address to fetch relayer positions for.

    Returns:
        dict: The relayer positions data.
    """
    url = f"https://stats.mydefi.wtf/cache/wallet_{wallet_address}.json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Example usage
if __name__ == "__main__":
    wallet_address = '0x4a4e392290A382C9d2754E5Dca8581eA1893db5D'
    positions = fetch_relayer_positions(wallet_address)
    print(positions)


