import logging
from dydx3 import Client
from dydx3.constants import API_HOST_MAINNET
from typing import Dict, Any
from dydx3.errors import DydxApiError

# Configure logging
logging.basicConfig(level=logging.INFO)

class dydxClient:
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str, ethereum_address: str):
        """
        Initialize the dYdX client.

        Args:
            api_key (str): The API key.
            api_secret (str): The API secret.
            api_passphrase (str): The API passphrase.
            ethereum_address (str): The Ethereum address.
        """
        self.client = Client(
            host=API_HOST_MAINNET,
            api_key_credentials={
                'key': api_key,
                'secret': api_secret,
                'passphrase': api_passphrase,
            },
            default_ethereum_address=ethereum_address
        )

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information.

        Returns:
            Dict[str, Any]: The account information.
        """
        try:
            logging.info("Fetching account information.")
            return self.client.private.get_account().data
        except DydxApiError as e:
            logging.error(f"dYdX API error while fetching account info: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching account info: {e}")
            raise

    def get_open_orders(self) -> Dict[str, Any]:
        """
        Get open orders.

        Returns:
            Dict[str, Any]: The open orders.
        """
        logging.info("Fetching open orders.")
        return self.client.private.get_orders().data

    def get_trade_history(self) -> Dict[str, Any]:
        """
        Get trade history.

        Returns:
            Dict[str, Any]: The trade history.
        """
        logging.info("Fetching trade history.")
        return self.client.private.get_fills().data

    def get_transfers(self) -> Dict[str, Any]:
        """
        Get transfers.

        Returns:
            Dict[str, Any]: The transfers.
        """
        logging.info("Fetching transfers.")
        return self.client.private.get_transfers().data

    def get_positions(self) -> Dict[str, Any]:
        """
        Get positions.

        Returns:
            Dict[str, Any]: The positions.
        """
        logging.info("Fetching positions.")
        return self.client.private.get_positions().data

# Example usage (This section can be commented out or removed in production)
if __name__ == "__main__":
    from config import WALLETS
    wallet = WALLETS[4]
    key = wallet.get('dydxv3_key')
    secret = wallet.get('dydxv3_secret')
    passphrase = wallet.get('dydxv3_phrase')
    eth_address = wallet.get('address')
    
    # Initialize the client
    client = dydxClient(
        api_key=key,
        api_secret=secret,
        api_passphrase=passphrase,
        ethereum_address=eth_address
    )
    # Fetch and print dYdX account information
    try:
        account_info = client.get_account_info()
        logging.info(f'Account Information: {account_info}')
    except Exception as e:
        logging.error(f"Error fetching account information: {e}")

    # Fetch and print dYdX open orders
    try:
        open_orders = client.get_open_orders()
        logging.info(f'Open Orders: {open_orders}')
    except Exception as e:
        logging.error(f"Error fetching open orders: {e}")

    # Fetch and print dYdX trade history
    try:
        trade_history = client.get_trade_history()
        logging.info(f'Trade History: {trade_history}')
    except Exception as e:
        logging.error(f"Error fetching trade history: {e}")

    # Fetch and print dYdX transfers
    try:
        transfers = client.get_transfers()
        logging.info(f'Transfers: {transfers}')
    except Exception as e:
        logging.error(f"Error fetching transfers: {e}")

    # Fetch and print dYdX positions
    try:
        positions = client.get_positions()
        logging.info(f'Positions: {positions}')
    except Exception as e:
        logging.error(f"Error fetching positions: {e}")