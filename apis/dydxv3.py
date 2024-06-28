from dydx3 import Client
from dydx3.constants import API_HOST_MAINNET

class dydxClient:
    def __init__(self, api_key, api_secret, api_passphrase, ethereum_address):
        self.client = Client(
            host=API_HOST_MAINNET,
            api_key_credentials={
                'key': api_key,
                'secret': api_secret,
                'passphrase': api_passphrase,
            },
            default_ethereum_address=ethereum_address
        )

    def get_account_info(self):
        return self.client.private.get_account().data

    def get_open_orders(self):
        return self.client.private.get_orders().data

    def get_trade_history(self):
        return self.client.private.get_fills().data

    def get_transfers(self):
        return self.client.private.get_transfers().data

    def get_positions(self):
        return self.client.private.get_positions().data

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    from config import DYDXV3_API_KEY_2, DYDXV3_API_SECRET_2, DYDXV3_API_PASSPHRASE_2
    ETHEREUM_ADDRESS = '0xF9D0De258931D88E370245Ebf8b40119EC91912b'
    
    # Initialize the client
    client = dydxClient(
        api_key=DYDXV3_API_KEY_2,
        api_secret=DYDXV3_API_SECRET_2,
        api_passphrase=DYDXV3_API_PASSPHRASE_2,
        ethereum_address=ETHEREUM_ADDRESS
    )

    # Fetch and print dYdX account information
    account_info = client.get_account_info()
    print('Account Information:', account_info)

    # Fetch and print dYdX open orders
    open_orders = client.get_open_orders()
    print('Open Orders:', open_orders)

    # Fetch and print dYdX trade history
    trade_history = client.get_trade_history()
    print('Trade History:', trade_history)

    # Fetch and print dYdX transfers
    transfers = client.get_transfers()
    print('Transfers:', transfers)

    # Fetch and print dYdX positions
    positions = client.get_positions()
    print('Positions:', positions)
