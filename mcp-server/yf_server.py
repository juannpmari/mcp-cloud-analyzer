
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
# import pandas_ta as ta
import yfinance as yf
import pandas as pd
import requests
# Create an MCP server
mcp = FastMCP("Market analyzer")

@mcp.resource()
def search_stock_tickers(ticker_query: str = "") -> str:
    """Return up to 20 ticker names related to ticker_query. Use to retrieve tickers names for other resources.
    
    Parameters:
    ticker_query (str): e.g. 'AAPL' or 'GOOG', 'MSFT'
    
    Returns:
    dict: Dictionary with tickers as keys and their company names as values.
    """
    ticker_query = ticker_query.lower()
    url = "https://api.tickertick.com/tickers"
    params = {
        "p": f"{ticker_query}",
        "n": 20,
    }

    response = requests.get(url, params=params)
    data = response.json()

    return {item['ticker']:item['company_name'] for item in data['tickers']}

@mcp.resource()
def get_tickers_price(tickers: list[str]) -> Dict[str, float]:
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

@mcp.resource()
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

@mcp.resource()
def list_ticker_news(ticker: str, n_news: int = 10, hours_ago: int = 0) -> str:
    """ Returns n_news news about a ticker from the last hours_ago hours. Use to get context to predict ticker evolution.
    
    Parameters:
    ticker (str): e.g. 'AAPL' or 'GOOG', 'MSFT'
    n_news (int): number of news to return
    hours_ago (int): news are from up to hours_ago hours ago

    Returns:
    str: string with the last n_news news about the ticker
    """
    ticker = ticker.lower()
    url = "https://api.tickertick.com/feed"
    params = {
        "q": f"(and tt:{ticker} T:curated)",
        "n": n_news,
        "hours_ago": hours_ago
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

@mcp.prompt() #IDEA: podría devolver un prompt para summarizar las noticias de un ticker, o para armar un reporte semanal de ciertos tickers
def summarize_ticker_news(ticker: str, news: List[str] = []) -> str:
    """
    """
    return f"Given the following news about {ticker}: {news}, summarize them in a single paragraph."


# Run the server
if __name__ == "__main__":
    mcp.run(transport='sse')#, port=3001)