
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
# Create an MCP server
mcp = FastMCP("Market analyzer")

@mcp.tool()
def list_ticker_names():
    pass #TODO

@mcp.tool()
def get_ticker_prices(tickers:List[str]) -> Dict[str, float]:
    """
    Get the latest price for a list of tickers using Yahoo Finance.

    Parameters:
    tickers (list): List of ticker symbols (e.g., ['AAPL', 'GOOG', 'MSFT'])

    Returns:
    dict: Dictionary with tickers as keys and their latest price as values.
    """
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            price = stock.info['regularMarketPrice']
            prices[ticker] = price
        except Exception as e:
            prices[ticker] = f"Error: {e}"
    return prices

@mcp.tool()
def get_historical_prices(ticker: str, start_date: str, end_date: str) -> List[tuple]:
    """
    Fetches daily closing prices for a given ticker between start_date and end_date.

    Parameters:
    - ticker (str): e.g. 'AAPL' or 'BTC-USD'
    - start_date (str): e.g. '2024-01-01'
    - end_date (str): e.g. '2024-06-01'

    Returns:
    - List of (date, closing_price) tuples
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
        if data.empty:
            return []

        # Reset index to turn Date from index to column
        data = data.reset_index()

        # Create the list of (date, close) tuples
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        return [(str(date.date()), close) for date, close in zip(dates, data['Close'][ticker])]

    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return []

@mcp.tool()
def list_ticker_news():
    pass

@mcp.tool()
def list_crypto_names():
    pass #TODO

@mcp.tool()
def get_crypto_prices(crypto_symbols:List[str]) -> Dict[str, float]:
    """
    Fetches current crypto prices from Yahoo Finance using yfinance.
    
    Parameters:
    crypto_symbols (list): List like ['BTC', 'ETH', 'DOGE']
    
    Returns:
    dict: { 'BTC': 66234.4, 'ETH': 3342.1, ... }
    """
    prices = {}
    for symbol in crypto_symbols:
        ticker = f"{symbol}-USD"
        try:
            price = yf.Ticker(ticker).fast_info['last_price']
            prices[symbol] = price
        except Exception as e:
            prices[symbol] = f"Error: {e}"
    return prices


# @mcp.prompt() #IDEA: podría devolver un prompt para summarizar las noticias de un ticker
# def optimize_guidelines(s3_guidelines:str) -> str:
#     """
#     """
#     return f""

# @mcp.resource("s3://{bucket}") #TODO: check if this is useful
# def s3_resource(bucket: str) -> str:
#     return get_s3_client()


# Run the server
if __name__ == "__main__":
    mcp.run(transport='sse', port=3001)