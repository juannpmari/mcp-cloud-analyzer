
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
import pandas_ta as ta
import yfinance as yf
import pandas as pd
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
def get_technical_indicators(ticker, start='2024-01-01', end=None):
    """
    Fetches technical indicators for a ticker using yfinance and pandas_ta.

    Parameters:
    - ticker (str): e.g., 'AAPL' or 'BTC-USD'
    - start (str): start date in YYYY-MM-DD
    - end (str): end date in YYYY-MM-DD (optional)

    Returns:
    - DataFrame with indicators as columns (latest row only)
    """
    try:
        df = yf.download(ticker, start=start, end=end, interval='1d', progress=False)
        if df.empty:
            print("No data found.")
            return None

        # Add indicators
        df.ta.sma(length=20, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.bbands(append=True)

        # Return latest row with indicators
        indicators = df.iloc[-1][[
            'SMA_20', 'EMA_20', 'RSI_14',
            'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9',
            'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0'
        ]]

        return indicators.dropna().to_dict()
    
    except Exception as e:
        print(f"Error fetching indicators for {ticker}: {e}")
        return None

@mcp.tool()
def list_ticker_news(ticker: str, n_news: int = 10) -> str:
    ticker = ticker.lower()
    url = "https://api.tickertick.com/feed"
    params = {
        # "q": f"(diff tt:{ticker} s:reddit)",
        "q": f"(and tt:{ticker} T:curated)",
        "n": n_news,
        # "last": 6844326865886118959,
        # "hours_ago": 2400
    }

    response = requests.get(url, params=params)
    data = response.json()

    news=f"Last {n_news} news about {ticker}: \n"
    for item in data["stories"]:
        news += f" Title: {item['title']} \n"
        if 'description' in item:
            news += f" Description: {item['description']} \n"
        news += f" URL: {item['url']} \n"
        news += "--------------------------------\n"

    return news

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


# @mcp.prompt() #IDEA: podría devolver un prompt para summarizar las noticias de un ticker, o para armar un reporte semanal de ciertos tickers
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