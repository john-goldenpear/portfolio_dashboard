import logging
import sys
import os
import azure.functions as func

# Add the parent directory of 'src' module to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the main function from src.main module
from src.main import main as portfolio_main

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function triggered to run portfolio_main.')

    try:
        # Call the main function from src/main.py
        portfolio_main()
        return func.HttpResponse("Portfolio dashboard script executed successfully.", status_code=200)
    
    except Exception as e:
        logging.error(f"Error executing portfolio_main: {e}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500) 

